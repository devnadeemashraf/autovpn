"""Script to setup sample automation data for testing."""

import asyncio
from sqlmodel import Session, select

from autovpn.core.database import engine
from autovpn.models.automation import Automation, AutomationStep
from autovpn.models.user_login import UserLogin
from autovpn.models.app_password import AppPassword
from autovpn.core.security import hash_password


async def setup_sample_data():
    """Setup sample automation data."""
    with Session(engine) as session:
        # Create sample automation
        automation = Automation(
            name="Sample VPN Site",
            description="Sample automation for testing",
            base_url="https://example.com",
            is_active=True,
        )
        session.add(automation)
        session.commit()
        session.refresh(automation)

        # Create sample steps
        steps = [
            AutomationStep(
                automation_id=automation.id,
                step_order=1,
                action_type="navigate",
                input_value="https://example.com/login",
                description="Navigate to login page",
            ),
            AutomationStep(
                automation_id=automation.id,
                step_order=2,
                action_type="wait_for_element",
                xpath="//input[@name='username']",
                description="Wait for username field",
            ),
            AutomationStep(
                automation_id=automation.id,
                step_order=3,
                action_type="input",
                xpath="//input[@name='username']",
                input_value="{username}",
                description="Enter username",
            ),
            AutomationStep(
                automation_id=automation.id,
                step_order=4,
                action_type="input",
                xpath="//input[@name='password']",
                input_value="{password}",
                description="Enter password",
            ),
            AutomationStep(
                automation_id=automation.id,
                step_order=5,
                action_type="click",
                xpath="//button[@type='submit']",
                description="Click login button",
            ),
            AutomationStep(
                automation_id=automation.id,
                step_order=6,
                action_type="wait",
                wait_time=3,
                description="Wait for login to complete",
            ),
            AutomationStep(
                automation_id=automation.id,
                step_order=7,
                action_type="navigate",
                input_value="https://example.com/generate",
                description="Navigate to generation page",
            ),
        ]

        for step in steps:
            session.add(step)

        # Create sample user login
        user_login = UserLogin(
            automation_id=automation.id,
            username="testuser",
            password="testpass",
            display_name="Test User",
            is_active=True,
        )
        session.add(user_login)

        # Create sample app password
        app_password = AppPassword(
            name="test_password", password_hash=hash_password("test123"), is_active=True
        )
        session.add(app_password)

        session.commit()

        print("Sample data created successfully!")
        print(f"Automation ID: {automation.id}")
        print(f"User Login ID: {user_login.id}")
        print(f"App Password: test123")


if __name__ == "__main__":
    asyncio.run(setup_sample_data())
