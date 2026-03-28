"""
MCP工具API路由
提供MCP工具的HTTP接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.response import ApiResponse
from app.core.auth import get_current_user
from app.core.dependencies import NovelOwner
from app.auth.models import User
from app.novels.models import Novel
from .base import MCPToolRegistry, MCPToolCategory
from .novel_tools import NovelManagementTools

router = APIRouter(prefix="/mcp", tags=["mcp"])


def get_mcp_registry(db: Session = Depends(get_db)) -> MCPToolRegistry:
    """获取MCP工具注册表实例"""
    registry = MCPToolRegistry()
    NovelManagementTools.register_all(db, registry)
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
    """
    获取小说摘要 - 便捷接口
    """
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
    """
    获取章节列表 - 便捷接口
    """
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
    """
    获取章节内容 - 便捷接口
    """
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
    """
    获取小说进度 - 便捷接口
    """
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
    """
    获取角色列表 - 便捷接口
    """
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
    """
    获取角色详情 - 便捷接口
    """
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
