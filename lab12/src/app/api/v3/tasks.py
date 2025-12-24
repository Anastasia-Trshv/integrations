from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.core.storage import db
from app.schemas.task import TaskOutV3, TaskOutV3WithUser


router = APIRouter(prefix="/tasks", tags=["tasks v3"])


@router.get("/", response_model=list[TaskOutV3])
def list_tasks(
    project_id: Optional[int] = Query(default=None),
    completed: Optional[bool] = Query(default=None),
    priority_min: Optional[int] = Query(default=None, ge=0),
    priority_max: Optional[int] = Query(default=None, ge=0),
    user_id: Optional[int] = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    include: Optional[str] = Query(default=None, description="Comma-separated fields, e.g. user"),
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

    total = len(tasks)
    tasks = tasks[offset : offset + limit]

    if include:
        parts = {p.strip() for p in include.split(",") if p.strip()}
        if "user" in parts:
            enriched: list[TaskOutV3WithUser] = []
            for t in tasks:
                u = db.users.get(t.user_id) if t.user_id is not None else None
                enriched.append(TaskOutV3WithUser(**t.__dict__, user=u))
            return enriched
    return tasks

