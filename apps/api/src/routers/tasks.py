from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..deps import get_db
from ..models import Task
from ..models.task import TaskStatus, TaskAction
from ..schemas.task import TaskCreate, TaskResponse
from ..services.tasks import TaskService

router = APIRouter()

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):
    """Создает новую задачу."""
    service = TaskService(db)
    return await service.create_task(task_data)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Получает информацию о задаче."""
    service = TaskService(db)
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[TaskStatus] = Query(None),
    action: Optional[TaskAction] = Query(None),
    node_id: Optional[int] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Список задач с фильтрацией."""
    service = TaskService(db)
    return await service.list_tasks(status, action, node_id, limit, offset)

@router.post("/bulk")
async def create_bulk_tasks(
    tasks_data: List[TaskCreate],
    db: Session = Depends(get_db)
):
    """Создает несколько задач одновременно."""
    service = TaskService(db)
    return await service.create_bulk_tasks(tasks_data)
