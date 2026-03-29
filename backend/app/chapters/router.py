"""
章节管理模块 - API路由
"""
from fastapi import APIRouter, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional

from app.core.response import ApiResponse
from app.core.database import DBSession
from app.core.auth import CurrentUser
from app.core.dependencies import NovelOwner
from app.core.exceptions import NotFoundException, UnauthorizedException
from app.novels.models import Novel
from .models import Chapter
from .schemas import ChapterCreate, ChapterUpdate

router = APIRouter(prefix="/chapters", tags=["chapters"])


@router.get("/novel/{novel_id}")
async def get_chapters_by_novel(
    novel: NovelOwner,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    order: str = Query("asc", pattern="^(asc|desc)$")
):
    """
    获取小说章节列表
    
    - novel_id: 小说ID
    - page: 页码
    - page_size: 每页数量
    - status: 状态筛选 (draft/completed)
    - order: 排序 (asc/desc)
    """
    query = select(Chapter).where(Chapter.novel_id == novel.id)
    
    if status:
        query = query.where(Chapter.status == status)
    
    if order == "desc":
        query = query.order_by(Chapter.chapter_number.desc())
    else:
        query = query.order_by(Chapter.chapter_number.asc())
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    chapters = result.scalars().all()
    
    items = [
        {
            "id": ch.id,
            "novel_id": ch.novel_id,
            "chapter_number": ch.chapter_number,
            "title": ch.title,
            "word_count": len(ch.content or ""),
            "status": ch.status,
            "summary": ch.summary,
            "created_at": ch.created_at,
            "updated_at": ch.updated_at
        }
        for ch in chapters
    ]
    
    return ApiResponse.paginated(items, total, page, page_size)


@router.post("", status_code=201)
async def create_chapter(
    chapter: ChapterCreate, 
    db: DBSession,
    current_user: CurrentUser
):
    """
    创建章节
    """
    result = await db.execute(
        select(Novel).where(Novel.id == chapter.novel_id)
    )
    novel = result.scalar_one_or_none()
    
    if novel is None:
        raise NotFoundException("小说")
    if novel.author_id != current_user.id:
        raise UnauthorizedException("无权访问此小说")
    
    db_chapter = Chapter(**chapter.model_dump())
    db.add(db_chapter)
    await db.commit()
    await db.refresh(db_chapter)
    
    return ApiResponse.success(
        {
            "id": db_chapter.id,
            "novel_id": db_chapter.novel_id,
            "chapter_number": db_chapter.chapter_number,
            "title": db_chapter.title,
            "content": db_chapter.content,
            "summary": db_chapter.summary,
            "status": db_chapter.status,
            "word_count": len(db_chapter.content or ""),
            "created_at": db_chapter.created_at
        },
        message="章节创建成功"
    )


@router.get("/{chapter_id}")
async def get_chapter(
    chapter_id: int, 
    db: DBSession,
    current_user: CurrentUser
):
    """
    获取章节详情
    """
    result = await db.execute(
        select(Chapter)
        .options(
            selectinload(Chapter.novel),
            selectinload(Chapter.plot_events)
        )
        .where(Chapter.id == chapter_id)
    )
    chapter = result.scalar_one_or_none()
    
    if chapter is None:
        raise NotFoundException("章节")
    
    if chapter.novel.author_id != current_user.id:
        raise UnauthorizedException("无权访问此章节")
    
    return ApiResponse.success({
        "id": chapter.id,
        "novel_id": chapter.novel_id,
        "chapter_number": chapter.chapter_number,
        "title": chapter.title,
        "content": chapter.content,
        "summary": chapter.summary,
        "status": chapter.status,
        "word_count": len(chapter.content or ""),
        "created_at": chapter.created_at,
        "updated_at": chapter.updated_at,
        "novel": {
            "id": chapter.novel.id,
            "title": chapter.novel.title
        },
        "plot_events": [
            {
                "id": pe.id,
                "event_type": pe.event_type,
                "description": pe.description
            }
            for pe in chapter.plot_events
        ]
    })


@router.put("/{chapter_id}")
async def update_chapter(
    chapter_id: int, 
    chapter: ChapterUpdate, 
    db: DBSession,
    current_user: CurrentUser
):
    """
    更新章节
    """
    result = await db.execute(
        select(Chapter)
        .options(selectinload(Chapter.novel))
        .where(Chapter.id == chapter_id)
    )
    db_chapter = result.scalar_one_or_none()
    
    if db_chapter is None:
        raise NotFoundException("章节")
    
    if db_chapter.novel.author_id != current_user.id:
        raise UnauthorizedException("无权修改此章节")
    
    update_data = chapter.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_chapter, key, value)
    
    await db.commit()
    await db.refresh(db_chapter)
    
    return ApiResponse.success(
        {
            "id": db_chapter.id,
            "title": db_chapter.title,
            "content": db_chapter.content,
            "summary": db_chapter.summary,
            "status": db_chapter.status,
            "word_count": len(db_chapter.content or ""),
            "updated_at": db_chapter.updated_at
        },
        message="章节更新成功"
    )


@router.delete("/{chapter_id}")
async def delete_chapter(
    chapter_id: int, 
    db: DBSession,
    current_user: CurrentUser
):
    """
    删除章节
    """
    result = await db.execute(
        select(Chapter)
        .options(selectinload(Chapter.novel))
        .where(Chapter.id == chapter_id)
    )
    db_chapter = result.scalar_one_or_none()
    
    if db_chapter is None:
        raise NotFoundException("章节")
    
    if db_chapter.novel.author_id != current_user.id:
        raise UnauthorizedException("无权删除此章节")
    
    await db.delete(db_chapter)
    await db.commit()
    
    return ApiResponse.success(message="章节删除成功")
