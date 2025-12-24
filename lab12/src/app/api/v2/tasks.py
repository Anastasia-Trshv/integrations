from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request, Response, Header
from app.core.storage import db
from app.schemas.task import TaskCreateV2, TaskUpdateV2, TaskOutV2


router = APIRouter(prefix="/tasks", tags=["tasks v2"])


@router.post("/", response_model=TaskOutV2, status_code=201)
def create_task(payload: TaskCreateV2, request: Request, response: Response, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    if payload.project_id not in db.projects:
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.user_id is not None and payload.user_id not in db.users:
        raise HTTPException(status_code=404, detail="User not found")
    if idempotency_key:
        k = f"{request.url.path}:{idempotency_key}"
        existing_id = db.idempotency.get(k)
        if existing_id is not None and existing_id in db.tasks:
            return db.tasks[existing_id]
    task = db.create_task_v2(
        project_id=payload.project_id,
        title=payload.title,
        completed=payload.completed,
        priority=payload.priority,
        user_id=payload.user_id,
    )
    response.headers["X-Resource-Id"] = str(task.id)
    if idempotency_key:
        db.idempotency[f"{request.url.path}:{idempotency_key}"] = task.id
    return task


@router.get("/", response_model=list[TaskOutV2])
def list_tasks(
    project_id: Optional[int] = Query(default=None),
    completed: Optional[bool] = Query(default=None),
    priority_min: Optional[int] = Query(default=None, ge=0),
    priority_max: Optional[int] = Query(default=None, ge=0),
    user_id: Optional[int] = Query(default=None),
):
    tasks = list(db.tasks.values())
    if project_id is not None:
        tasks = [t for t in tasks if t.project_id == project_id]
    if completed is not None:
        tasks = [t for t in tasks if t.completed == completed]
    if priority_min is not None:
        tasks = [t for t in tasks if t.priority is not None and t.priority >= priority_min]
    if priority_max is not None:
        tasks = [t for t in tasks if t.priority is not None and t.priority <= priority_max]
    if user_id is not None:
        tasks = [t for t in tasks if t.user_id == user_id]
    return tasks


@router.get("/{task_id}", response_model=TaskOutV2)
def get_task(task_id: int):
    task = db.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskOutV2)
def update_task(task_id: int, payload: TaskUpdateV2):
    task = db.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if payload.title is not None:
        task.title = payload.title
    if payload.completed is not None:
        task.completed = payload.completed
    if payload.priority is not None:
        task.priority = payload.priority
    if payload.user_id is not None:
        if payload.user_id not in db.users:
            raise HTTPException(status_code=404, detail="User not found")
        task.user_id = payload.user_id
    db.tasks[task_id] = task
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in db.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del db.tasks[task_id]
    return None

