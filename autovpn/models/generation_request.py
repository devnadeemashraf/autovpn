"""Generation request model for tracking automation runs."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class GenerationRequest(SQLModel, table=True):
    """Track automation generation requests."""

    id: Optional[int] = Field(default=None, primary_key=True)
    automation_id: int = Field(foreign_key="automation.id")
    user_login_id: int = Field(foreign_key="userlogin.id")
    num_profiles: int = Field(description="Number of profiles requested")
    status: str = Field(
        default="pending", description="Status: pending, running, completed, failed"
    )
    result_file: Optional[str] = Field(default=None, description="Path to result file")
    error_message: Optional[str] = Field(
        default=None, description="Error message if failed"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(
        default=None, description="When the request was completed"
    )
