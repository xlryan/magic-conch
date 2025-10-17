"""
FastAPI 主应用
"""
import hashlib
from datetime import date
from pathlib import Path
from typing import List

from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from server.settings import settings
from server.models import get_engine, create_tables, get_session_factory, Entry, Vote
from server.schema import EntryResponse, VoteRequest, APIResponse
from server.scoring import calculate_score

# 初始化数据库
engine = get_engine(settings.DB_PATH)
create_tables(engine)
SessionLocal = get_session_factory(engine)

# 创建 FastAPI 应用
app = FastAPI(
    title="神奇海螺·烂尾博物馆",
    description="一个极简的烂尾项目展览馆",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 依赖：数据库会话
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_client_ip(request: Request) -> str:
    """获取客户端 IP 地址"""
    # 优先从 X-Forwarded-For 获取（取第一个 IP）
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    # 从 X-Real-IP 获取
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # 最后使用直连 IP
    return request.client.host


def hash_ip(ip: str, today: date = None) -> str:
    """
    生成 IP 哈希

    Args:
        ip: IP 地址
        today: 日期（默认今天）

    Returns:
        SHA256 哈希值
    """
    if today is None:
        today = date.today()

    # sha256(ip + SECRET_KEY + yyyy-mm-dd)
    raw = f"{ip}{settings.SECRET_KEY}{today.isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()


# ==================== API 路由 ====================

@app.get("/api/entries", response_model=List[EntryResponse])
async def get_entries(db: Session = Depends(get_db)):
    """
    获取所有条目，包含实时评分
    """
    entries = db.query(Entry).all()
    result = []

    for entry in entries:
        # 统计投票数
        vote_count = db.query(func.count(Vote.id)).filter(Vote.entry_id == entry.id).scalar()

        # 计算评分
        score_data = calculate_score(vote_count, entry.last_commit)

        result.append({
            "id": entry.id,
            "title": entry.title,
            "owner": entry.owner,
            "repo_url": entry.repo_url,
            "last_commit": entry.last_commit,
            "summary": entry.summary,
            "tags": entry.tags,
            "days_stale": score_data['days_stale'],
            "votes": vote_count,
            "score": score_data['total_score']
        })

    # 按分数降序排序
    result.sort(key=lambda x: x['score'], reverse=True)

    return result


@app.post("/api/vote")
async def vote(
    vote_req: VoteRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    为条目投票（防刷：每个 IP 每天每条目最多 1 票）
    """
    # 检查条目是否存在
    entry = db.query(Entry).filter(Entry.id == vote_req.entry_id).first()
    if not entry:
        return JSONResponse(
            status_code=404,
            content={"ok": False, "error": "Entry not found"}
        )

    # 获取客户端 IP 并生成哈希
    client_ip = get_client_ip(request)
    today = date.today()
    ip_hash_value = hash_ip(client_ip, today)

    # 检查今天是否已投票
    existing_vote = db.query(Vote).filter(
        Vote.entry_id == vote_req.entry_id,
        Vote.vote_date == today,
        Vote.ip_hash == ip_hash_value
    ).first()

    if existing_vote:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": "Already voted today"}
        )

    # 创建投票记录
    new_vote = Vote(
        entry_id=vote_req.entry_id,
        vote_date=today,
        ip_hash=ip_hash_value
    )
    db.add(new_vote)
    db.commit()

    # 重新计算分数
    vote_count = db.query(func.count(Vote.id)).filter(Vote.entry_id == vote_req.entry_id).scalar()
    score_data = calculate_score(vote_count, entry.last_commit)

    return {
        "ok": True,
        "data": {
            "entry_id": vote_req.entry_id,
            "votes": vote_count,
            "score": score_data['total_score']
        }
    }


@app.post("/api/reload")
async def reload_entries(
    x_admin_token: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    重新加载条目（需要管理员 Token）
    """
    if x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token")

    # 导入脚本逻辑
    import yaml
    from datetime import datetime

    # 确定数据目录（支持本地和 Docker）
    data_dir = Path("/app/data/entries") if Path("/app/data/entries").exists() else Path("data/entries")
    if not data_dir.exists():
        return {"ok": False, "error": "Data directory not found"}

    count = 0
    for yaml_file in data_dir.glob("*.yml"):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # 处理日期
        if isinstance(data.get('last_commit'), str):
            last_commit = datetime.strptime(data['last_commit'], '%Y-%m-%d').date()
        else:
            last_commit = data.get('last_commit')

        # 处理标签
        tags_str = ','.join(data.get('tags', [])) if data.get('tags') else None

        # Upsert
        entry = db.query(Entry).filter(Entry.id == data['id']).first()
        if entry:
            entry.title = data['title']
            entry.owner = data['owner']
            entry.repo_url = data['repo_url']
            entry.last_commit = last_commit
            entry.summary = data['summary']
            entry.tags = tags_str
        else:
            entry = Entry(
                id=data['id'],
                title=data['title'],
                owner=data['owner'],
                repo_url=data['repo_url'],
                last_commit=last_commit,
                summary=data['summary'],
                tags=tags_str
            )
            db.add(entry)
        count += 1

    db.commit()

    return {"ok": True, "data": {"count": count}}


# ==================== 静态文件服务 ====================

# 确定静态文件目录（支持本地和 Docker）
PUBLIC_DIR = Path("/app/public") if Path("/app/public").exists() else Path("public")

# 挂载静态文件目录
app.mount("/assets", StaticFiles(directory=str(PUBLIC_DIR)), name="assets")


@app.get("/")
async def index():
    """返回前端页面"""
    return FileResponse(str(PUBLIC_DIR / "index.html"))


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}
