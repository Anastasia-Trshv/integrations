from fastapi import APIRouter, HTTPException, Request, Response, Header
from app.core.storage import db
from app.schemas.user import UserCreate, UserUpdate, UserOut


router = APIRouter(prefix="/users", tags=["users v2"])


@router.post("/", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, request: Request, response: Response, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    if idempotency_key:
        k = f"{request.url.path}:{idempotency_key}"
        existing_id = db.idempotency.get(k)
        if existing_id is not None and existing_id in db.users:
            return db.users[existing_id]
    user = db.create_user(name=payload.name, email=str(payload.email))
    response.headers["X-Resource-Id"] = str(user.id)
    if idempotency_key:
        db.idempotency[f"{request.url.path}:{idempotency_key}"] = user.id
    return user


@router.get("/", response_model=list[UserOut])
def list_users():
    return list(db.users.values())


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    user = db.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate):
    user = db.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        user.email = str(payload.email)
    db.users[user_id] = user
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id not in db.users:
        raise HTTPException(status_code=404, detail="User not found")
    # detach user from tasks
    for t in db.tasks.values():
        if t.user_id == user_id:
            t.user_id = None
    del db.users[user_id]
    return None

