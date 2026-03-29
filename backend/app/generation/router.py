"""
章节生成API路由
"""
import logging
import asyncio
from functools import wraps
from fastapi import APIRouter, BackgroundTasks
from sqlalchemy import select

from app.core.response import ApiResponse
from app.core.database import DBSession, AsyncSessionLocal
from app.core.exceptions import NotFoundException
from app.core.dependencies import NovelOwner
from app.generation.service import ChapterGenerationService
from app.chapters.models import Chapter
from app.agents.models import AgentTaskRecord
from app.agents.base import TaskType, TaskStatus

router = APIRouter(prefix="/generation", tags=["generation"])
logger = logging.getLogger(__name__)

_generation_locks: dict = {}


@router.post("/novels/{novel_id}/chapters/{chapter_number}")
async def generate_chapter(
    novel: NovelOwner,
    db: DBSession,
    background_tasks: BackgroundTasks,
    chapter_number: int,
    target_length: int = 3000,
    style: str = "narrative"
):
    """
    生成章节（异步）
    
    - chapter_number: 章节号
    - target_length: 目标字数
    - style: 写作风格
    """
    logger.info(f"Request to generate chapter {chapter_number} for novel {novel.id}")
    
    lock_key = f"{novel.id}_{chapter_number}"
    if lock_key in _generation_locks and _generation_locks[lock_key]:
        return ApiResponse.error(
            code="GEN_001",
            message="章节正在生成中，请稍后再试",
            status_code=409
        )
    
    result = await db.execute(
        select(Chapter).where(
            Chapter.novel_id == novel.id,
            Chapter.chapter_number == chapter_number
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing and existing.status == "generating":
        return ApiResponse.error(
            code="GEN_001",
            message="章节正在生成中",
            status_code=409
        )
    
    task_record = AgentTaskRecord(
        task_id=f"gen_{novel.id}_{chapter_number}",
        novel_id=novel.id,
        task_type=TaskType.GENERATE_CHAPTER.value,
        status=TaskStatus.PENDING.value,
        parameters={
            "chapter_number": chapter_number,
            "target_length": target_length,
            "style": style
        }
    )
    db.add(task_record)
    await db.commit()
    
    if not existing:
        chapter = Chapter(
            novel_id=novel.id,
            chapter_number=chapter_number,
            title=f"第{chapter_number}章",
            content="",
            status="generating"
        )
        db.add(chapter)
        await db.commit()
    else:
        existing.status = "generating"
        await db.commit()
    
    _generation_locks[lock_key] = True
    
    background_tasks.add_task(
        _generate_chapter_task,
        novel.id, chapter_number, target_length, style, task_record.task_id
    )
    
    return ApiResponse.success({
        "task_id": task_record.task_id,
        "chapter_number": chapter_number,
        "status": "generating",
        "message": "章节生成任务已提交"
    })


async def _generate_chapter_task(
    novel_id: int,
    chapter_number: int,
    target_length: int,
    style: str,
    task_id: str
):
    """后台任务：生成章节"""
    async with AsyncSessionLocal() as db:
        lock_key = f"{novel_id}_{chapter_number}"
        
        try:
            result = await db.execute(
                select(AgentTaskRecord).where(AgentTaskRecord.task_id == task_id)
            )
            task_record = result.scalar_one_or_none()
            
            if task_record:
                task_record.status = TaskStatus.IN_PROGRESS.value
                await db.commit()
            
            service = ChapterGenerationService(db, novel_id)
            result_data = await _generate_with_retry(
                service, chapter_number, target_length, style, max_retries=3
            )
            
            if task_record:
                task_record.status = TaskStatus.COMPLETED.value if result_data["success"] else TaskStatus.FAILED.value
                task_record.result = result_data
                if not result_data["success"]:
                    task_record.error = result_data.get("error", "Unknown error")
                await db.commit()
            
            logger.info(f"Chapter generation task {task_id} completed: {result_data['success']}")
            
        except Exception as e:
            logger.error(f"Chapter generation task {task_id} failed: {e}")
            try:
                result = await db.execute(
                    select(AgentTaskRecord).where(AgentTaskRecord.task_id == task_id)
                )
                task_record = result.scalar_one_or_none()
                if task_record:
                    task_record.status = TaskStatus.FAILED.value
                    task_record.error = str(e)
                    await db.commit()
            except Exception as db_error:
                logger.error(f"Failed to update task status: {db_error}")
        finally:
            _generation_locks[lock_key] = False


async def _generate_with_retry(
    service: ChapterGenerationService,
    chapter_number: int,
    target_length: int,
    style: str,
    max_retries: int = 3
) -> dict:
    """带重试的章节生成"""
    last_error = None
    for attempt in range(max_retries):
        try:
            result = await service.generate_chapter(
                chapter_number=chapter_number,
                target_length=target_length,
                style=style
            )
            if result["success"]:
                return result
            last_error = result.get("error", "Unknown error")
            logger.warning(f"Generation attempt {attempt + 1} failed: {last_error}")
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Generation attempt {attempt + 1} raised error: {e}")
        
        if attempt < max_retries - 1:
            await asyncio.sleep(2.0 * (attempt + 1))
    
    return {"success": False, "error": f"Failed after {max_retries} retries: {last_error}"}


@router.post("/novels/{novel_id}/chapters/{chapter_id}/regenerate")
async def regenerate_chapter(
    novel: NovelOwner,
    db: DBSession,
    background_tasks: BackgroundTasks,
    chapter_id: int,
    feedback: str = None
):
    """
    重新生成章节
    
    - chapter_id: 章节ID
    - feedback: 反馈意见
    """
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.novel_id == novel.id
        )
    )
    chapter = result.scalar_one_or_none()
    
    if not chapter:
        raise NotFoundException("章节")
    
    lock_key = f"{novel.id}_{chapter.chapter_number}"
    if lock_key in _generation_locks and _generation_locks[lock_key]:
        return ApiResponse.error(
            code="GEN_002",
            message="章节正在生成中，无法重新生成",
            status_code=409
        )
    
    task_record = AgentTaskRecord(
        task_id=f"regen_{novel.id}_{chapter.chapter_number}",
        novel_id=novel.id,
        chapter_id=chapter_id,
        task_type=TaskType.GENERATE_CHAPTER.value,
        status=TaskStatus.PENDING.value,
        parameters={
            "chapter_number": chapter.chapter_number,
            "feedback": feedback
        }
    )
    db.add(task_record)
    
    chapter.status = "generating"
    await db.commit()
    
    _generation_locks[lock_key] = True
    
    background_tasks.add_task(
        _regenerate_chapter_task,
        novel.id, chapter_id, chapter.chapter_number, feedback, task_record.task_id
    )
    
    return ApiResponse.success({
        "task_id": task_record.task_id,
        "chapter_id": chapter_id,
        "status": "regenerating",
        "message": "章节重新生成任务已提交"
    })


async def _regenerate_chapter_task(
    novel_id: int,
    chapter_id: int,
    chapter_number: int,
    feedback: str,
    task_id: str
):
    """后台任务：重新生成章节"""
    async with AsyncSessionLocal() as db:
        lock_key = f"{novel_id}_{chapter_number}"
        
        try:
            result = await db.execute(
                select(AgentTaskRecord).where(AgentTaskRecord.task_id == task_id)
            )
            task_record = result.scalar_one_or_none()
            
            if task_record:
                task_record.status = TaskStatus.IN_PROGRESS.value
                await db.commit()
            
            service = ChapterGenerationService(db, novel_id)
            result_data = await _regenerate_with_retry(
                service, chapter_id, feedback, max_retries=3
            )
            
            if task_record:
                task_record.status = TaskStatus.COMPLETED.value if result_data["success"] else TaskStatus.FAILED.value
                task_record.result = result_data
                if not result_data["success"]:
                    task_record.error = result_data.get("error", "Unknown error")
                await db.commit()
            
        except Exception as e:
            logger.error(f"Chapter regeneration task {task_id} failed: {e}")
            try:
                result = await db.execute(
                    select(AgentTaskRecord).where(AgentTaskRecord.task_id == task_id)
                )
                task_record = result.scalar_one_or_none()
                if task_record:
                    task_record.status = TaskStatus.FAILED.value
                    task_record.error = str(e)
                    await db.commit()
            except Exception as db_error:
                logger.error(f"Failed to update task status: {db_error}")
        finally:
            _generation_locks[lock_key] = False


async def _regenerate_with_retry(
    service: ChapterGenerationService,
    chapter_id: int,
    feedback: str,
    max_retries: int = 3
) -> dict:
    """带重试的章节重新生成"""
    last_error = None
    for attempt in range(max_retries):
        try:
            result = await service.regenerate_chapter(
                chapter_id=chapter_id,
                feedback=feedback
            )
            if result["success"]:
                return result
            last_error = result.get("error", "Unknown error")
            logger.warning(f"Regeneration attempt {attempt + 1} failed: {last_error}")
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Regeneration attempt {attempt + 1} raised error: {e}")
        
        if attempt < max_retries - 1:
            await asyncio.sleep(2.0 * (attempt + 1))
    
    return {"success": False, "error": f"Failed after {max_retries} retries: {last_error}"}


@router.get("/novels/{novel_id}/tasks")
async def get_generation_tasks(
    novel: NovelOwner,
    db: DBSession,
    status: str = None,
    page: int = 1,
    page_size: int = 20
):
    """
    获取生成任务列表
    
    - status: 任务状态筛选
    - page: 页码
    - page_size: 每页数量
    """
    from sqlalchemy import func
    
    query = select(AgentTaskRecord).where(
        AgentTaskRecord.novel_id == novel.id
    )
    
    if status:
        query = query.where(AgentTaskRecord.status == status)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.order_by(AgentTaskRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    items = [
        {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "chapter_id": task.chapter_id,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error": task.error
        }
        for task in tasks
    ]
    
    return ApiResponse.paginated(items, total, page, page_size)


@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    db: DBSession
):
    """
    获取任务状态
    """
    result = await db.execute(
        select(AgentTaskRecord).where(AgentTaskRecord.task_id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise NotFoundException("任务")
    
    return ApiResponse.success({
        "task_id": task.task_id,
        "task_type": task.task_type,
        "novel_id": task.novel_id,
        "chapter_id": task.chapter_id,
        "status": task.status,
        "parameters": task.parameters,
        "result": task.result,
        "error": task.error,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None
    })
