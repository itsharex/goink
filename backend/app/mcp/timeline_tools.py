"""
故事时间线MCP工具集
供AI调用的5个核心工具：查询/添加/更新/解决/获取上下文
"""
from typing import Any, Dict, List, Optional
from enum import Enum

from .base import BaseMCPTool, MCPToolResult, MCPToolCategory, MCPToolRegistry
from app.timeline.models import TimelineEntry
from app.timeline.schemas import (
    TimelineEntryCreate,
    TimelineEntryUpdate,
    TimelineEntryResolve,
)
from app.timeline.service import TimelineService


class GetStoryTimelineTool(BaseMCPTool):
    """获取故事时间线"""

    name = "get_story_timeline"
    description = (
        "获取当前小说的完整故事时间线，包含伏笔、章节规划、用户指令等所有条目。"
        "支持按分类、状态、时间范围筛选。返回结果按目标章节号排序。"
        "无需传novel_id，系统会注入当前小说ID。"
        "\n适用场景：需要全面了解故事规划、查看未回收伏笔、确认未来安排时调用。"
    )
    category = MCPToolCategory.NOVEL_MANAGEMENT
    parameters_schema = {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["foreshadowing", "plot_node", "chapter_plan", "user_directive"],
                "description": "按分类筛选：foreshadowing(伏笔)/plot_node(情节节点)/chapter_plan(章节规划)/user_directive(用户指令)"
            },
            "status": {
                "type": "string",
                "enum": ["pending", "active", "completed", "resolved", "abandoned", "deferred"],
                "description": "按状态筛选"
            },
            "time_horizon": {
                "type": "string",
                "enum": ["next", "near_term", "long_term", "undefined"],
                "description": "按时间范围筛选：next(下一章)/near_term(近期)/long_term(远期)"
            },
            "search": {"type": "string", "description": "搜索关键词（匹配标题和描述）"},
            "page": {"type": "integer", "default": 1, "description": "页码"},
            "page_size": {"type": "integer", "default": 20, "description": "每页数量，最大100"},
        },
    }

    async def execute(
        self,
        db,
        novel_id: int,
        category: Optional[str] = None,
        status: Optional[str] = None,
        time_horizon: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        **kwargs
    ) -> MCPToolResult:
        try:
            service = TimelineService(db, novel_id)
            items, total = await service.get_timeline(
                page=page, page_size=page_size, category=category,
                status=status, time_horizon=time_horizon, search=search,
            )
            return MCPToolResult(
                success=True,
                data={
                    "items": [_entry_to_dict(e) for e in items],
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                },
                metadata={"tool": self.name, "novel_id": novel_id}
            )
        except Exception as e:
            return MCPToolResult(success=False, error=f"获取时间线失败: {str(e)}")


class AddTimelineEntryTool(BaseMCPTool):
    """添加时间线条目"""

    name = "add_timeline_entry"
    description = (
        "向故事时间线中添加一条新条目。可以添加伏笔/钩子、章节规划、用户指令等。"
        "无需传novel_id，系统会注入当前小说ID。"
        "\n适用场景：章节生成后自动提取伏笔和规划、用户通过对话要求记录某个想法或安排时调用。"
        "\n分类说明："
        "- foreshadowing: 本章埋下的伏笔/钩子（待后续章节回收）"
        "- chapter_plan: 章节安排（下章/近期/远期的写作计划）"
        "- user_directive: 用户主动告知的创作规则或方向性指令"
        "- plot_node: 情节节点（关键事件里程碑）"
    )
    category = MCPToolCategory.WRITING_ASSISTANT
    parameters_schema = {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["foreshadowing", "plot_node", "chapter_plan", "user_directive"],
                "description": "条目分类（必填）"
            },
            "title": {"type": "string", "description": "标题（必填）"},
            "description": {"type": "string", "description": "详细描述"},
            "detail_json": {"type": "object", "description": "结构化详情（因category而异）"},
            "target_chapter": {"type": "integer", "description": "目标章节号（可选）"},
            "time_horizon": {
                "type": "string",
                "enum": ["next", "near_term", "long_term", "undefined"],
                "description": "时间范围"
            },
            "importance": {"type": "integer", "default": 3, "description": "重要程度1-5"},
            "source_chapter_id": {"type": "integer", "description": "来源章节ID（如从某章提取）"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "标签列表"},
        },
        "required": ["category", "title"],
    }

    async def execute(
        self,
        db,
        novel_id: int,
        category: str,
        title: str,
        description: Optional[str] = None,
        detail_json: Optional[Dict] = None,
        target_chapter: Optional[int] = None,
        time_horizon: Optional[str] = None,
        importance: int = 3,
        source_chapter_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> MCPToolResult:
        try:
            data = TimelineEntryCreate(
                category=category,
                title=title,
                description=description,
                detail_json=detail_json,
                target_chapter=target_chapter,
                time_horizon=time_horizon,
                importance=importance,
                source="ai_generated",
                source_chapter_id=source_chapter_id,
                tags=tags,
            )
            service = TimelineService(db, novel_id)
            entry = await service.add_entry(data)
            return MCPToolResult(
                success=True,
                data=_entry_to_dict(entry),
                metadata={"tool": self.name, "novel_id": novel_id}
            )
        except Exception as e:
            return MCPToolResult(success=False, error=f"添加时间线条目失败: {str(e)}")


class UpdateTimelineEntryTool(BaseMCPTool):
    """更新时间线条目"""

    name = "update_timeline_entry"
    description = (
        "更新已有的时间线条目内容。适用于AI根据新信息修正规划、或应用户要求修改条目时使用。"
        "每次更新会递增版本号并保留原始AI输出（如果之前是AI创建的），方便追踪变更历史。"
        "无需传novel_id，系统会注入当前小说ID。"
        "\n注意：只能修改标题、描述、详情等字段；要改变状态（如标记已解决）请用 resolve_timeline_entry。"
    )
    category = MCPToolCategory.WRITING_ASSISTANT
    parameters_schema = {
        "type": "object",
        "properties": {
            "entry_id": {"type": "integer", "description": "条目ID（必填）"},
            "title": {"type": "string", "description": "新的标题"},
            "description": {"type": "string", "description": "新的描述"},
            "detail_json": {"type": "object", "description": "新的结构化详情"},
            "target_chapter": {"type": "integer", "description": "新的目标章节号"},
            "time_horizon": {
                "type": "string",
                "enum": ["next", "near_term", "long_term", "undefined"],
                "description": "新的时间范围"
            },
            "status": {
                "type": "string",
                "enum": ["pending", "active", "completed", "resolved", "abandoned", "deferred"],
                "description": "新状态"
            },
            "importance": {"type": "integer", "description": "新的重要程度(1-5)"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "新的标签列表"},
        },
        "required": ["entry_id"],
    }

    async def execute(
        self,
        db,
        novel_id: int,
        entry_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        detail_json: Optional[Dict] = None,
        target_chapter: Optional[int] = None,
        time_horizon: Optional[str] = None,
        status: Optional[str] = None,
        importance: Optional[int] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> MCPToolResult:
        try:
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if description is not None:
                update_data["description"] = description
            if detail_json is not None:
                update_data["detail_json"] = detail_json
            if target_chapter is not None:
                update_data["target_chapter"] = target_chapter
            if time_horizon is not None:
                update_data["time_horizon"] = time_horizon
            if status is not None:
                update_data["status"] = status
            if importance is not None:
                update_data["importance"] = importance
            if tags is not None:
                update_data["tags"] = tags

            data = TimelineEntryUpdate(**update_data) if update_data else TimelineEntryUpdate()
            service = TimelineService(db, novel_id)
            entry = await service.update_entry(entry_id, data, editor="ai")
            if not entry:
                return MCPToolResult(success=False, error=f"条目 {entry_id} 不存在")
            return MCPToolResult(
                success=True,
                data=_entry_to_dict(entry),
                metadata={"tool": self.name, "novel_id": novel_id, "version": entry.version}
            )
        except Exception as e:
            return MCPToolResult(success=False, error=f"更新时间线条目失败: {str(e)}")


class ResolveTimelineEntryTool(BaseMCPTool):
    """解决/完成时间线条目"""

    name = "resolve_timeline_entry"
    description = (
        "将一条时间线条目标记为已解决/已完成/已废弃。主要用于："
        "1. 伏笔被回收时标记为resolved；2. 规划事项完成时标记为completed；3. 不再需要的条目标记为abandoned。"
        "无需传novel_id，系统会注入当前小说ID。"
        "\n💡 提示：此工具是 update_timeline_entry 的快捷方式（专门用于状态变更），也可以直接用 update_timeline_entry 并设置 status 参数。"
    )
    category = MCPToolCategory.WRITING_ASSISTANT
    parameters_schema = {
        "type": "object",
        "properties": {
            "entry_id": {"type": "integer", "description": "条目ID（必填）"},
            "resolved_chapter_id": {"type": "integer", "description": "解决时的章节ID（可选）"},
            "resolution_notes": {"type": "string", "description": "解决说明（可选）"},
        },
        "required": ["entry_id"],
    }

    async def execute(
        self,
        db,
        novel_id: int,
        entry_id: int,
        resolved_chapter_id: Optional[int] = None,
        resolution_notes: Optional[str] = None,
        **kwargs
    ) -> MCPToolResult:
        try:
            data = TimelineEntryResolve(
                resolved_chapter_id=resolved_chapter_id,
                resolution_notes=resolution_notes,
            )
            service = TimelineService(db, novel_id)
            entry = await service.resolve_entry(entry_id, data)
            if not entry:
                return MCPToolResult(success=False, error=f"条目 {entry_id} 不存在")
            return MCPToolResult(
                success=True,
                data=_entry_to_dict(entry),
                metadata={
                    "tool": self.name,
                    "novel_id": novel_id,
                    "new_status": entry.status,
                }
            )
        except Exception as e:
            return MCPToolResult(success=False, error=f"解决时间线条目失败: {str(e)}")


class GetTimelineContextTool(BaseMCPTool):
    """获取AI生成用的精简时间线上下文"""

    name = "get_timeline_context"
    description = (
        "获取精简的故事时间线上下文，专为AI生成章节时设计。"
        "智能筛选与当前章节最相关的条目（未完成的伏笔、近期的规划、用户指令等）。"
        "无需传novel_id，系统会注入当前小说ID。"
        "\n这是生成章节前应该调用的工具，帮助AI了解当前有哪些待处理的事项和约束。"
        "\n如果返回的结果不够，可以再调用 get_story_timeline 查看完整时间线。"
    )
    category = MCPToolCategory.MEMORY_RETRIEVAL
    parameters_schema = {
        "type": "object",
        "properties": {
            "current_chapter": {"type": "integer", "description": "当前章节号（必填）"},
            "max_entries": {"type": "integer", "default": 15, "description": "最大返回条数(1-50)"},
        },
        "required": ["current_chapter"],
    }

    async def execute(
        self,
        db,
        novel_id: int,
        current_chapter: int,
        max_entries: int = 15,
        **kwargs
    ) -> MCPToolResult:
        try:
            service = TimelineService(db, novel_id)
            entries, summary_text = await service.get_context_for_generation(current_chapter, max_entries)
            return MCPToolResult(
                success=True,
                data={
                    "entries": [_entry_to_dict(e) for e in entries],
                    "total_count": len(entries),
                    "summary_text": summary_text,
                    "current_chapter": current_chapter,
                },
                metadata={
                    "tool": self.name,
                    "novel_id": novel_id,
                    "max_entries": max_entries,
                }
            )
        except Exception as e:
            return MCPToolResult(success=False, error=f"获取时间线上下文失败: {str(e)}")


def _entry_to_dict(entry: TimelineEntry) -> Dict[str, Any]:
    return {
        "id": entry.id,
        "category": entry.category,
        "status": entry.status,
        "title": entry.title,
        "description": entry.description,
        "detail_json": entry.detail_json,
        "target_chapter": entry.target_chapter,
        "time_horizon": entry.time_horizon,
        "importance": entry.importance,
        "source": entry.source,
        "source_chapter_id": entry.source_chapter_id,
        "version": entry.version,
        "last_editor": entry.last_editor,
        "tags": entry.tags,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
    }


def register_timeline_tools(registry: MCPToolRegistry):
    registry.register(GetStoryTimelineTool())
    registry.register(AddTimelineEntryTool())
    registry.register(UpdateTimelineEntryTool())
    registry.register(ResolveTimelineEntryTool())
    registry.register(GetTimelineContextTool())
