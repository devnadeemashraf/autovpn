"""App password model for storing master passwords."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class AppPassword(SQLModel, table=True):
    """Application master passwords for user access."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(description="Name/identifier for this password")
    password_hash: str = Field(description="Hashed password")
    is_active: bool = Field(default=True, description="Whether this password is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
