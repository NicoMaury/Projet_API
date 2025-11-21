"""Database utilities for PostgreSQL access."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import get_settings


settings = get_settings()

engine = create_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()


def init_db() -> None:
    """Create database tables if they don't already exist."""

    import app.models.db  # noqa: F401 - ensure models are imported

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency providing a scoped SQLAlchemy session."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
