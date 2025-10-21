from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import get_settings

Base = declarative_base()


def _database_url() -> str:
    settings = get_settings()
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    # default to sqlite file
    path = settings.DATABASE_PATH or "/data/app.db"
    return f"sqlite+pysqlite:///{path}"


_engine = create_engine(_database_url(), future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False, future=True)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
