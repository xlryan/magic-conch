"""
Pydantic 数据模型
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class EntryResponse(BaseModel):
    """条目响应模型"""
    id: str
    title: str
    owner: str
    repo_url: str
    last_commit: date
    summary: str
    tags: Optional[str] = None
    days_stale: int = Field(description="停更天数")
    votes: int = Field(description="投票数")
    score: int = Field(description="烂尾指数 0-100")

    class Config:
        from_attributes = True


class VoteRequest(BaseModel):
    """投票请求模型"""
    entry_id: str


class APIResponse(BaseModel):
    """统一 API 响应格式"""
    ok: bool
    data: Optional[dict | list] = None
    error: Optional[str] = None
