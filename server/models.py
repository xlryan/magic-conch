"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Date, Index, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Entry(Base):
    """项目条目表"""
    __tablename__ = "entries"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    repo_url = Column(String, nullable=False)
    last_commit = Column(Date, nullable=False)
    summary = Column(String, nullable=False)
    tags = Column(String, nullable=True)  # 逗号分隔的标签

    def __repr__(self):
        return f"<Entry(id={self.id}, title={self.title})>"


class Vote(Base):
    """投票记录表"""
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(String, nullable=False, index=True)
    vote_date = Column(Date, nullable=False)
    ip_hash = Column(String, nullable=False)

    # 唯一约束：同一条目、同一天、同一 IP 只能投一次
    __table_args__ = (
        Index('idx_unique_vote', 'entry_id', 'vote_date', 'ip_hash', unique=True),
    )

    def __repr__(self):
        return f"<Vote(entry_id={self.entry_id}, date={self.vote_date})>"


def get_engine(db_path: str):
    """创建数据库引擎"""
    return create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})


def create_tables(engine):
    """创建所有表"""
    Base.metadata.create_all(bind=engine)


def get_session_factory(engine):
    """创建会话工厂"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
