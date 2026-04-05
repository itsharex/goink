"""
地点管理MCP工具
"""
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base import BaseMCPTool, MCPToolResult, MCPToolCategory

from app.novels.models import Novel


class GetLocationListTool(BaseMCPTool):
    """获取地点列表"""

    name = "get_location_list"
    description = (
        "获取当前小说的地点列表。无需传novel_id，系统会注入当前小说ID。"
        "\n返回所有已创建的地点，包含名称、类型、描述等信息。"
        "\n适用场景：了解故事中的地点布局、确认某个地点是否存在、规划新章节的场景时。"
        "\n支持按类型筛选（city/forest/building等）和关键词搜索。"
    )
    category = MCPToolCategory.NOVEL_MANAGEMENT
    parameters_schema = {
        "type": "object",
        "properties": {
            "location_type": {
                "type": "string",
                "enum": ["city", "town", "forest", "mountain", "building", "room",
                         "sea", "river", "road", "castle", "temple", "village",
                         "dungeon", "palace", "market", "inn", "other"],
                "description": "按类型筛选（可选）"
            },
            "search": {"type": "string", "description": "按名称或描述搜索（可选）"},
        },
        "required": []
    }

    async def execute(self, db, novel_id: int=0, location_type: Optional[str]=None,
                     search: Optional[str]=None, user_id=None, **kwargs) -> MCPToolResult:
        try:
            from app.locations.service import LocationService
            svc = LocationService(db, novel_id)
            
            if search:
                locations = await svc.search(search)
            elif location_type:
                locations = await svc.get_by_type(location_type)
            else:
                locations = await svc.get_all()
            
            return MCPToolResult(
                success=True,
                data={
                    "locations": [
                        {"id": l.id, "name": l.name, "type": l.location_type,
                         "description": l.description[:100] if l.description else None,
                         "tags": l.tags}
                        for l in locations
                    ],
                    "total": len(locations),
                    "types": list(set(l.location_type for l in locations)),
                },
                metadata={"tool": self.name, "novel_id": novel_id}
            )
        except Exception as e:
            return MCPToolResult(success=False, error=f"获取地点列表失败: {str(e)}")


class GetLocationDetailTool(BaseMCPTool):
    """获取地点详情"""

    name = "get_location_detail"
    description = (
        "获取指定地点的详细信息。无需传novel_id，系统会注入当前小说ID。"
        "\n返回完整信息：名称、类型、描述、地理信息、关联角色、关联章节、子地点等。"
        "\n适用场景：需要深入了解某个地点的详细设定、写某地点发生的戏份前调用。"
    )
    category = MCPToolCategory.NOVEL_MANAGEMENT
    parameters_schema = {
        "type": "object",
        "properties": {
            "location_id": {"type": "integer", "description": "地点ID（必填）"},
        },
        "required": ["location_id"]
    }

    async def execute(self, db, novel_id: int=0, location_id: int=0,
                     user_id=None, **kwargs) -> MCPToolResult:
        try:
            from app.locations.service import LocationService
            svc = LocationService(db, novel_id)
            location = await svc.get_by_id(location_id)
            
            if not location:
                return MCPToolResult(success=False, error=f"地点 {location_id} 不存在")
            
            parent_name = None
            children = []
            if location.parent_location_id:
                parent = await svc.get_by_id(location.parent_location_id)
                if parent:
                    parent_name = parent.name
            
            all_locs = await svc.get_all()
            children = [{"id": c.id, "name": c.name, "type": c.location_type}
                       for c in all_locs if c.parent_location_id == location_id]
            
            return MCPToolResult(
                success=True,
                data={
                    "id": location.id,
                    "name": location.name,
                    "type": location.location_type,
                    "description": location.description,
                    "geo_info": location.geo_info,
                    "related_characters": location.related_characters,
                    "related_chapters": location.related_chapters,
                    "tags": location.tags,
                    "parent_name": parent_name,
                    "children": children,
                    "children_count": len(children),
                },
                metadata={"tool": self.name, "novel_id": novel_id, "location_id": location_id}
            )
        except Exception as e:
            return MCPToolResult(success=False, error=f"获取地点详情失败: {str(e)}")


class CreateLocationTool(BaseMCPTool):
    """创建新地点"""

    name = "create_location"
    description = (
        "为当前小说创建一个新地点。无需传novel_id，系统会注入当前小说ID。"
        "\n适用场景：用户要求添加新地点、AI写作时发现需要新的场景设定、规划世界观时。"
        "\nname 为必填；location_type 建议从 city/town/forest/building 等中选择。"
        "\n创建后可通过 get_location_detail 查看详情。"
    )
    category = MCPToolCategory.NOVEL_MANAGEMENT
    parameters_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "地点名称（必填），如'迷雾森林''黑铁城堡'"},
            "location_type": {
                "type": "string",
                "enum": ["city", "town", "forest", "mountain", "building", "room",
                         "sea", "river", "road", "castle", "temple", "village",
                         "dungeon", "palace", "market", "inn", "other"],
                "description": "地点类型"
            },
            "description": {"type": "string", "description": "环境氛围、特色等描述"},
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "标签，如['危险','神秘','主角出生地']"
            },
            "parent_location_id": {"type": "integer", "description": "父级地点ID（用于构建层级关系）"},
        },
        "required": ["name"]
    }

    async def execute(self, db, novel_id: int=0, name: str="",
                     location_type: Optional[str]=None, description: Optional[str]=None,
                     tags: Optional[List[str]]=None, parent_location_id: Optional[int]=None,
                     user_id=None, **kwargs) -> MCPToolResult:
        try:
            result = await db.execute(select(Novel).where(Novel.id == novel_id))
            novel = result.scalar_one_or_none()
            if not novel:
                return MCPToolResult(success=False, error=f"小说 {novel_id} 不存在")
            
            from app.locations.schemas import LocationCreate, LocationType
            from app.locations.service import LocationService
            
            loc_data = LocationCreate(
                name=name,
                location_type=LocationType(location_type) if location_type else LocationType.OTHER,
                description=description,
                tags=tags,
                parent_location_id=parent_location_id,
            )
            
            svc = LocationService(db, novel_id)
            location = await svc.create(loc_data)
            
            return MCPToolResult(
                success=True,
                data={
                    "id": location.id,
                    "name": location.name,
                    "type": location.location_type,
                    "novel_id": novel_id,
                },
                metadata={"tool": self.name, "novel_id": novel_id, "location_id": location.id}
            )
        except Exception as e:
            return MCPToolResult(success=False, error=f"创建地点失败: {str(e)}")


def register_location_tools(registry) -> None:
    registry.register(GetLocationListTool())
    registry.register(GetLocationDetailTool())
    registry.register(CreateLocationTool())
