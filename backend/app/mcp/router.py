"""
MCP工具API路由
提供MCP工具的HTTP接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.response import ApiResponse
from app.core.auth import get_current_user
from app.core.dependencies import NovelOwner
from app.auth.models import User
from app.novels.models import Novel
from .base import MCPToolRegistry, MCPToolCategory
from .novel_tools import NovelManagementTools
from .memory_tools import MemoryRetrievalTools
from .consistency_tools import ConsistencyCheckTools

router = APIRouter(prefix="/mcp", tags=["mcp"])


def get_mcp_registry(db: Session = Depends(get_db)) -> MCPToolRegistry:
    """获取MCP工具注册表实例"""
    registry = MCPToolRegistry()
    NovelManagementTools.register_all(db, registry)
    MemoryRetrievalTools.register_all(db, registry)
    ConsistencyCheckTools.register_all(db, registry)
    return registry


@router.get("/tools")
def list_tools(
    category: Optional[str] = Query(None, description="工具分类筛选"),
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    """
    列出所有可用的MCP工具
    
    - category: 可选的分类筛选 (novel_management/memory_retrieval/consistency_check/writing_assistant)
    """
    cat = None
    if category:
        try:
            cat = MCPToolCategory(category)
        except ValueError:
            pass
    
    tools = registry.list_tools(cat)
    
    return ApiResponse.success({
        "tools": tools,
        "total": len(tools)
    })


@router.get("/tools/categories")
def list_categories(
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    """
    按分类列出所有工具
    """
    result = registry.list_by_category()
    
    return ApiResponse.success(result)


@router.get("/tools/{tool_name}")
def get_tool_info(
    tool_name: str,
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定工具的详细信息
    """
    tool = registry.get(tool_name)
    if not tool:
        return ApiResponse.error("NOT_FOUND", f"Tool not found: {tool_name}")
    
    return ApiResponse.success(tool.get_info())


@router.post("/tools/{tool_name}/execute")
async def execute_tool(
    tool_name: str,
    params: dict,
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    """
    执行指定的MCP工具
    
    - params: 工具参数，根据不同工具有不同的参数要求
    """
    result = await registry.execute(tool_name, **params)
    
    return ApiResponse.success(
        {
            "success": result.success,
            "data": result.data,
            "error": result.error,
            "metadata": result.metadata
        },
        message="工具执行完成" if result.success else "工具执行失败"
    )


@router.post("/novels/{novel_id}/summary")
async def get_novel_summary(
    novel: Novel = NovelOwner,
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    result = await registry.execute("get_novel_summary", novel_id=novel.id)
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")


@router.post("/novels/{novel_id}/chapters/list")
async def get_chapter_list(
    novel: Novel = NovelOwner,
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    result = await registry.execute(
        "get_chapter_list",
        novel_id=novel.id,
        status=status,
        page=page,
        page_size=page_size
    )
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")


@router.post("/chapters/{chapter_id}/content")
async def get_chapter_content(
    chapter_id: int,
    include_summary: bool = Query(True),
    db: Session = Depends(get_db),
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    from app.chapters.models import Chapter
    from app.core.exceptions import NotFoundException, UnauthorizedException
    
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException("章节")
    
    novel = db.query(Novel).filter(Novel.id == chapter.novel_id).first()
    if not novel or novel.author_id != current_user.id:
        raise UnauthorizedException("无权访问此章节")
    
    result = await registry.execute(
        "get_chapter_content",
        chapter_id=chapter_id,
        include_summary=include_summary
    )
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")


@router.post("/novels/{novel_id}/progress")
async def get_novel_progress(
    novel: Novel = NovelOwner,
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    result = await registry.execute("get_novel_progress", novel_id=novel.id)
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")


@router.post("/novels/{novel_id}/characters/list")
async def get_character_list(
    novel: Novel = NovelOwner,
    search: Optional[str] = Query(None),
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    result = await registry.execute(
        "get_character_list",
        novel_id=novel.id,
        search=search
    )
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")


@router.post("/characters/{character_id}/detail")
async def get_character_detail(
    character_id: int,
    db: Session = Depends(get_db),
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    from app.characters.models import Character
    from app.core.exceptions import NotFoundException, UnauthorizedException
    
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise NotFoundException("角色")
    
    novel = db.query(Novel).filter(Novel.id == character.novel_id).first()
    if not novel or novel.author_id != current_user.id:
        raise UnauthorizedException("无权访问此角色")
    
    result = await registry.execute(
        "get_character_detail",
        character_id=character_id
    )
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")


@router.post("/novels/{novel_id}/memory/search")
async def search_plot_memory(
    novel: Novel = NovelOwner,
    query: str = Query(..., description="搜索查询文本"),
    top_k: int = Query(10, ge=1, le=50, description="返回结果数量"),
    chapter_ids: Optional[str] = Query(None, description="限定章节ID，逗号分隔"),
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    ids = None
    if chapter_ids:
        ids = [int(x.strip()) for x in chapter_ids.split(",") if x.strip().isdigit()]
    
    result = await registry.execute(
        "search_plot_memory",
        novel_id=novel.id,
        query=query,
        top_k=top_k,
        chapter_ids=ids
    )
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")


@router.post("/characters/{character_id}/memory")
async def get_character_memory(
    character_id: int,
    include_plot_events: bool = Query(True, description="是否包含情节事件"),
    db: Session = Depends(get_db),
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    from app.characters.models import Character
    from app.core.exceptions import NotFoundException, UnauthorizedException
    
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise NotFoundException("角色")
    
    novel = db.query(Novel).filter(Novel.id == character.novel_id).first()
    if not novel or novel.author_id != current_user.id:
        raise UnauthorizedException("无权访问此角色")
    
    result = await registry.execute(
        "get_character_memory",
        novel_id=novel.id,
        character_id=character_id,
        include_plot_events=include_plot_events
    )
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")


@router.post("/novels/{novel_id}/timeline")
async def get_timeline(
    novel: Novel = NovelOwner,
    start_chapter: Optional[int] = Query(None, description="起始章节号"),
    end_chapter: Optional[int] = Query(None, description="结束章节号"),
    event_types: Optional[str] = Query(None, description="事件类型，逗号分隔"),
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    types = None
    if event_types:
        types = [x.strip() for x in event_types.split(",") if x.strip()]
    
    result = await registry.execute(
        "get_timeline",
        novel_id=novel.id,
        start_chapter=start_chapter,
        end_chapter=end_chapter,
        event_types=types
    )
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")


@router.post("/chapters/{chapter_id}/context")
async def get_recent_context(
    chapter_id: int,
    window_size: int = Query(3, ge=1, le=10, description="前文章节数量"),
    context_size: int = Query(3000, ge=500, le=10000, description="上下文最大字符数"),
    db: Session = Depends(get_db),
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    from app.chapters.models import Chapter
    from app.core.exceptions import NotFoundException, UnauthorizedException
    
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException("章节")
    
    novel = db.query(Novel).filter(Novel.id == chapter.novel_id).first()
    if not novel or novel.author_id != current_user.id:
        raise UnauthorizedException("无权访问此章节")
    
    result = await registry.execute(
        "get_recent_context",
        novel_id=novel.id,
        chapter_id=chapter_id,
        window_size=window_size,
        context_size=context_size
    )
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")


@router.post("/novels/{novel_id}/consistency/character")
async def check_character_consistency(
    novel: Novel = NovelOwner,
    chapter_ids: Optional[str] = Query(None, description="章节ID，逗号分隔"),
    character_id: Optional[int] = Query(None, description="指定角色ID"),
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    ids = None
    if chapter_ids:
        ids = [int(x.strip()) for x in chapter_ids.split(",") if x.strip().isdigit()]
    
    result = await registry.execute(
        "check_character_consistency",
        novel_id=novel.id,
        chapter_ids=ids,
        character_id=character_id
    )
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")


@router.post("/novels/{novel_id}/consistency/plot")
async def check_plot_consistency(
    novel: Novel = NovelOwner,
    chapter_ids: Optional[str] = Query(None, description="章节ID，逗号分隔"),
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    ids = None
    if chapter_ids:
        ids = [int(x.strip()) for x in chapter_ids.split(",") if x.strip().isdigit()]
    
    result = await registry.execute(
        "check_plot_consistency",
        novel_id=novel.id,
        chapter_ids=ids
    )
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")


@router.post("/novels/{novel_id}/consistency/full")
async def run_full_consistency_check(
    novel: Novel = NovelOwner,
    chapter_ids: Optional[str] = Query(None, description="章节ID，逗号分隔"),
    check_types: Optional[str] = Query(None, description="检查类型，逗号分隔(character,plot,timeline,foreshadowing)"),
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    ids = None
    if chapter_ids:
        ids = [int(x.strip()) for x in chapter_ids.split(",") if x.strip().isdigit()]
    
    types = None
    if check_types:
        types = [x.strip() for x in check_types.split(",") if x.strip()]
    
    result = await registry.execute(
        "run_full_consistency_check",
        novel_id=novel.id,
        chapter_ids=ids,
        check_types=types
    )
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")


@router.get("/novels/{novel_id}/foreshadowing/unresolved")
async def list_unresolved_plots(
    novel: Novel = NovelOwner,
    min_importance: Optional[int] = Query(None, ge=1, le=5, description="最小重要程度"),
    days_pending: Optional[int] = Query(None, ge=1, description="挂起天数筛选"),
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    result = await registry.execute(
        "list_unresolved_plots",
        novel_id=novel.id,
        min_importance=min_importance,
        days_pending=days_pending
    )
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")


@router.get("/novels/{novel_id}/foreshadowing/status")
async def get_foreshadowing_status(
    novel: Novel = NovelOwner,
    registry: MCPToolRegistry = Depends(get_mcp_registry),
    current_user: User = Depends(get_current_user)
):
    result = await registry.execute(
        "get_foreshadowing_status",
        novel_id=novel.id
    )
    
    if result.success:
        return ApiResponse.success(result.data)
    return ApiResponse.error("TOOL_ERROR", result.error or "Unknown error")
