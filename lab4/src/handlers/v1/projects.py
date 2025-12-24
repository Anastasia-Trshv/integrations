from src.core.storage import db
from src.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut

def create_project(data: dict) -> ProjectOut:
    payload = ProjectCreate(**data)
    project = db.create_project(name=payload.name, description=payload.description or "")
    return ProjectOut.model_validate(project)

def list_projects(data: dict) -> list[ProjectOut]:
    return [ProjectOut.model_validate(p) for p in db.projects.values()]

def get_project(data: dict) -> ProjectOut:
    project_id = data.get("id")
    if project_id is None:
        raise ValueError("id is required")
    project = db.projects.get(int(project_id))
    if not project:
        raise ValueError("Project not found")
    return ProjectOut.model_validate(project)

def update_project(data: dict) -> ProjectOut:
    project_id = data.get("id")
    if project_id is None:
        raise ValueError("id is required")
    payload = ProjectUpdate(**data)
    
    project = db.projects.get(int(project_id))
    if not project:
        raise ValueError("Project not found")
        
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    db.projects[int(project_id)] = project
    return ProjectOut.model_validate(project)

def delete_project(data: dict) -> None:
    project_id = data.get("id")
    if project_id is None:
        raise ValueError("id is required")
    
    pid = int(project_id)
    if pid not in db.projects:
        raise ValueError("Project not found")
    
    # cascade delete tasks
    # Note: we need to handle this carefully as we are modifying the dictionary while iterating if we were deleting in place, 
    # but here we are creating a new dict.
    # However, db.tasks is a global dict. We should iterate a copy or use comprehension.
    # In Lab 3 it was: db.tasks = {tid: t for tid, t in db.tasks.items() if t.project_id != project_id}
    # But db.tasks is a field in InMemoryDB dataclass.
    
    new_tasks = {tid: t for tid, t in db.tasks.items() if t.project_id != pid}
    # We need to update the db object. Since it's a dataclass field, we can assign it.
    # But wait, db is an instance. 
    # Check storage.py: tasks: Dict[int, Task]
    
    # To modify the dictionary in place to avoid replacing the reference if other threads hold it (though we are single threaded mostly)
    # A safe way is to identify keys to delete.
    to_delete = [tid for tid, t in db.tasks.items() if t.project_id == pid]
    for tid in to_delete:
        del db.tasks[tid]
        
    del db.projects[pid]
    return None

