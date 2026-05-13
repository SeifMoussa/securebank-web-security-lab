"""SQLAlchemy database setup."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from securebank.config import get_settings


class Base(DeclarativeBase):
    """Base class for application models."""


def _make_engine(database_url: str) -> Engine:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args)


engine = _make_engine(get_settings().database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def configure_database(database_url: str) -> None:
    """Configure the module-level engine and session factory."""
    global SessionLocal, engine

    engine = _make_engine(database_url)
    SessionLocal.configure(bind=engine)


def init_db() -> None:
    """Create configured database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for request handling."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
