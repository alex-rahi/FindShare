from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import get_settings
from app.db import engine
from app.errors import AppError, app_error_handler
from app.routers import auth, catalog

settings = get_settings()
logger = getLogger("findshare")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.seed_on_startup and settings.app_env != "test":
        from app.seed import seed_if_needed

        seed_if_needed()
    yield


app = FastAPI(
    title="FindShare API",
    description=(
        "Social product-discovery platform (Phase 1 local foundation). "
        "Registration is invitation-only by default."
    ),
    version="0.1.0",
    lifespan=lifespan,
)
app.add_exception_handler(AppError, app_error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(catalog.router)

_OPEN_PATHS = {"/health", "/ready", "/docs", "/openapi.json", "/redoc"}


@app.middleware("http")
async def maintenance_gate(request: Request, call_next):
    if request.url.path in _OPEN_PATHS:
        return await call_next(request)
    if settings.maintenance_mode:
        return JSONResponse(
            {"detail": "FindShare is in maintenance mode.", "code": "MAINTENANCE"},
            status_code=503,
        )
    return await call_next(request)


@app.get("/health")
def health():
    return {"status": "ok", "service": "findshare-api", "phase": 1, "env": settings.app_env}


@app.get("/ready")
def ready():
    from fastapi.responses import JSONResponse

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        logger.exception("database not ready")
        return JSONResponse({"status": "unavailable", "code": "DB_UNAVAILABLE"}, status_code=503)
    try:
        from app.security import get_redis

        get_redis().ping()
    except Exception:
        logger.exception("redis not ready")
        return JSONResponse({"status": "unavailable", "code": "REDIS_UNAVAILABLE"}, status_code=503)
    return {"status": "ready"}
