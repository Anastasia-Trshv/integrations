from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field
from .user import UserOut


class TaskCreateV1(BaseModel):
    project_id: int
    title: str = Field(..., min_length=1)
    completed: bool = False


class TaskCreateV2(TaskCreateV1):
    priority: Optional[int] = None
    user_id: Optional[int] = None


class TaskUpdateV1(BaseModel):
    title: str | None = None
    completed: bool | None = None


class TaskUpdateV2(TaskUpdateV1):
    priority: Optional[int] = None
    user_id: Optional[int] = None


class TaskOutV1(BaseModel):
    id: int
    project_id: int
    title: str
    completed: bool
    
    model_config = {
        "from_attributes": True,
    }


class TaskOutV2(TaskOutV1):
    priority: Optional[int] = None
    user_id: Optional[int] = None


# v3 output always contains optional 'user' field; when not requested it is null
class TaskOutV3(TaskOutV2):
    pass


class TaskOutV3WithUser(TaskOutV3):
    user: UserOut | None = None

