"""
Pydantic 数据模型
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class EntrySubmit(BaseModel):
    """用户提交条目模型"""
    title: str = Field(..., min_length=1, max_length=200, description="项目标题")
    owner: str = Field(..., min_length=1, max_length=100, description="项目所有者")
    repo_url: str = Field(..., description="仓库链接")
    last_commit: date = Field(..., description="最后提交日期")
    summary: str = Field(..., min_length=10, max_length=2000, description="项目描述")
    tags: Optional[List[str]] = Field(default=None, description="标签列表")


class EntryResponse(BaseModel):
    """条目响应模型"""
    id: str
    title: str
    owner: str
    repo_url: str
    last_commit: date
    summary: str
    tags: Optional[str] = None
    status: str = Field(description="审核状态: pending/approved/rejected")
    days_stale: int = Field(description="停更天数")
    votes: int = Field(description="踩一脚数")
    likes: int = Field(description="点赞数")
    score: int = Field(description="烂尾指数 0-100")
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EntryReview(BaseModel):
    """审核条目模型"""
    action: str = Field(..., pattern="^(approve|reject)$", description="审核动作")
    review_note: Optional[str] = Field(None, max_length=500, description="审核备注")


class VoteRequest(BaseModel):
    """踩一脚请求模型"""
    entry_id: str


class LikeRequest(BaseModel):
    """点赞请求模型"""
    entry_id: str


class APIResponse(BaseModel):
    """统一 API 响应格式"""
    ok: bool
    data: Optional[dict | list] = None
    error: Optional[str] = None
