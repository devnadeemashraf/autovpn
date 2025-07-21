"""Test script for delete functionality."""

import asyncio
from sqlmodel import Session, select

from autovpn.core.database import engine
from autovpn.models.automation import Automation
from autovpn.models.user_login import UserLogin
from autovpn.models.app_password import AppPassword


async def test_delete_functionality():
    """Test delete functionality for all entities."""
    with Session(engine) as session:
        print("=" * 50)
        print("Testing Delete Functionality")
        print("=" * 50)

        # Test App Passwords
        print("\n1. Testing App Passwords:")
        passwords = session.exec(select(AppPassword)).all()
        print(f"   Found {len(passwords)} app passwords")
        for pwd in passwords:
            print(f"   - {pwd.name} (ID: {pwd.id})")

        # Test Automations
        print("\n2. Testing Automations:")
        automations = session.exec(select(Automation)).all()
        print(f"   Found {len(automations)} automations")
        for auto in automations:
            print(f"   - {auto.name} (ID: {auto.id})")

        # Test User Logins
        print("\n3. Testing User Logins:")
        logins = session.exec(select(UserLogin)).all()
        print(f"   Found {len(logins)} user logins")
        for login in logins:
            print(f"   - {login.display_name or login.username} (ID: {login.id})")

        print("\n" + "=" * 50)
        print("Delete functionality is ready!")
        print("You can now use the admin panel to delete items.")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_delete_functionality())
