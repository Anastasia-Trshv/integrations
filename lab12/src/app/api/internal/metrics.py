from fastapi import APIRouter, Depends
from app.core.auth import internal_auth
from app.core.storage import db


router = APIRouter(prefix="/internal", tags=["internal"], dependencies=[Depends(internal_auth)])


@router.get("/metrics")
def metrics():
    return {
        "projects": len(db.projects),
        "tasks": len(db.tasks),
        "users": len(db.users),
    }

