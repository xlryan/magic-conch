"""
FastAPI 主应用
"""
import hashlib
import hmac
import re
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import List
from slugify import slugify

from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from server.settings import settings
from server.models import (
    get_engine, create_tables, get_session_factory,
    Entry, Vote, Like, ApprovalStatus
)
from server.schema import (
    EntryResponse, EntrySubmit, EntryReview,
    VoteRequest, LikeRequest, APIResponse
)
from server.scoring import calculate_score

# 初始化数据库
engine = get_engine(settings.DB_URL)
create_tables(engine)
SessionLocal = get_session_factory(engine)

# 创建 FastAPI 应用
app = FastAPI(
    title="神奇海螺·烂尾博物馆",
    description="一个极简的烂尾项目展览馆，支持用户提交和管理员审核",
    version="2.0.0"
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


def hash_ip(ip: str, salt: str = "") -> str:
    """
    生成 IP 哈希（永久，用于点赞）

    Args:
        ip: IP 地址
        salt: 额外盐值

    Returns:
        SHA256 哈希值
    """
    raw = f"{ip}{settings.SECRET_KEY}{salt}"
    return hashlib.sha256(raw.encode()).hexdigest()


def hash_ip_daily(ip: str, today: date = None) -> str:
    """
    生成 IP 每日哈希（用于踩一脚）

    Args:
        ip: IP 地址
        today: 日期（默认今天）

    Returns:
        SHA256 哈希值
    """
    if today is None:
        today = date.today()
    return hash_ip(ip, salt=today.isoformat())


def generate_entry_id(title: str) -> str:
    """
    从标题生成唯一 ID

    Args:
        title: 项目标题

    Returns:
        唯一标识符
    """
    # 使用 slugify 生成 URL 友好的 ID
    base_id = slugify(title, max_length=50)
    # 添加时间戳确保唯一性
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{base_id}-{timestamp}"


# ==================== API 路由 ====================

@app.get("/api/entries", response_model=List[EntryResponse])
async def get_entries(
    include_pending: bool = False,
    db: Session = Depends(get_db)
):
    """
    获取所有条目，包含实时评分

    Args:
        include_pending: 是否包含待审核条目（需要管理员）
    """
    # 查询已批准的条目
    query = db.query(Entry).filter(Entry.status == ApprovalStatus.APPROVED)

    entries = query.all()
    result = []

    for entry in entries:
        # 统计投票数和点赞数
        vote_count = db.query(func.count(Vote.id)).filter(Vote.entry_id == entry.id).scalar()
        like_count = db.query(func.count(Like.id)).filter(Like.entry_id == entry.id).scalar()

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
            "status": entry.status.value,
            "days_stale": score_data['days_stale'],
            "votes": vote_count,
            "likes": like_count,
            "score": score_data['total_score'],
            "submitted_at": entry.submitted_at
        })

    # 按分数降序排序
    result.sort(key=lambda x: x['score'], reverse=True)

    return result


@app.post("/api/submit")
async def submit_entry(
    entry_data: EntrySubmit,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    用户提交新项目（待审核）
    """
    # 生成唯一 ID
    entry_id = generate_entry_id(entry_data.title)

    # 处理标签
    tags_str = ','.join(entry_data.tags) if entry_data.tags else None

    # 创建条目
    new_entry = Entry(
        id=entry_id,
        title=entry_data.title,
        owner=entry_data.owner,
        repo_url=entry_data.repo_url,
        last_commit=entry_data.last_commit,
        summary=entry_data.summary,
        tags=tags_str,
        status=ApprovalStatus.PENDING  # 默认待审核
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return {
        "ok": True,
        "data": {
            "id": new_entry.id,
            "status": "pending",
            "message": "提交成功，等待管理员审核后即可展示"
        }
    }


@app.post("/api/vote")
async def vote(
    vote_req: VoteRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    为条目投票（踩一脚，防刷：每个 IP 每天每条目最多 1 票）
    """
    # 检查条目是否存在且已批准
    entry = db.query(Entry).filter(
        Entry.id == vote_req.entry_id,
        Entry.status == ApprovalStatus.APPROVED
    ).first()

    if not entry:
        return JSONResponse(
            status_code=404,
            content={"ok": False, "error": "Entry not found or not approved"}
        )

    # 获取客户端 IP 并生成每日哈希
    client_ip = get_client_ip(request)
    today = date.today()
    ip_hash_value = hash_ip_daily(client_ip, today)

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


@app.post("/api/like")
async def like_entry(
    like_req: LikeRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    为条目点赞（每个 IP 每条目只能点赞一次）
    """
    # 检查条目是否存在且已批准
    entry = db.query(Entry).filter(
        Entry.id == like_req.entry_id,
        Entry.status == ApprovalStatus.APPROVED
    ).first()

    if not entry:
        return JSONResponse(
            status_code=404,
            content={"ok": False, "error": "Entry not found or not approved"}
        )

    # 获取客户端 IP 并生成哈希
    client_ip = get_client_ip(request)
    ip_hash_value = hash_ip(client_ip)

    # 检查是否已点赞
    existing_like = db.query(Like).filter(
        Like.entry_id == like_req.entry_id,
        Like.ip_hash == ip_hash_value
    ).first()

    if existing_like:
        # 已点赞，则取消点赞
        db.delete(existing_like)
        db.commit()
        action = "unliked"
    else:
        # 未点赞，则添加点赞
        new_like = Like(
            entry_id=like_req.entry_id,
            ip_hash=ip_hash_value
        )
        db.add(new_like)
        db.commit()
        action = "liked"

    # 获取最新点赞数
    like_count = db.query(func.count(Like.id)).filter(Like.entry_id == like_req.entry_id).scalar()

    return {
        "ok": True,
        "data": {
            "entry_id": like_req.entry_id,
            "action": action,
            "likes": like_count
        }
    }


@app.get("/api/admin/pending")
async def get_pending_entries(
    x_admin_token: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    获取待审核条目（管理员）
    """
    if x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token")

    pending_entries = db.query(Entry).filter(
        Entry.status == ApprovalStatus.PENDING
    ).order_by(Entry.submitted_at.desc()).all()

    result = []
    for entry in pending_entries:
        result.append({
            "id": entry.id,
            "title": entry.title,
            "owner": entry.owner,
            "repo_url": entry.repo_url,
            "last_commit": entry.last_commit,
            "summary": entry.summary,
            "tags": entry.tags,
            "status": entry.status.value,
            "submitted_at": entry.submitted_at
        })

    return {"ok": True, "data": result}


@app.post("/api/admin/review/{entry_id}")
async def review_entry(
    entry_id: str,
    review: EntryReview,
    x_admin_token: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    审核条目（管理员）
    """
    if x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token")

    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    # 更新审核状态
    if review.action == "approve":
        entry.status = ApprovalStatus.APPROVED
    elif review.action == "reject":
        entry.status = ApprovalStatus.REJECTED

    entry.reviewed_at = datetime.utcnow()
    entry.review_note = review.review_note

    db.commit()

    return {
        "ok": True,
        "data": {
            "entry_id": entry_id,
            "status": entry.status.value,
            "review_note": entry.review_note
        }
    }


@app.post("/api/reload")
async def reload_entries(
    x_admin_token: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    重新加载条目（需要管理员 Token）
    从 YAML 文件导入，自动设为已批准状态
    """
    if x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token")

    # 导入脚本逻辑
    import yaml

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
            # YAML 导入的条目自动批准
            if entry.status == ApprovalStatus.PENDING:
                entry.status = ApprovalStatus.APPROVED
        else:
            entry = Entry(
                id=data['id'],
                title=data['title'],
                owner=data['owner'],
                repo_url=data['repo_url'],
                last_commit=last_commit,
                summary=data['summary'],
                tags=tags_str,
                status=ApprovalStatus.APPROVED  # YAML 导入自动批准
            )
            db.add(entry)
        count += 1

    db.commit()

    return {"ok": True, "data": {"count": count}}


def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    """
    验证 GitHub Webhook 签名

    Args:
        payload_body: 原始请求体
        signature_header: X-Hub-Signature-256 头部值

    Returns:
        签名是否有效
    """
    if not settings.WEBHOOK_SECRET:
        # 如果未配置 secret，则跳过验证（不安全，仅用于测试）
        return True

    if not signature_header:
        return False

    # GitHub 使用 sha256=<hash> 格式
    hash_algorithm, signature = signature_header.split('=')
    if hash_algorithm != 'sha256':
        return False

    # 计算 HMAC
    mac = hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = mac.hexdigest()

    # 使用 constant time 比较防止时序攻击
    return hmac.compare_digest(expected_signature, signature)


@app.post("/api/webhook/deploy")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256")
):
    """
    GitHub Webhook 端点，用于自动部署

    接收 push 事件并执行部署脚本
    """
    # 获取原始请求体
    payload_body = await request.body()

    # 验证签名
    if not verify_github_signature(payload_body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # 解析 JSON
    import json
    try:
        payload = json.loads(payload_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # 检查是否是 push 到 main 分支
    ref = payload.get('ref', '')
    if ref != 'refs/heads/main':
        return {
            "ok": True,
            "message": f"Ignored: not main branch (ref={ref})"
        }

    # 执行部署脚本
    deploy_script = Path(__file__).parent.parent / "scripts" / "deploy.sh"

    if not deploy_script.exists():
        return {
            "ok": False,
            "error": "Deploy script not found"
        }

    try:
        # 异步执行部署脚本
        result = subprocess.run(
            ["bash", str(deploy_script)],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        return {
            "ok": True,
            "data": {
                "ref": ref,
                "commit": payload.get('after', '')[:7],
                "message": payload.get('head_commit', {}).get('message', ''),
                "deploy_output": result.stdout,
                "deploy_stderr": result.stderr,
                "return_code": result.returncode
            }
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": "Deployment timeout (>5 minutes)"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }


# ==================== 静态文件服务 ====================

# 确定静态文件目录（支持本地和 Docker）
PUBLIC_DIR = Path("/app/public") if Path("/app/public").exists() else Path("public")

# 挂载静态文件目录
app.mount("/assets", StaticFiles(directory=str(PUBLIC_DIR)), name="assets")


@app.get("/")
async def index():
    """返回前端页面"""
    return FileResponse(str(PUBLIC_DIR / "index.html"))


@app.get("/admin")
async def admin_page():
    """返回管理员页面"""
    admin_file = PUBLIC_DIR / "admin.html"
    if admin_file.exists():
        return FileResponse(str(admin_file))
    return JSONResponse(
        status_code=404,
        content={"error": "Admin page not found"}
    )


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "version": "2.0.0"}
