"""
审查类MCP工具（整合版）
将原来分散的4个一致性检查工具合并为1个统一的 run_review 工具，
同时保留 list_unresolved_plots 的能力（作为 scope=foreshadowing）。
原来的工具类保留在文件末尾标记为 deprecated，不删除以防外部引用。
"""
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from .base import BaseMCPTool, MCPToolResult, MCPToolCategory, MCPToolRegistry
from app.novels.models import Novel
from app.chapters.models import Chapter
from app.characters.models import Character
from app.plot_events.models import PlotEvent
from app.timeline.models import TimelineEntry, TimelineEntryCategory, TimelineEntryStatus
from app.consistency.service import ConsistencyChecker


class RunReviewTool(BaseMCPTool):
    """统一审查工具 — 替代 check_character_consistency / check_plot_consistency / list_unresolved_plots / run_full_consistency_check"""

    name = "run_review"
    description = (
        "执行小说审查，支持多种检查类型。无需传novel_id，系统会注入当前小说ID。"
        "\n适用场景："
        "\n- 写完几章后检查角色/情节是否前后一致 → scope='character' 或 'plot'"
        "\n- 查看还有哪些伏笔没有回收 → scope='foreshadowing'"
        "\n- 全面体检发现潜在问题 → scope='full'"
        "\n通过 scope 参数指定检查范围，一次调用即可完成所有需要的检查。"
    )
    category = MCPToolCategory.CONSISTENCY_CHECK
    parameters_schema = {
        "type": "object",
        "properties": {
            "scope": {
                "type": "string",
                "enum": ["character", "plot", "foreshadowing", "full"],
                "description": "检查范围：character=角色一致性, plot=情节逻辑, foreshadowing=未回收伏笔, full=全面检查(含以上全部+时间线)"
            },
            "chapter_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "只检查指定章节（可选，不传则检查全部已完成章节）"
            },
            "min_importance": {
                "type": "integer",
                "description": "仅scope=foreshadowing时有效，筛选最低重要程度（1-5），默认不筛选"
            },
        },
        "required": ["scope"]
    }

    async def execute(
        self,
        db: AsyncSession,
        novel_id: int,
        scope: str,
        chapter_ids: Optional[List[int]] = None,
        min_importance: Optional[int] = None,
        user_id: Optional[int] = None,
        **kwargs
    ) -> MCPToolResult:
        result = await db.execute(select(Novel).where(Novel.id == novel_id))
        novel = result.scalar_one_or_none()
        if not novel:
            return MCPToolResult(success=False, error=f"Novel not found: {novel_id}")
        if user_id and novel.author_id != user_id:
            return MCPToolResult(success=False, error="无权访问此小说")

        try:
            if scope == "foreshadowing":
                return await self._query_foreshadowing(db, novel_id, min_importance)

            checker = ConsistencyChecker(db, novel_id)

            query = select(Chapter).where(Chapter.novel_id == novel_id, Chapter.status == "completed")
            if chapter_ids:
                query = query.where(Chapter.id.in_(chapter_ids))
            query = query.order_by(Chapter.chapter_number)
            result = await db.execute(query)
            chapters = result.scalars().all()

            if scope == "character":
                issues = await checker.check_character_consistency(chapters)
                return MCPToolResult(
                    success=True,
                    data={
                        "review_type": "character",
                        "issues": [issue.model_dump() for issue in issues],
                        "total_issues": len(issues),
                        "checked_chapters": len(chapters),
                        "summary": f"角色一致性检查完成，共{len(issues)}个问题" if issues else "角色一致性检查通过，未发现问题",
                    },
                    metadata={"tool": self.name, "novel_id": novel_id}
                )

            elif scope == "plot":
                issues = await checker.check_plot_consistency(chapters)
                return MCPToolResult(
                    success=True,
                    data={
                        "review_type": "plot",
                        "issues": [issue.model_dump() for issue in issues],
                        "total_issues": len(issues),
                        "checked_chapters": len(chapters),
                        "summary": f"情节逻辑检查完成，共{len(issues)}个问题" if issues else "情节逻辑检查通过，未发现问题",
                    },
                    metadata={"tool": self.name, "novel_id": novel_id}
                )

            elif scope == "full":
                check_result = await checker.check_all(
                    chapter_ids=chapter_ids,
                    check_types=["character", "plot", "timeline", "foreshadowing"]
                )
                foreshadowing_data = await self._query_foreshadowing(db, novel_id, min_importance, return_raw=True)
                check_result["unresolved_plots"] = foreshadowing_data.get("unresolved_plots", [])
                check_result["review_type"] = "full"
                return MCPToolResult(success=True, data=check_result, metadata={"tool": self.name, "novel_id": novel_id})

            else:
                return MCPToolResult(success=False, error=f"不支持的scope: {scope}")

        except Exception as e:
            return MCPToolResult(success=False, error=f"审查失败: {str(e)}")

    async def _query_foreshadowing(self, db, novel_id, min_importance=None, return_raw=False):
        query = select(TimelineEntry).where(
            TimelineEntry.novel_id == novel_id,
            TimelineEntry.category == TimelineEntryCategory.FORESHADOWING.value,
            TimelineEntry.status.in_([TimelineEntryStatus.PENDING.value, TimelineEntryStatus.ACTIVE.value])
        )
        if min_importance:
            query = query.where(TimelineEntry.importance >= min_importance)
        query = query.order_by(TimelineEntry.importance.desc(), TimelineEntry.created_at.desc())
        result = await db.execute(query)
        entries = result.scalars().all()

        result_list = []
        for entry in entries:
            pending_days = (datetime.now() - entry.created_at).days if entry.created_at else 0
            source_chapter = None
            if entry.source_chapter_id:
                ch_result = await db.execute(select(Chapter).where(Chapter.id == entry.source_chapter_id))
                chapter = ch_result.scalar_one_or_none()
                if chapter:
                    source_chapter = {"id": chapter.id, "chapter_number": chapter.chapter_number, "title": chapter.title}
            result_list.append({
                "id": entry.id, "title": entry.title, "description": entry.description,
                "category": entry.category, "importance": entry.importance, "status": entry.status,
                "source_chapter": source_chapter, "created_at": entry.created_at.isoformat() if entry.created_at else None,
                "days_pending": pending_days, "detail_json": entry.detail_json
            })

        data = {"review_type": "foreshadowing", "unresolved_plots": result_list, "total": len(result_list), "filters": {"min_importance": min_importance}}
        if return_raw:
            return data
        return MCPToolResult(success=True, data=data, metadata={"tool": self.name, "novel_id": novel_id})


# ========== 以下为 deprecated 旧工具类，保留以兼容可能的直接引用 ==========
# 已被 RunReviewTool(scope=...) 完全替代

class CheckCharacterConsistencyTool(BaseMCPTool):
    """[deprecated] 使用 run_review(scope='character') 替代"""
    name = "check_character_consistency"
    description = "[已弃用] 请使用 run_review(scope='character')"
    category = MCPToolCategory.CONSISTENCY_CHECK
    parameters_schema = {"type": "object", "properties": {}, "required": []}
    async def execute(self, db, **kwargs):
        return MCPToolResult(success=False, error="此工具已弃用，请使用 run_review(scope='character')")

class CheckPlotConsistencyTool(BaseMCPTool):
    """[deprecated] 使用 run_review(scope='plot') 替代"""
    name = "check_plot_consistency"
    description = "[已弃用] 请使用 run_review(scope='plot')"
    category = MCPToolCategory.CONSISTENCY_CHECK
    parameters_schema = {"type": "object", "properties": {}, "required": []}
    async def execute(self, db, **kwargs):
        return MCPToolResult(success=False, error="此工具已弃用，请使用 run_review(scope='plot')")

class ListUnresolvedPlotsTool(BaseMCPTool):
    """[deprecated] 使用 run_review(scope='foreshadowing') 替代"""
    name = "list_unresolved_plots"
    description = "[已弃用] 请使用 run_review(scope='foreshadowing')"
    category = MCPToolCategory.CONSISTENCY_CHECK
    parameters_schema = {"type": "object", "properties": {}, "required": []}
    async def execute(self, db, **kwargs):
        return MCPToolResult(success=False, error="此工具已弃用，请使用 run_review(scope='foreshadowing')")

class RunFullConsistencyCheckTool(BaseMCPTool):
    """[deprecated] 使用 run_review(scope='full') 替代"""
    name = "run_full_consistency_check"
    description = "[已弃用] 请使用 run_review(scope='full')"
    category = MCPToolCategory.CONSISTENCY_CHECK
    parameters_schema = {"type": "object", "properties": {}, "required": []}
    async def execute(self, db, **kwargs):
        return MCPToolResult(success=False, error="此工具已弃用，请使用 run_review(scope='full')")


class ConsistencyCheckTools:
    """审查工具集合 — 只注册新的 RunReviewTool"""

    @staticmethod
    def register_all(registry: MCPToolRegistry) -> None:
        registry.register(RunReviewTool())
