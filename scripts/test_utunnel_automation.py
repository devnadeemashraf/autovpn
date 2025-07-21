"""Test script for UTunnel automation."""

import asyncio
from sqlmodel import Session, select

from autovpn.core.database import engine
from autovpn.models.automation import Automation
from autovpn.models.user_login import UserLogin
from autovpn.automation.engine import AutomationEngine


async def test_utunnel_automation():
    """Test the UTunnel automation workflow."""
    with Session(engine) as session:
        # Get UTunnel automation
        statement = select(Automation).where(Automation.name == "UTUNNEL")
        automation = session.exec(statement).first()

        if not automation:
            print(
                "UTunnel automation not found. Please run create_utunnel_automation.py first."
            )
            return

        # Get a user login for this automation
        statement = select(UserLogin).where(UserLogin.automation_id == automation.id)
        user_login = session.exec(statement).first()

        if not user_login:
            print("No user login found for UTunnel automation.")
            return

        print(f"Testing UTunnel automation with user: {user_login.username}")
        print(f"Number of profiles to generate: 5")

        # Create automation engine
        automation_engine = AutomationEngine()

        try:
            # Execute automation
            result = await automation_engine.execute_automation(
                automation=automation, user_login=user_login, num_profiles=5
            )

            if result["success"]:
                print("✅ Automation completed successfully!")
                print(f"Result file: {result['result_file']}")
                print(f"Message: {result['message']}")
            else:
                print("❌ Automation failed!")
                print(f"Error: {result['error']}")
                print(f"Message: {result['message']}")

        except Exception as e:
            print(f"❌ Automation failed with exception: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_utunnel_automation())
