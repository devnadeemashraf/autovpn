"""Script to Create UTunnel automation with updated steps."""

import asyncio
from sqlmodel import Session, select

from autovpn.core.database import engine
from autovpn.models.automation import Automation, AutomationStep
from autovpn.models.user_login import UserLogin


async def recreate_utunnel_automation():
    """Delete old UTunnel automation and recreate with updated steps."""
    with Session(engine) as session:
        # Delete existing UTunnel automation and all its steps
        statement = select(Automation).where(Automation.name == "UTUNNEL")
        existing_automation = session.exec(statement).first()

        if existing_automation:
            print(
                f"🗑️ Deleting existing UTunnel automation (ID: {existing_automation.id})"
            )

            # Delete all steps for this automation
            steps_statement = select(AutomationStep).where(
                AutomationStep.automation_id == existing_automation.id
            )
            steps = session.exec(steps_statement).all()
            for step in steps:
                session.delete(step)

            # Delete the automation
            session.delete(existing_automation)
            session.commit()
            print(f"✅ Deleted {len(steps)} steps and automation")

        # Create new automation
        automation = Automation(
            name="UTUNNEL",
            description="Automated VPN profile generation from UTunnel Pro",
            base_url="https://utunnelpro.xyz",
            is_active=True,
        )
        session.add(automation)
        session.commit()
        session.refresh(automation)

        print(f"✅ Created new UTunnel automation (ID: {automation.id})")

        # Create automation steps with updated structure
        steps = [
            # Step 1: Navigate to login page
            AutomationStep(
                automation_id=automation.id,
                step_order=1,
                action_type="navigate",
                input_value="https://utunnelpro.xyz/login",
                description="Navigate to login page",
            ),
            # Step 2: Check if already logged in
            AutomationStep(
                automation_id=automation.id,
                step_order=2,
                action_type="check_session_status",
                description="Check if user is already logged in",
            ),
            # Step 3: Wait for login form
            AutomationStep(
                automation_id=automation.id,
                step_order=3,
                action_type="wait_for_element",
                xpath="/html/body/div[1]/section/div/div/div/div[2]/div/form/div[2]/input",
                description="Wait for username field",
            ),
            # Step 4: Enter username
            AutomationStep(
                automation_id=automation.id,
                step_order=4,
                action_type="input",
                xpath="/html/body/div[1]/section/div/div/div/div[2]/div/form/div[2]/input",
                input_value="{username}",
                description="Enter username",
            ),
            # Step 5: Enter password
            AutomationStep(
                automation_id=automation.id,
                step_order=5,
                action_type="input",
                xpath="/html/body/div[1]/section/div/div/div/div[2]/div/form/div[3]/input",
                input_value="{password}",
                description="Enter password",
            ),
            # Step 6: Click login button
            AutomationStep(
                automation_id=automation.id,
                step_order=6,
                action_type="click",
                xpath="/html/body/div[1]/section/div/div/div/div[2]/div/form/div[4]/button",
                description="Click login button",
            ),
            # Step 7: Wait for login response
            AutomationStep(
                automation_id=automation.id,
                step_order=7,
                action_type="wait",
                wait_time=3,
                description="Wait for login response",
            ),
            # Step 8: Check login success via URL redirect
            AutomationStep(
                automation_id=automation.id,
                step_order=8,
                action_type="check_url_redirect",
                success_indicator="dashboard",
                description="Check if login was successful by URL redirect",
            ),
            # Step 9: Navigate to dashboard
            AutomationStep(
                automation_id=automation.id,
                step_order=9,
                action_type="navigate",
                input_value="https://utunnelpro.xyz/dashboard",
                description="Navigate to dashboard",
            ),
            # Step 10: Wait for dashboard to load
            AutomationStep(
                automation_id=automation.id,
                step_order=10,
                action_type="wait",
                wait_time=2,
                description="Wait for dashboard to load",
            ),
            # Step 11: Navigate to add user page
            AutomationStep(
                automation_id=automation.id,
                step_order=11,
                action_type="navigate",
                input_value="https://utunnelpro.xyz/add/user",
                description="Navigate to add user page",
            ),
            # Step 12: Wait for bulk add card
            AutomationStep(
                automation_id=automation.id,
                step_order=12,
                action_type="wait_for_element",
                xpath="/html/body/div[2]/div[3]/section/div[3]/div/div[2]/div/div/h5",
                description="Wait for bulk add card",
            ),
            # Step 13: Get credit balance
            AutomationStep(
                automation_id=automation.id,
                step_order=13,
                action_type="get_element_value",
                xpath="/html/body/div[2]/div[3]/section/div[3]/div/div[2]/div/div/form/div[1]/input",
                description="Get credit balance",
            ),
            # Step 14: Check if enough credit
            AutomationStep(
                automation_id=automation.id,
                step_order=14,
                action_type="check_credit_balance",
                description="Check if user has enough credit",
            ),
            # Step 15: Generate random prefix
            AutomationStep(
                automation_id=automation.id,
                step_order=15,
                action_type="generate_prefix",
                description="Generate random 5-digit prefix",
            ),
            # Step 16: Enter prefix
            AutomationStep(
                automation_id=automation.id,
                step_order=16,
                action_type="input",
                xpath="/html/body/div[2]/div[3]/section/div[3]/div/div[2]/div/div/form/div[2]/input",
                input_value="{generated_prefix}",
                description="Enter generated prefix",
            ),
            # Step 17: Enter amount
            AutomationStep(
                automation_id=automation.id,
                step_order=17,
                action_type="input",
                xpath="/html/body/div[2]/div[3]/section/div[3]/div/div[2]/div/div/form/div[3]/input",
                input_value="{num_profiles}",
                description="Enter number of profiles to create",
            ),
            # Step 18: Submit form
            AutomationStep(
                automation_id=automation.id,
                step_order=18,
                action_type="click",
                xpath="/html/body/div[2]/div[3]/section/div[3]/div/div[2]/div/div/form/div[4]/button",
                description="Click Generate Button",
            ),
            # Step 19: Wait for response
            AutomationStep(
                automation_id=automation.id,
                step_order=19,
                action_type="wait",
                wait_time=3,
                description="Wait for form submission response",
            ),
            # Step 20: Check operation success
            AutomationStep(
                automation_id=automation.id,
                step_order=20,
                action_type="check_operation_success",
                xpath="/html/body/div[2]/div[3]/section/div[2]/div/div/div[2]/div",
                description="Check if operation was successful",
            ),
            # Step 21: Navigate to bulk log
            AutomationStep(
                automation_id=automation.id,
                step_order=21,
                action_type="navigate",
                input_value="https://utunnelpro.xyz/log/bulk",
                description="Navigate to bulk log page",
            ),
            # Step 22: Wait for log page
            AutomationStep(
                automation_id=automation.id,
                step_order=22,
                action_type="wait",
                wait_time=2,
                description="Wait for log page to load",
            ),
            # Step 23: Find generated entry
            AutomationStep(
                automation_id=automation.id,
                step_order=23,
                action_type="find_generated_entry",
                description="Find the generated entry in the log",
            ),
            # Step 24: Download CSV
            AutomationStep(
                automation_id=automation.id,
                step_order=24,
                action_type="download_csv",
                description="Download the CSV file",
            ),
            # Step 25: Convert to Excel
            AutomationStep(
                automation_id=automation.id,
                step_order=25,
                action_type="convert_to_excel",
                description="Convert CSV to Excel format",
            ),
        ]

        for step in steps:
            session.add(step)

        session.commit()

        print(f"✅ UTunnel automation recreated successfully!")
        print(f"📊 Total steps created: {len(steps)}")
        print(f"🆔 New automation ID: {automation.id}")

        return automation.id


if __name__ == "__main__":
    asyncio.run(recreate_utunnel_automation())
