"""
地点管理模块 - Pydantic验证模型
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class LocationType(str, Enum):
    CITY = "city"
    TOWN = "town"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    BUILDING = "building"
    ROOM = "room"
    SEA = "sea"
    RIVER = "river"
    ROAD = "road"
    CASTLE = "castle"
    TEMPLE = "temple"
    VILLAGE = "village"
    DUNGEON = "dungeon"
    PALACE = "palace"
    MARKET = "market"
    INN = "inn"
    OTHER = "other"


class LocationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    location_type: LocationType = Field(default=LocationType.OTHER)
    description: Optional[str] = None
    geo_info: Optional[Dict[str, Any]] = None
    related_characters: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    parent_location_id: Optional[int] = None
    first_appearance_chapter_id: Optional[int] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    location_type: Optional[LocationType] = None
    description: Optional[str] = None
    geo_info: Optional[Dict[str, Any]] = None
    related_characters: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    parent_location_id: Optional[int] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class LocationResponse(LocationBase):
    id: int
    novel_id: int
    related_chapters: Optional[List[int]] = None
    parent_name: Optional[str] = None
    children_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LocationNetworkResponse(BaseModel):
    """地点网络响应（层级结构）"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    total_nodes: int
    root_locations: List[Dict[str, Any]]
