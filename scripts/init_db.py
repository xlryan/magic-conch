#!/usr/bin/env python3
"""
数据库初始化脚本
- 自动创建所有表结构
- 支持 SQLite 和 PostgreSQL
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.models import Base, get_engine
from server.settings import settings


def init_database():
    """初始化数据库，创建所有表"""
    print(f"🔧 正在初始化数据库: {settings.DB_URL}")

    try:
        # 获取数据库引擎
        engine = get_engine(settings.DB_URL)

        # 创建所有表
        Base.metadata.create_all(bind=engine)

        print("✅ 数据库初始化成功！")
        print(f"📊 已创建表: {', '.join(Base.metadata.tables.keys())}")

        return True

    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
