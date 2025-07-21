"""Background task handler for automation execution."""

import asyncio
from datetime import datetime
from sqlmodel import Session, select

from autovpn.core.database import engine
from autovpn.models.generation_request import GenerationRequest
from autovpn.models.automation import Automation
from autovpn.models.user_login import UserLogin
from autovpn.automation.engine import AutomationEngine


async def execute_generation_request(request_id: int):
    """Execute a generation request in the background."""
    print(f"🚀 Starting generation request #{request_id}")

    with Session(engine) as session:
        # Get the request
        statement = select(GenerationRequest).where(GenerationRequest.id == request_id)
        request = session.exec(statement).first()

        if not request:
            print(f"❌ Request #{request_id} not found")
            return

        # Update status to running
        request.status = "running"
        session.commit()
        print(f"🔄 Request #{request_id} status updated to running")

        try:
            # Get automation and user login
            automation = session.exec(
                select(Automation).where(Automation.id == request.automation_id)
            ).first()

            user_login = session.exec(
                select(UserLogin).where(UserLogin.id == request.user_login_id)
            ).first()

            if not automation or not user_login:
                request.status = "failed"
                request.error_message = "Automation or user login not found"
                session.commit()
                print(
                    f"❌ Request #{request_id} failed: Automation or user login not found"
                )
                return

            print(
                f"✅ Request #{request_id}: Found automation '{automation.name}' and user '{user_login.username}'"
            )

            # Execute automation
            automation_engine = AutomationEngine()
            result = await automation_engine.execute_automation(
                automation=automation,
                user_login=user_login,
                num_profiles=request.num_profiles,
            )

            # Update request with result
            if result["success"]:
                request.status = "completed"
                request.result_file = result["result_file"]
                request.completed_at = datetime.utcnow()
                print(
                    f"✅ Request #{request_id} completed successfully! Result file: {result['result_file']}"
                )
            else:
                request.status = "failed"
                request.error_message = result["error"]
                print(f"❌ Request #{request_id} failed: {result['error']}")

            session.commit()

        except Exception as e:
            request.status = "failed"
            request.error_message = str(e)
            session.commit()
            print(f"❌ Request #{request_id} failed with exception: {str(e)}")


def start_background_task(request_id: int):
    """Start a background task for automation execution."""
    asyncio.create_task(execute_generation_request(request_id))
