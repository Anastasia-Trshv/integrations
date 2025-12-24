from src.core.storage import db
from src.schemas.task import TaskCreateV1, TaskUpdateV1, TaskOutV1

def create_task(data: dict) -> TaskOutV1:
    payload = TaskCreateV1(**data)
    if payload.project_id not in db.projects:
        raise ValueError("Project not found")
        
    task = db.create_task(project_id=payload.project_id, title=payload.title, completed=payload.completed)
    return TaskOutV1.model_validate(task)

def list_tasks(data: dict) -> list[TaskOutV1]:
    project_id = data.get("project_id")
    tasks = list(db.tasks.values())
    if project_id is not None:
        tasks = [t for t in tasks if t.project_id == int(project_id)]
    return [TaskOutV1.model_validate(t) for t in tasks]

def get_task(data: dict) -> TaskOutV1:
    task_id = data.get("id")
    if task_id is None:
        raise ValueError("id is required")
        
    task = db.tasks.get(int(task_id))
    if not task:
        raise ValueError("Task not found")
    return TaskOutV1.model_validate(task)

def update_task(data: dict) -> TaskOutV1:
    task_id = data.get("id")
    if task_id is None:
        raise ValueError("id is required")
        
    payload = TaskUpdateV1(**data)
    task = db.tasks.get(int(task_id))
    if not task:
        raise ValueError("Task not found")
        
    if payload.title is not None:
        task.title = payload.title
    if payload.completed is not None:
        task.completed = payload.completed
    db.tasks[int(task_id)] = task
    return TaskOutV1.model_validate(task)

def delete_task(data: dict) -> None:
    task_id = data.get("id")
    if task_id is None:
        raise ValueError("id is required")
        
    tid = int(task_id)
    if tid not in db.tasks:
        raise ValueError("Task not found")
    del db.tasks[tid]
    return None

