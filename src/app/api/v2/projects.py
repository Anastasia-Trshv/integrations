from fastapi import APIRouter, HTTPException, Request, Response, Header
from app.core.storage import db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut


router = APIRouter(prefix="/projects", tags=["projects v2"])


@router.post("/", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, request: Request, response: Response, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    if idempotency_key:
        k = f"{request.url.path}:{idempotency_key}"
        existing_id = db.idempotency.get(k)
        if existing_id is not None and existing_id in db.projects:
            return db.projects[existing_id]
    project = db.create_project(name=payload.name, description=payload.description or "")
    response.headers["X-Resource-Id"] = str(project.id)
    if idempotency_key:
        db.idempotency[f"{request.url.path}:{idempotency_key}"] = project.id
    return project


@router.get("/", response_model=list[ProjectOut])
def list_projects():
    return list(db.projects.values())


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int):
    project = db.projects.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate):
    project = db.projects.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    db.projects[project_id] = project
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int):
    if project_id not in db.projects:
        raise HTTPException(status_code=404, detail="Project not found")
    db.tasks = {tid: t for tid, t in db.tasks.items() if t.project_id != project_id}
    del db.projects[project_id]
    return None

