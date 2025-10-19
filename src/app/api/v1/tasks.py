from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request, Response, Header
from app.core.storage import db
from app.schemas.task import TaskCreateV1, TaskUpdateV1, TaskOutV1


router = APIRouter(prefix="/tasks", tags=["tasks v1"])


@router.post("/", response_model=TaskOutV1, status_code=201)
def create_task(payload: TaskCreateV1, request: Request, response: Response, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    if payload.project_id not in db.projects:
        raise HTTPException(status_code=404, detail="Project not found")
    if idempotency_key:
        k = f"{request.url.path}:{idempotency_key}"
        existing_id = db.idempotency.get(k)
        if existing_id is not None and existing_id in db.tasks:
            return db.tasks[existing_id]
    task = db.create_task(project_id=payload.project_id, title=payload.title, completed=payload.completed)
    response.headers["X-Resource-Id"] = str(task.id)
    if idempotency_key:
        db.idempotency[f"{request.url.path}:{idempotency_key}"] = task.id
    return task


@router.get("/", response_model=list[TaskOutV1])
def list_tasks(project_id: Optional[int] = Query(default=None)):
    tasks = list(db.tasks.values())
    if project_id is not None:
        tasks = [t for t in tasks if t.project_id == project_id]
    return tasks


@router.get("/{task_id}", response_model=TaskOutV1)
def get_task(task_id: int):
    task = db.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskOutV1)
def update_task(task_id: int, payload: TaskUpdateV1):
    task = db.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if payload.title is not None:
        task.title = payload.title
    if payload.completed is not None:
        task.completed = payload.completed
    db.tasks[task_id] = task
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in db.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del db.tasks[task_id]
    return None

