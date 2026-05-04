"""
Agent任务持久化模型
"""
from sqlalchemy import String, Text, ForeignKey, JSON, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Any

from core.database import Base


class AgentTaskRecord(Base):
    """Agent任务记录 - 持久化任务状态"""
    __tablename__ = "agent_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    novel_id: Mapped[int] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id: Mapped[int | None] = mapped_column(ForeignKey("chapters.id", ondelete="SET NULL"))
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='pending', index=True)
    parameters: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    context: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    error: Mapped[str | None] = mapped_column(Text)
    agent_id: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(server_default=func.now(), onupdate=func.now())
    completed_at: Mapped[datetime | None] = mapped_column()

    __table_args__ = (
        Index('idx_agent_task_novel_status', 'novel_id', 'status'),
        Index('idx_agent_task_type_status', 'task_type', 'status'),
    )
