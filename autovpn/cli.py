"""CLI commands for AutoVPN."""

import asyncio
import getpass
import sys

try:
    from sqlmodel import Session, select
    from autovpn.core.database import engine
    from autovpn.core.config import settings
    from autovpn.models.app_password import AppPassword
    from autovpn.core.security import hash_password, verify_password
except ImportError:
    print("Dependencies not installed. Please run: pip install -r requirements.txt")
    sys.exit(1)


def show_help():
    """Show CLI help."""
    print("=" * 50)
    print("AutoVPN CLI")
    print("=" * 50)
    print("\nUsage: python -m autovpn.cli <command>")
    print("\nAvailable commands:")
    print("  setup-admin     - Setup admin master password")
    print("  create-password - Create a new app password")
    print("  list-passwords  - List all app passwords")
    print("  verify-admin    - Verify admin password")
    print("\nExample:")
    print("  python -m autovpn.cli setup-admin")


def setup_admin():
    """Setup admin master password via CLI."""
    print("=" * 50)
    print("AutoVPN Admin Setup")
    print("=" * 50)

    # Check if admin already exists
    with Session(engine) as session:
        statement = select(AppPassword).where(AppPassword.name == "admin_master")
        existing_admin = session.exec(statement).first()

        if existing_admin:
            print("Admin is already setup!")
            return

    # Get admin password
    while True:
        password = getpass.getpass("Enter admin master password: ")
        confirm_password = getpass.getpass("Confirm admin master password: ")

        if password == confirm_password:
            if len(password) < 6:
                print("Password must be at least 6 characters long.")
                continue
            break
        else:
            print("Passwords do not match. Please try again.")

    # Create admin password
    with Session(engine) as session:
        admin_password = AppPassword(
            name="admin_master", password_hash=hash_password(password), is_active=True
        )
        session.add(admin_password)
        session.commit()

    print("\n" + "=" * 50)
    print("Admin setup completed successfully!")
    print("=" * 50)


def create_app_password():
    """Create a new app password via CLI."""
    print("=" * 50)
    print("Create App Password")
    print("=" * 50)

    name = input("Enter password name: ")
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if password != confirm_password:
        print("Passwords do not match!")
        return

    with Session(engine) as session:
        app_password = AppPassword(
            name=name, password_hash=hash_password(password), is_active=True
        )
        session.add(app_password)
        session.commit()

    print(f"\nApp password '{name}' created successfully!")


def list_app_passwords():
    """List all app passwords."""
    print("=" * 50)
    print("App Passwords")
    print("=" * 50)

    with Session(engine) as session:
        statement = select(AppPassword)
        passwords = session.exec(statement).all()

        if not passwords:
            print("No app passwords found.")
            return

        for password in passwords:
            print(f"ID: {password.id}")
            print(f"Name: {password.name}")
            print(f"Active: {password.is_active}")
            print(f"Created: {password.created_at}")
            print("-" * 30)


def verify_admin_password():
    """Verify admin password via CLI."""
    print("=" * 50)
    print("Verify Admin Password")
    print("=" * 50)

    password = getpass.getpass("Enter admin password: ")

    with Session(engine) as session:
        statement = select(AppPassword).where(AppPassword.name == "admin_master")
        admin_password = session.exec(statement).first()

        if not admin_password:
            print("Admin not setup yet!")
            return

        if verify_password(password, admin_password.password_hash):
            print("Admin password verified successfully!")
        else:
            print("Invalid admin password!")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1]

    if command == "setup-admin":
        setup_admin()
    elif command == "create-password":
        create_app_password()
    elif command == "list-passwords":
        list_app_passwords()
    elif command == "verify-admin":
        verify_admin_password()
    else:
        print(f"Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()
