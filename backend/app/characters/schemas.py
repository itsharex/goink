"""
角色管理模块 - Pydantic Schemas
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CharacterBase(BaseModel):
    name: str
    personality: Optional[Dict[str, Any]] = None
    relationships: Optional[Dict[str, str]] = None
    abilities: Optional[List[str]] = None


class CharacterCreate(CharacterBase):
    novel_id: int


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    personality: Optional[Dict[str, Any]] = None
    relationships: Optional[Dict[str, str]] = None
    abilities: Optional[List[str]] = None


class CharacterResponse(CharacterBase):
    id: int
    novel_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class RelationStatus(str, Enum):
    ACTIVE = "active"
    DORMANT = "dormant"
    RESOLVED = "resolved"
    SEVERED = "severed"


class RelationType(str, Enum):
    ALLY = "ally"
    ENEMY = "enemy"
    LOVER = "lover"
    FAMILY = "family"
    MENTOR = "mentor"
    STUDENT = "student"
    RIVAL = "rival"
    ACQUAINTANCE = "acquaintance"
    STRANGER = "stranger"
    COLLEAGUE = "colleague"
    SUBORDINATE = "subordinate"
    SUPERIOR = "superior"
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    SPOUSE = "spouse"
    EX_LOVER = "ex_lover"
    OTHER = "other"


class CharacterRelationBase(BaseModel):
    relationship_type: RelationType
    description: Optional[str] = None
    intensity: int = Field(default=3, ge=1, le=5)
    status: RelationStatus = RelationStatus.ACTIVE


class CharacterRelationCreate(CharacterRelationBase):
    source_character_id: int
    target_character_id: int
    established_chapter_id: Optional[int] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class CharacterRelationUpdate(BaseModel):
    relationship_type: Optional[RelationType] = None
    description: Optional[str] = None
    intensity: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[RelationStatus] = None
    established_chapter_id: Optional[int] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class CharacterRelationEvolve(BaseModel):
    """关系演变请求 - 创建新的关系记录并链接到旧记录"""
    relationship_type: RelationType
    description: Optional[str] = None
    intensity: int = Field(default=3, ge=1, le=5)
    status: RelationStatus = RelationStatus.ACTIVE
    evolution_notes: Optional[str] = Field(None, description="演变原因说明")
    established_chapter_id: Optional[int] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class CharacterRelationResponse(CharacterRelationBase):
    id: int
    novel_id: int
    source_character_id: int
    target_character_id: int
    established_chapter_id: Optional[int] = None
    evolved_from_id: Optional[int] = None
    extra_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    source_name: Optional[str] = None
    target_name: Optional[str] = None
    evolved_from_type: Optional[str] = None

    class Config:
        from_attributes = True


class CharacterNetworkResponse(BaseModel):
    """人物关系图响应"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    total_nodes: int
    total_edges: int
