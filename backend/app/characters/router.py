"""
角色管理模块 - API路由
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
from app.core.redis_service import redis_service
from app.novels.models import Novel
from .models import Character
from .schemas import CharacterCreate, CharacterUpdate

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("/novel/{novel_id}")
async def get_characters_by_novel(
    novel: NovelOwner,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=50)
):
    """
    获取小说角色列表
    
    - novel_id: 小说ID
    - page: 页码
    - page_size: 每页数量
    - search: 角色名搜索
    """
    cache_key = f"novel:{novel.id}:characters:{page}:{page_size}:{search}"
    cached = await redis_service.get(cache_key)
    if cached:
        return ApiResponse.paginated(cached["items"], cached["total"], page, page_size)
    
    query = select(Character).where(Character.novel_id == novel.id)
    
    if search:
        query = query.where(Character.name.contains(search))
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    characters = result.scalars().all()
    
    items = [
        {
            "id": ch.id,
            "novel_id": ch.novel_id,
            "name": ch.name,
            "personality": ch.personality,
            "relationships": ch.relationships,
            "abilities": ch.abilities,
            "created_at": ch.created_at
        }
        for ch in characters
    ]
    
    await redis_service.set(cache_key, {"items": items, "total": total}, ttl=120)
    
    return ApiResponse.paginated(items, total, page, page_size)


@router.post("", status_code=201)
async def create_character(
    character: CharacterCreate, 
    db: DBSession,
    current_user: CurrentUser
):
    """
    创建角色
    """
    result = await db.execute(
        select(Novel).where(Novel.id == character.novel_id)
    )
    novel = result.scalar_one_or_none()
    
    if novel is None:
        raise NotFoundException("小说")
    if novel.author_id != current_user.id:
        raise UnauthorizedException("无权访问此小说")
    
    db_character = Character(**character.model_dump())
    db.add(db_character)
    await db.commit()
    await db.refresh(db_character)
    
    await redis_service.clear_pattern(f"novel:{character.novel_id}:characters:*")
    
    return ApiResponse.success(
        {
            "id": db_character.id,
            "novel_id": db_character.novel_id,
            "name": db_character.name,
            "personality": db_character.personality,
            "relationships": db_character.relationships,
            "abilities": db_character.abilities,
            "created_at": db_character.created_at
        },
        message="角色创建成功"
    )


@router.get("/{character_id}")
async def get_character(
    character_id: int, 
    db: DBSession,
    current_user: CurrentUser
):
    """
    获取角色详情
    """
    cache_key = f"character:{character_id}:detail"
    cached = await redis_service.get(cache_key)
    if cached:
        return ApiResponse.success(cached)
    
    result = await db.execute(
        select(Character)
        .options(selectinload(Character.novel))
        .where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()
    
    if character is None:
        raise NotFoundException("角色")
    
    if character.novel.author_id != current_user.id:
        raise UnauthorizedException("无权访问此角色")
    
    data = {
        "id": character.id,
        "novel_id": character.novel_id,
        "name": character.name,
        "personality": character.personality,
        "relationships": character.relationships,
        "abilities": character.abilities,
        "created_at": character.created_at,
        "novel": {
            "id": character.novel.id,
            "title": character.novel.title
        }
    }
    
    await redis_service.set(cache_key, data, ttl=300)
    
    return ApiResponse.success(data)


@router.put("/{character_id}")
async def update_character(
    character_id: int, 
    character: CharacterUpdate, 
    db: DBSession,
    current_user: CurrentUser
):
    """
    更新角色
    """
    result = await db.execute(
        select(Character)
        .options(selectinload(Character.novel))
        .where(Character.id == character_id)
    )
    db_character = result.scalar_one_or_none()
    
    if db_character is None:
        raise NotFoundException("角色")
    
    if db_character.novel.author_id != current_user.id:
        raise UnauthorizedException("无权修改此角色")
    
    update_data = character.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_character, key, value)
    
    await db.commit()
    await db.refresh(db_character)
    
    await redis_service.delete(f"character:{character_id}:detail")
    await redis_service.clear_pattern(f"novel:{db_character.novel_id}:characters:*")
    
    return ApiResponse.success(
        {
            "id": db_character.id,
            "name": db_character.name,
            "personality": db_character.personality,
            "relationships": db_character.relationships,
            "abilities": db_character.abilities
        },
        message="角色更新成功"
    )


@router.delete("/{character_id}")
async def delete_character(
    character_id: int, 
    db: DBSession,
    current_user: CurrentUser
):
    """
    删除角色
    """
    result = await db.execute(
        select(Character)
        .options(selectinload(Character.novel))
        .where(Character.id == character_id)
    )
    db_character = result.scalar_one_or_none()
    
    if db_character is None:
        raise NotFoundException("角色")
    
    if db_character.novel.author_id != current_user.id:
        raise UnauthorizedException("无权删除此角色")
    
    novel_id = db_character.novel_id
    
    await db.delete(db_character)
    await db.commit()
    
    await redis_service.delete(f"character:{character_id}:detail")
    await redis_service.clear_pattern(f"novel:{novel_id}:characters:*")
    
    return ApiResponse.success(message="角色删除成功")
