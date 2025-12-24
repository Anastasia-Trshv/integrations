from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.auth import api_key_auth
from app.middlewares.rate_limit import RateLimitMiddleware
from app.middlewares.idempotency import IdempotencyMiddleware
from app.api.v1.projects import router as projects_v1
from app.api.v1.tasks import router as tasks_v1
from app.api.v2.projects import router as projects_v2
from app.api.v2.tasks import router as tasks_v2
from app.api.v2.users import router as users_v2
from app.api.v3.tasks import router as tasks_v3
from app.api.internal.metrics import router as internal_metrics


def create_app() -> FastAPI:
    app = FastAPI(title="Tasks API", version="2.0.0", docs_url="/docs", redoc_url="/redoc")

    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(IdempotencyMiddleware)

    app.include_router(projects_v1, prefix="/api/v1", dependencies=[Depends(api_key_auth)])
    app.include_router(tasks_v1, prefix="/api/v1", dependencies=[Depends(api_key_auth)])
    app.include_router(projects_v2, prefix="/api/v2", dependencies=[Depends(api_key_auth)])
    app.include_router(tasks_v2, prefix="/api/v2", dependencies=[Depends(api_key_auth)])
    app.include_router(users_v2, prefix="/api/v2", dependencies=[Depends(api_key_auth)])
    app.include_router(tasks_v3, prefix="/api/v3", dependencies=[Depends(api_key_auth)])
    app.include_router(internal_metrics)

    @app.get("/health")
    def health():
        return JSONResponse({"status": "ok"})

    return app


app = create_app()

