from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import settings
from app.core.storage import db


class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # On successful creation, store mapping via response header if present
        if request.method == "POST" and response.status_code in (200, 201):
            key = request.headers.get(settings.idempotency_header)
            created_id = response.headers.get("X-Resource-Id")
            if key and created_id:
                namespaced = f"{request.url.path}:{key}"
                if namespaced not in db.idempotency:
                    try:
                        db.idempotency[namespaced] = int(created_id)
                    except Exception:
                        pass
        return response

