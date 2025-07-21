"""Database connection and table creation."""

from sqlmodel import SQLModel, create_engine, Session
from autovpn.core.config import settings

engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args=(
        {"check_same_thread": False} if "sqlite" in settings.database_url else {}
    ),
)


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session


async def create_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)
