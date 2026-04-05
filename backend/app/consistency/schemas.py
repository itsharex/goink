"""
一致性检查 - Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class SeverityLevel(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"


class IssueType(str, Enum):
    character = "character"
    plot = "plot"
    timeline = "timeline"
    foreshadowing = "foreshadowing"
    unknown = "unknown"


class ConsistencyIssue(BaseModel):
    """一致性问题"""
    issue_type: str = Field(..., description="问题类型")
    severity: str = Field(default="info", description="严重程度")
    chapter_id: Optional[int] = Field(None, description="章节ID")
    chapter_number: Optional[int] = Field(None, description="章节号")
    description: str = Field(..., description="问题描述")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    suggestion: Optional[str] = Field(None, description="修改建议")

    class Config:
        from_attributes = True


class ConsistencyCheckRequest(BaseModel):
    """一致性检查请求"""
    chapter_ids: Optional[List[int]] = Field(None, description="指定检查的章节ID列表")
    check_types: Optional[List[str]] = Field(
        default=None,
        description="检查类型列表 [character, plot, timeline, foreshadowing]"
    )
