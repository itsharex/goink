"""
故事时间线模块 - 数据库模型
TimelineEntry: 统一的时间线条目，替代分散的 Foreshadowing 系统
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, JSON, Index, func
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any, List
import enum

from app.core.database import Base


class TimelineEntryCategory(str, enum.Enum):
    FORESHADOWING = "foreshadowing"
    PLOT_NODE = "plot_node"
    CHAPTER_PLAN = "chapter_plan"
    USER_DIRECTIVE = "user_directive"


class TimelineEntryStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    RESOLVED = "resolved"
    ABANDONED = "abandoned"
    DEFERRED = "deferred"


class TimeHorizon(str, enum.Enum):
    NEXT = "next"
    NEAR_TERM = "near_term"
    LONG_TERM = "long_term"
    UNDEFINED = "undefined"


class TimelineEntry(Base):
    __tablename__ = "timeline_entries"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    novel_id: int = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, index=True)

    category: str = Column(String(50), nullable=False, index=True)
    status: str = Column(String(50), default=TimelineEntryStatus.PENDING.value, index=True)

    title: str = Column(String(255), nullable=False)
    description: Optional[str] = Column(Text)
    detail_json: Optional[Dict[str, Any]] = Column(JSON)

    target_chapter: Optional[int] = Column(Integer, index=True)
    time_horizon: Optional[str] = Column(String(20))

    importance: int = Column(Integer, default=3)
    source: str = Column(String(50), default="ai")
    source_chapter_id: Optional[int] = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"))

    resolved_chapter_id: Optional[int] = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"))
    related_entry_ids: Optional[List[int]] = Column(JSON)
    tags: Optional[List[str]] = Column(JSON)

    version: int = Column(Integer, default=1)
    last_editor: Optional[str] = Column(String(50))
    original_ai_output: Optional[Dict[str, Any]] = Column(JSON)

    extra_metadata: Optional[Dict[str, Any]] = Column(JSON)

    created_at: datetime = Column(TIMESTAMP, server_default=func.now())
    updated_at: datetime = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    resolved_at: Optional[datetime] = Column(TIMESTAMP)

    novel = relationship("Novel", back_populates="timeline_entries")
    source_chapter = relationship("Chapter", foreign_keys=[source_chapter_id])
    resolved_chapter = relationship("Chapter", foreign_keys=[resolved_chapter_id])

    __table_args__ = (
        Index('idx_timeline_novel_category', 'novel_id', 'category'),
        Index('idx_timeline_novel_status', 'novel_id', 'status'),
        Index('idx_timeline_novel_chapter', 'novel_id', 'target_chapter'),
        Index('idx_timeline_horizon', 'time_horizon'),
    )
