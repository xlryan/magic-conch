#!/usr/bin/env python3
"""
导入 YAML 条目到数据库
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import yaml

# 添加 server 模块到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.models import get_engine, create_tables, get_session_factory, Entry
from server.settings import settings


def import_entries():
    """从 YAML 文件导入条目"""
    # 初始化数据库
    print(f"🗄️  数据库路径: {settings.DB_PATH}")

    # 确保数据库目录存在
    db_dir = Path(settings.DB_PATH).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    engine = get_engine(settings.DB_PATH)
    create_tables(engine)
    SessionLocal = get_session_factory(engine)
    db = SessionLocal()

    # 查找 YAML 文件
    data_dir = Path("/app/data/entries") if Path("/app/data/entries").exists() else Path("data/entries")

    if not data_dir.exists():
        print(f"❌ 数据目录不存在: {data_dir}")
        return

    yaml_files = list(data_dir.glob("*.yml")) + list(data_dir.glob("*.yaml"))

    if not yaml_files:
        print(f"⚠️  未找到 YAML 文件: {data_dir}")
        return

    print(f"📂 发现 {len(yaml_files)} 个 YAML 文件")

    count_new = 0
    count_updated = 0

    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not data:
                print(f"⚠️  跳过空文件: {yaml_file.name}")
                continue

            # 必填字段检查
            required_fields = ['id', 'title', 'owner', 'repo_url', 'summary']
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                print(f"❌ {yaml_file.name} 缺少字段: {', '.join(missing_fields)}")
                continue

            # 处理日期
            if 'last_commit' in data:
                if isinstance(data['last_commit'], str):
                    last_commit = datetime.strptime(data['last_commit'], '%Y-%m-%d').date()
                else:
                    last_commit = data['last_commit']
            else:
                # 默认 30 天前
                last_commit = (datetime.now() - timedelta(days=30)).date()
                print(f"⚠️  {yaml_file.name} 未指定 last_commit，使用默认值: {last_commit}")

            # 处理标签
            tags_str = ','.join(data.get('tags', [])) if data.get('tags') else None

            # 检查是否已存在
            entry = db.query(Entry).filter(Entry.id == data['id']).first()

            if entry:
                # 更新现有条目
                entry.title = data['title']
                entry.owner = data['owner']
                entry.repo_url = data['repo_url']
                entry.last_commit = last_commit
                entry.summary = data['summary']
                entry.tags = tags_str
                count_updated += 1
                print(f"🔄 更新: {data['id']}")
            else:
                # 创建新条目
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
                count_new += 1
                print(f"✅ 新增: {data['id']}")

        except Exception as e:
            print(f"❌ 处理文件 {yaml_file.name} 失败: {e}")
            continue

    # 提交事务
    try:
        db.commit()
        print(f"\n✨ 导入完成！新增 {count_new} 条，更新 {count_updated} 条")
    except Exception as e:
        db.rollback()
        print(f"❌ 提交失败: {e}")
    finally:
        db.close()


if __name__ == '__main__':
    import_entries()
