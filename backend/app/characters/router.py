"""
角色管理模块 - API路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.response import ApiResponse
from app.core.exceptions import NotFoundException, UnauthorizedException
from app.core.auth import get_current_user
from app.auth.models import User
from app.novels.models import Novel
from .models import Character
from .schemas import CharacterCreate, CharacterUpdate

router = APIRouter(prefix="/characters", tags=["characters"])


def check_novel_ownership(db: Session, novel_id: int, user_id: int) -> Novel:
    """检查小说所有权"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if novel is None:
        raise NotFoundException("小说")
    if novel.author_id != user_id:
        raise UnauthorizedException("无权访问此小说")
    return novel


@router.get("/novel/{novel_id}")
def get_characters_by_novel(
    novel_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取小说角色列表
    
    - novel_id: 小说ID
    - page: 页码
    - page_size: 每页数量
    - search: 角色名搜索
    """
    check_novel_ownership(db, novel_id, current_user.id)
    
    query = db.query(Character).filter(Character.novel_id == novel_id)
    
    if search:
        query = query.filter(Character.name.contains(search))
    
    total = query.count()
    characters = query.offset((page - 1) * page_size).limit(page_size).all()
    
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
    
    return ApiResponse.paginated(items, total, page, page_size)


@router.post("", status_code=201)
def create_character(
    character: CharacterCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建角色
    """
    check_novel_ownership(db, character.novel_id, current_user.id)
    
    db_character = Character(**character.dict())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    
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
def get_character(
    character_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取角色详情
    """
    character = db.query(Character).filter(Character.id == character_id).first()
    if character is None:
        raise NotFoundException("角色")
    
    check_novel_ownership(db, character.novel_id, current_user.id)
    
    return ApiResponse.success({
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
    })


@router.put("/{character_id}")
def update_character(
    character_id: int, 
    character: CharacterUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新角色
    """
    db_character = db.query(Character).filter(Character.id == character_id).first()
    if db_character is None:
        raise NotFoundException("角色")
    
    check_novel_ownership(db, db_character.novel_id, current_user.id)
    
    update_data = character.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_character, key, value)
    
    db.commit()
    db.refresh(db_character)
    
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
def delete_character(
    character_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除角色
    """
    db_character = db.query(Character).filter(Character.id == character_id).first()
    if db_character is None:
        raise NotFoundException("角色")
    
    check_novel_ownership(db, db_character.novel_id, current_user.id)
    
    db.delete(db_character)
    db.commit()
    
    return ApiResponse.success(message="角色删除成功")
