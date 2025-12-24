import logging
from src.core.storage import db
from src.schemas.user import UserCreate, UserUpdate, UserOut

logger = logging.getLogger(__name__)

def create_user(data: dict) -> UserOut:
    payload = UserCreate(**data)
    # Semantic idempotency: check if user with this email already exists
    email = str(payload.email)
    for user in db.users.values():
        if user.email == email:
            # Return existing user instead of creating duplicate
            logger.info(f"User with email {email} already exists, returning existing user")
            return UserOut.model_validate(user)
    
    # Create new user if email doesn't exist
    user = db.create_user(name=payload.name, email=email)
    return UserOut.model_validate(user)

def list_users(data: dict) -> list[UserOut]:
    return [UserOut.model_validate(u) for u in db.users.values()]

def get_user(data: dict) -> UserOut:
    user_id = data.get("id")
    if user_id is None:
        raise ValueError("id is required")
    
    user = db.users.get(int(user_id))
    if not user:
        raise ValueError("User not found")
    return UserOut.model_validate(user)

def update_user(data: dict) -> UserOut:
    user_id = data.get("id")
    if user_id is None:
        raise ValueError("id is required")
        
    payload = UserUpdate(**data)
    
    user = db.users.get(int(user_id))
    if not user:
        raise ValueError("User not found")
        
    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        user.email = str(payload.email)
        
    db.users[int(user_id)] = user
    return UserOut.model_validate(user)

def delete_user(data: dict) -> None:
    user_id = data.get("id")
    if user_id is None:
        raise ValueError("id is required")
    
    uid = int(user_id)
    if uid not in db.users:
        raise ValueError("User not found")
    
    # Detach user from tasks
    for t in db.tasks.values():
        if t.user_id == uid:
            t.user_id = None
            
    del db.users[uid]
    return None

