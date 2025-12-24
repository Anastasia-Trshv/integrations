from __future__ import annotations

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.bucket: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable):
        identifier = request.headers.get("X-API-Key", request.client.host)
        now = time.time()
        window = settings.rate_limit_window_seconds
        max_requests = settings.rate_limit_requests

        timestamps = self.bucket.get(identifier, [])
        # prune old timestamps
        timestamps = [ts for ts in timestamps if ts > now - window]

        if len(timestamps) >= max_requests:
            retry_after = int(window - (now - timestamps[0]))
            return Response(
                status_code=429,
                headers={
                    "X-Limit-Remaining": "0",
                    "Retry-After": str(max(retry_after, 1)),
                },
                content=b"Too Many Requests",
            )

        timestamps.append(now)
        self.bucket[identifier] = timestamps

        response = await call_next(request)
        remaining = max_requests - len(timestamps)
        response.headers["X-Limit-Remaining"] = str(max(remaining, 0))
        return response

