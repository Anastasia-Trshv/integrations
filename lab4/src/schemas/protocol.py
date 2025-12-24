from typing import Any, Optional, Dict
from pydantic import BaseModel, Field

class RequestMessage(BaseModel):
    id: str
    version: str
    action: str
    data: Dict[str, Any] = Field(default_factory=dict)
    auth: Optional[str] = None

class ResponseMessage(BaseModel):
    correlation_id: str
    status: str  # "ok" or "error"
    data: Optional[Any] = None
    error: Optional[str] = None

