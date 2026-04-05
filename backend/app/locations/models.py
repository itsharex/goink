"""
地点管理模块 - 数据库模型
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, JSON, Index, func
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.core.database import Base


class Location(Base):
    """地点模型 - 管理小说中的场景地点"""
    __tablename__ = "locations"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    novel_id: int = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name: str = Column(String(200), nullable=False, index=True)
    location_type: str = Column(String(50), nullable=False, index=True)  # city/town/forest/building/...
    description: Optional[str] = Column(Text)
    
    geo_info: Optional[Dict[str, Any]] = Column(JSON)
    
    related_characters: Optional[List[int]] = Column(JSON)
    related_chapters: Optional[List[int]] = Column(JSON)
    
    parent_location_id: Optional[int] = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"))
    
    tags: Optional[List[str]] = Column(JSON)
    
    first_appearance_chapter_id: Optional[int] = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"))
    extra_metadata: Optional[Dict[str, Any]] = Column(JSON)
    
    created_at: datetime = Column(TIMESTAMP, server_default=func.now())
    updated_at: datetime = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    novel = relationship("Novel")
    parent = relationship("Location", remote_side=[id], backref="children")
    first_appearance_chapter = relationship("Chapter")

    __table_args__ = (
        Index('idx_location_novel', 'novel_id'),
        Index('idx_location_novel_type', 'novel_id', 'location_type'),
        Index('idx_location_parent', 'parent_location_id'),
    )
