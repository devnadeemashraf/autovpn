"""User login model for storing credentials for each automation."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class UserLogin(SQLModel, table=True):
    """User login credentials for automation workflows."""

    id: Optional[int] = Field(default=None, primary_key=True)
    automation_id: int = Field(foreign_key="automation.id")
    username: str = Field(description="Username for the automation")
    password: str = Field(description="Encrypted password for the automation")
    display_name: Optional[str] = Field(
        default=None, description="Display name for the user"
    )
    is_active: bool = Field(default=True, description="Whether this login is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    automation: Optional["Automation"] = Relationship(back_populates="user_logins")
