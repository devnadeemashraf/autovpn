"""Automation models for storing website automation configurations."""

from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class AutomationStep(SQLModel, table=True):
    """Individual step in an automation workflow."""

    id: Optional[int] = Field(default=None, primary_key=True)
    automation_id: int = Field(foreign_key="automation.id")
    step_order: int = Field(description="Order of this step in the workflow")
    action_type: str = Field(
        description="Type of action: click, input, wait, navigate, etc."
    )
    xpath: Optional[str] = Field(
        default=None, description="XPath selector for the element"
    )
    css_selector: Optional[str] = Field(
        default=None, description="CSS selector for the element"
    )
    input_value: Optional[str] = Field(
        default=None, description="Value to input or text to look for"
    )
    wait_time: Optional[int] = Field(
        default=None, description="Time to wait in seconds"
    )
    success_indicator: Optional[str] = Field(
        default=None, description="XPath or text to check for success"
    )
    description: Optional[str] = Field(
        default=None, description="Human readable description of this step"
    )

    automation: Optional["Automation"] = Relationship(back_populates="steps")


class Automation(SQLModel, table=True):
    """Website automation configuration."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(description="Name of the automation workflow")
    description: Optional[str] = Field(
        default=None, description="Description of what this automation does"
    )
    base_url: str = Field(description="Base URL of the website to automate")
    is_active: bool = Field(
        default=True, description="Whether this automation is active"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    steps: List[AutomationStep] = Relationship(back_populates="automation")
    user_logins: List["UserLogin"] = Relationship(back_populates="automation")
