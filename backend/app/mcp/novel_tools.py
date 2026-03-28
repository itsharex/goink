"""
小说管理类MCP工具
提供小说信息查询的标准接口
"""
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from .base import BaseMCPTool, MCPToolResult, MCPToolCategory, MCPToolRegistry
from app.novels.models import Novel
from app.chapters.models import Chapter
from app.characters.models import Character


class GetNovelSummaryTool(BaseMCPTool):
    """获取小说整体摘要"""
    
    name = "get_novel_summary"
    description = "获取小说的整体摘要信息，包括标题、类型、描述、状态、章节数、字数、角色数等"
    category = MCPToolCategory.NOVEL_MANAGEMENT
    parameters_schema = {
        "type": "object",
        "properties": {
            "novel_id": {
                "type": "integer",
                "description": "小说ID"
            }
        },
        "required": ["novel_id"]
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    async def execute(self, novel_id: int, **kwargs) -> MCPToolResult:
        novel = self.db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            return MCPToolResult(
                success=False,
                error=f"Novel not found: {novel_id}"
            )
        
        chapters = novel.chapters
        characters = novel.characters
        total_words = sum(len(ch.content or "") for ch in chapters)
        completed_chapters = len([ch for ch in chapters if ch.status == "completed"])
        
        summary = {
            "id": novel.id,
            "title": novel.title,
            "genre": novel.genre,
            "description": novel.description,
            "status": novel.status,
            "chapter_count": len(chapters),
            "completed_chapters": completed_chapters,
            "word_count": total_words,
            "character_count": len(characters),
            "created_at": novel.created_at.isoformat() if novel.created_at else None,
            "updated_at": novel.updated_at.isoformat() if novel.updated_at else None
        }
        
        return MCPToolResult(
            success=True,
            data=summary,
            metadata={"tool": self.name, "novel_id": novel_id}
        )


class GetChapterListTool(BaseMCPTool):
    """获取章节列表"""
    
    name = "get_chapter_list"
    description = "获取小说的章节列表，支持分页和状态筛选"
    category = MCPToolCategory.NOVEL_MANAGEMENT
    parameters_schema = {
        "type": "object",
        "properties": {
            "novel_id": {
                "type": "integer",
                "description": "小说ID"
            },
            "status": {
                "type": "string",
                "enum": ["draft", "completed"],
                "description": "章节状态筛选（可选）"
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "页码"
            },
            "page_size": {
                "type": "integer",
                "default": 20,
                "description": "每页数量"
            }
        },
        "required": ["novel_id"]
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    async def execute(
        self, 
        novel_id: int, 
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        **kwargs
    ) -> MCPToolResult:
        novel = self.db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            return MCPToolResult(
                success=False,
                error=f"Novel not found: {novel_id}"
            )
        
        query = self.db.query(Chapter).filter(Chapter.novel_id == novel_id)
        
        if status:
            query = query.filter(Chapter.status == status)
        
        total = query.count()
        chapters = query.order_by(Chapter.chapter_number).offset((page - 1) * page_size).limit(page_size).all()
        
        items = [
            {
                "id": ch.id,
                "chapter_number": ch.chapter_number,
                "title": ch.title,
                "word_count": len(ch.content or ""),
                "status": ch.status,
                "summary": ch.summary,
                "created_at": ch.created_at.isoformat() if ch.created_at else None,
                "updated_at": ch.updated_at.isoformat() if ch.updated_at else None
            }
            for ch in chapters
        ]
        
        return MCPToolResult(
            success=True,
            data={
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            },
            metadata={"tool": self.name, "novel_id": novel_id}
        )


class GetChapterContentTool(BaseMCPTool):
    """获取章节内容"""
    
    name = "get_chapter_content"
    description = "获取指定章节的完整内容"
    category = MCPToolCategory.NOVEL_MANAGEMENT
    parameters_schema = {
        "type": "object",
        "properties": {
            "chapter_id": {
                "type": "integer",
                "description": "章节ID"
            },
            "include_summary": {
                "type": "boolean",
                "default": True,
                "description": "是否包含摘要"
            }
        },
        "required": ["chapter_id"]
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    async def execute(
        self, 
        chapter_id: int, 
        include_summary: bool = True,
        **kwargs
    ) -> MCPToolResult:
        chapter = self.db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            return MCPToolResult(
                success=False,
                error=f"Chapter not found: {chapter_id}"
            )
        
        result = {
            "id": chapter.id,
            "novel_id": chapter.novel_id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "content": chapter.content,
            "word_count": len(chapter.content or ""),
            "status": chapter.status,
            "created_at": chapter.created_at.isoformat() if chapter.created_at else None,
            "updated_at": chapter.updated_at.isoformat() if chapter.updated_at else None
        }
        
        if include_summary:
            result["summary"] = chapter.summary
        
        return MCPToolResult(
            success=True,
            data=result,
            metadata={"tool": self.name, "chapter_id": chapter_id}
        )


class GetNovelProgressTool(BaseMCPTool):
    """获取小说进度"""
    
    name = "get_novel_progress"
    description = "获取小说的写作进度，包括章节完成情况、字数统计、角色数量等"
    category = MCPToolCategory.NOVEL_MANAGEMENT
    parameters_schema = {
        "type": "object",
        "properties": {
            "novel_id": {
                "type": "integer",
                "description": "小说ID"
            }
        },
        "required": ["novel_id"]
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    async def execute(self, novel_id: int, **kwargs) -> MCPToolResult:
        novel = self.db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            return MCPToolResult(
                success=False,
                error=f"Novel not found: {novel_id}"
            )
        
        chapters = novel.chapters
        characters = novel.characters
        plot_events = novel.plot_events
        
        total_chapters = len(chapters)
        completed_chapters = len([ch for ch in chapters if ch.status == "completed"])
        draft_chapters = total_chapters - completed_chapters
        total_words = sum(len(ch.content or "") for ch in chapters)
        
        avg_words_per_chapter = total_words / total_chapters if total_chapters > 0 else 0
        
        progress_percentage = (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0
        
        latest_chapter = None
        if chapters:
            latest = max(chapters, key=lambda x: x.chapter_number)
            latest_chapter = {
                "chapter_number": latest.chapter_number,
                "title": latest.title,
                "status": latest.status
            }
        
        progress = {
            "novel_id": novel.id,
            "novel_title": novel.title,
            "novel_status": novel.status,
            "chapters": {
                "total": total_chapters,
                "completed": completed_chapters,
                "draft": draft_chapters,
                "progress_percentage": round(progress_percentage, 2)
            },
            "words": {
                "total": total_words,
                "average_per_chapter": round(avg_words_per_chapter, 2)
            },
            "characters": {
                "total": len(characters)
            },
            "plot_events": {
                "total": len(plot_events)
            },
            "latest_chapter": latest_chapter
        }
        
        return MCPToolResult(
            success=True,
            data=progress,
            metadata={"tool": self.name, "novel_id": novel_id}
        )


class GetCharacterListTool(BaseMCPTool):
    """获取角色列表"""
    
    name = "get_character_list"
    description = "获取小说的角色列表"
    category = MCPToolCategory.NOVEL_MANAGEMENT
    parameters_schema = {
        "type": "object",
        "properties": {
            "novel_id": {
                "type": "integer",
                "description": "小说ID"
            },
            "search": {
                "type": "string",
                "description": "角色名搜索（可选）"
            }
        },
        "required": ["novel_id"]
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    async def execute(
        self, 
        novel_id: int, 
        search: Optional[str] = None,
        **kwargs
    ) -> MCPToolResult:
        novel = self.db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            return MCPToolResult(
                success=False,
                error=f"Novel not found: {novel_id}"
            )
        
        query = self.db.query(Character).filter(Character.novel_id == novel_id)
        
        if search:
            query = query.filter(Character.name.contains(search))
        
        characters = query.all()
        
        items = [
            {
                "id": ch.id,
                "name": ch.name,
                "personality": ch.personality,
                "abilities": ch.abilities,
                "relationships": ch.relationships,
                "created_at": ch.created_at.isoformat() if ch.created_at else None
            }
            for ch in characters
        ]
        
        return MCPToolResult(
            success=True,
            data=items,
            metadata={"tool": self.name, "novel_id": novel_id, "total": len(items)}
        )


class GetCharacterDetailTool(BaseMCPTool):
    """获取角色详情"""
    
    name = "get_character_detail"
    description = "获取指定角色的详细信息"
    category = MCPToolCategory.NOVEL_MANAGEMENT
    parameters_schema = {
        "type": "object",
        "properties": {
            "character_id": {
                "type": "integer",
                "description": "角色ID"
            }
        },
        "required": ["character_id"]
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    async def execute(self, character_id: int, **kwargs) -> MCPToolResult:
        character = self.db.query(Character).filter(Character.id == character_id).first()
        if not character:
            return MCPToolResult(
                success=False,
                error=f"Character not found: {character_id}"
            )
        
        result = {
            "id": character.id,
            "novel_id": character.novel_id,
            "name": character.name,
            "personality": character.personality,
            "abilities": character.abilities,
            "relationships": character.relationships,
            "created_at": character.created_at.isoformat() if character.created_at else None,
            "novel": {
                "id": character.novel.id,
                "title": character.novel.title
            } if character.novel else None
        }
        
        return MCPToolResult(
            success=True,
            data=result,
            metadata={"tool": self.name, "character_id": character_id}
        )


class NovelManagementTools:
    """小说管理工具集合"""
    
    @staticmethod
    def register_all(db: Session, registry: MCPToolRegistry) -> None:
        """注册所有小说管理工具"""
        registry.register(GetNovelSummaryTool(db))
        registry.register(GetChapterListTool(db))
        registry.register(GetChapterContentTool(db))
        registry.register(GetNovelProgressTool(db))
        registry.register(GetCharacterListTool(db))
        registry.register(GetCharacterDetailTool(db))
