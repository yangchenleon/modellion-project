from __future__ import annotations

import logging
from typing import Any

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import VersionInfo, get_settings
from .db import session_scope
from .models import User
from .security import hash_password, verify_password
from .routers import auth as auth_router
from .routers import products as products_router
from .routers import images as images_router
from .routers import imports as imports_router
from .routers import stats as stats_router


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ]
    )
    logging.basicConfig(level=logging.INFO)


settings = get_settings()
configure_logging()
log = structlog.get_logger()

app = FastAPI(
    title="数据库后台管理系统",
    version=VersionInfo(version="0.1.0", env=settings.ENV).version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS for local dev and simple deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    # Initialize or migrate admin user
    with session_scope() as session:
        username = settings.ADMIN_USERNAME
        user: User | None = session.query(User).filter(User.username == username).one_or_none()
        if user is None:
            user = User(
                username=username,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                role=settings.ADMIN_ROLE or "admin",
            )
            session.add(user)
            log.info("admin_user_initialized", username=username)
        else:
            # migrate hash if current password doesn't verify (e.g., scheme changed)
            if not verify_password(settings.ADMIN_PASSWORD, user.password_hash):
                user.password_hash = hash_password(settings.ADMIN_PASSWORD)
                session.add(user)
                log.info("admin_password_migrated", username=username)


# Routers
app.include_router(auth_router.router, prefix="/api/auth", tags=["认证"])
app.include_router(products_router.router, prefix="/api/products", tags=["产品"])
app.include_router(images_router.router, prefix="/api/images", tags=["图片"])
app.include_router(imports_router.router, prefix="/api/import", tags=["导入"])
app.include_router(stats_router.router, prefix="/api", tags=["统计与健康"])


@app.get("/version", response_model=VersionInfo, tags=["统计与健康"])
def version() -> Any:
    return VersionInfo(name="modellion-admin", version="0.1.0", env=settings.ENV)
