"""
故事时间线模块 - Pydantic验证模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class TimelineEntryCategory(str, Enum):
    FORESHADOWING = "foreshadowing"
    PLOT_NODE = "plot_node"
    CHAPTER_PLAN = "chapter_plan"
    USER_DIRECTIVE = "user_directive"


class TimelineEntryStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    RESOLVED = "resolved"
    ABANDONED = "abandoned"
    DEFERRED = "deferred"


class TimeHorizon(str, Enum):
    NEXT = "next"
    NEAR_TERM = "near_term"
    LONG_TERM = "long_term"
    UNDEFINED = "undefined"


class TimelineEntryCreate(BaseModel):
    """创建时间线条目请求"""
    category: TimelineEntryCategory = Field(..., description="条目分类")
    title: str = Field(..., min_length=1, max_length=255, description="标题")
    description: Optional[str] = Field(None, description="描述")
    detail_json: Optional[Dict[str, Any]] = Field(None, description="结构化详情（因category而异）")
    target_chapter: Optional[int] = Field(None, description="目标章节号")
    time_horizon: Optional[TimeHorizon] = Field(None, description="时间范围：next/near_term/long_term")
    importance: int = Field(default=3, ge=1, le=5, description="重要程度1-5")
    source: str = Field(default="ai", description="来源：ai_generated/user_created/user_edited")
    source_chapter_id: Optional[int] = Field(None, description="来源章节ID")
    related_entry_ids: Optional[List[int]] = Field(None, description="关联条目ID列表")
    tags: Optional[List[str]] = Field(None, description="标签列表")


class TimelineEntryUpdate(BaseModel):
    """更新时间线条目请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    detail_json: Optional[Dict[str, Any]] = None
    target_chapter: Optional[int] = None
    time_horizon: Optional[TimeHorizon] = None
    status: Optional[TimelineEntryStatus] = None
    importance: Optional[int] = Field(None, ge=1, le=5)
    related_entry_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None


class TimelineEntryResolve(BaseModel):
    """解决/完成时间线条目请求"""
    resolved_chapter_id: Optional[int] = Field(None, description="解决时关联的章节ID（可选）")
    resolution_notes: Optional[str] = Field(None, description="解决说明")


class TimelineEntryResponse(BaseModel):
    """时间线条目响应"""
    id: int
    novel_id: int
    category: str
    status: str
    title: str
    description: Optional[str]
    detail_json: Optional[Dict[str, Any]]
    target_chapter: Optional[int]
    time_horizon: Optional[str]
    importance: int
    source: str
    source_chapter_id: Optional[int]
    resolved_chapter_id: Optional[int]
    related_entry_ids: Optional[List[int]]
    tags: Optional[List[str]]
    version: int
    last_editor: Optional[str]
    original_ai_output: Optional[Dict[str, Any]]
    extra_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


class TimelineListResponse(BaseModel):
    """时间线列表响应"""
    items: List[TimelineEntryResponse]
    total: int
    page: int
    page_size: int


class TimelineContextRequest(BaseModel):
    """获取AI上下文用精简时间线的请求"""
    current_chapter: int = Field(..., description="当前章节号")
    max_entries: int = Field(default=15, ge=1, le=50, description="最大返回条数")
    include_categories: Optional[List[TimelineEntryCategory]] = Field(
        None, description="包含的分类，为空则全部包含"
    )
    include_statuses: Optional[List[TimelineEntryStatus]] = Field(
        None, description="包含的状态，默认为 pending+active+unresolved"
    )


class TimelineContextResponse(BaseModel):
    """AI上下文用精简时间线响应"""
    entries: List[TimelineEntryResponse]
    total_available: int
    truncated: bool
    summary: Optional[str] = Field(None, description="时间线摘要文本")
