"""
角色管理模块 - 数据库模型
"""
from sqlalchemy import Column, Integer, String, Text, JSON, TIMESTAMP, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.database import Base


class Character(Base):
    """角色模型 - 存储小说角色信息"""
    __tablename__ = "characters"
    
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    novel_id: int = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, index=True)
    name: str = Column(String(100), nullable=False, index=True)
    personality: Optional[Dict[str, Any]] = Column(JSON)
    relationships: Optional[Dict[str, List[int]]] = Column(JSON)
    abilities: Optional[List[str]] = Column(JSON)
    created_at: datetime = Column(TIMESTAMP, server_default=func.now())
    
    novel = relationship("Novel", back_populates="characters")
    
    __table_args__ = (
        Index('idx_character_novel_name', 'novel_id', 'name'),
    )


class CharacterRelation(Base):
    """人物关系 - 有向图边结构，支持关系演变追踪"""
    __tablename__ = "character_relations"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    novel_id: int = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, index=True)

    source_character_id: int = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    target_character_id: int = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)

    relationship_type: str = Column(String(50), nullable=False, index=True)
    description: Optional[str] = Column(Text)
    intensity: int = Column(Integer, default=3)
    status: str = Column(String(30), default="active")

    established_chapter_id: Optional[int] = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"))
    evolved_from_id: Optional[int] = Column(Integer, ForeignKey("character_relations.id", ondelete="SET NULL"))

    extra_metadata: Optional[Dict[str, Any]] = Column(JSON)

    created_at: datetime = Column(TIMESTAMP, server_default=func.now())
    updated_at: datetime = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    source = relationship("Character", foreign_keys=[source_character_id], backref="outgoing_relations")
    target = relationship("Character", foreign_keys=[target_character_id], backref="incoming_relations")
    evolved_from = relationship("CharacterRelation", remote_side=[id], backref="evolutions")

    __table_args__ = (
        Index('idx_relation_pair', 'source_character_id', 'target_character_id'),
        Index('idx_relation_novel_type', 'novel_id', 'relationship_type'),
        Index('idx_relation_target', 'target_character_id'),
    )
