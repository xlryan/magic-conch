"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, Index, create_engine, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

Base = declarative_base()


class ApprovalStatus(enum.Enum):
    """审核状态"""
    PENDING = "pending"      # 待审核
    APPROVED = "approved"    # 已批准
    REJECTED = "rejected"    # 已拒绝


class Entry(Base):
    """项目条目表"""
    __tablename__ = "entries"

    id = Column(String(100), primary_key=True)
    title = Column(String(200), nullable=False)
    owner = Column(String(100), nullable=False)
    repo_url = Column(String(500), nullable=False)
    last_commit = Column(Date, nullable=False)
    summary = Column(Text, nullable=False)
    tags = Column(String(200), nullable=True)  # 逗号分隔的标签

    # 审核相关
    status = Column(Enum(ApprovalStatus, name='approval_status', create_constraint=True, native_enum=True),
                    default=ApprovalStatus.PENDING, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    review_note = Column(Text, nullable=True)  # 审核备注

    def __repr__(self):
        return f"<Entry(id={self.id}, title={self.title}, status={self.status.value})>"


class Vote(Base):
    """投票记录表（踩一脚）"""
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(String(100), nullable=False, index=True)
    vote_date = Column(Date, nullable=False)
    ip_hash = Column(String(64), nullable=False)

    # 唯一约束：同一条目、同一天、同一 IP 只能投一次
    __table_args__ = (
        Index('idx_unique_vote', 'entry_id', 'vote_date', 'ip_hash', unique=True),
    )

    def __repr__(self):
        return f"<Vote(entry_id={self.entry_id}, date={self.vote_date})>"


class Like(Base):
    """点赞记录表"""
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(String(100), nullable=False, index=True)
    ip_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 唯一约束：同一条目、同一 IP 只能点赞一次
    __table_args__ = (
        Index('idx_unique_like', 'entry_id', 'ip_hash', unique=True),
    )

    def __repr__(self):
        return f"<Like(entry_id={self.entry_id})>"


def get_engine(db_url: str):
    """创建数据库引擎"""
    if db_url.startswith("sqlite"):
        return create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        return create_engine(db_url, pool_pre_ping=True, pool_recycle=3600)


def create_tables(engine):
    """创建所有表"""
    Base.metadata.create_all(bind=engine)


def get_session_factory(engine):
    """创建会话工厂"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
