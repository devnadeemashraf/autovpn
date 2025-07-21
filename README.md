# AutoVPN

Automated VPN profile creation from websites using configurable automation workflows.

## Features

- Web automation for VPN profile generation
- Configurable automation workflows
- Admin and user interfaces
- File conversion (txt to xlsx)
- Secure authentication system

## Tech Stack

- Python 3.13
- FastAPI (Backend)
- SQLite3 + SQLModel
- Selenium (Web Automation)
- Poetry (Dependency Management)

## Quick Start

1. Install dependencies:

```bash
poetry install
# or
pip install -r requirements.txt
```

2. Setup admin (CLI only):

```bash
python -m autovpn.cli setup-admin
```

3. Run the application:

```bash
python -m autovpn.main
# or
python run.py
```

4. Access the application at `http://localhost:8000`

## Development

- Backend: FastAPI with SQLModel
- Frontend: HTML templates with Jinja2
- Database: SQLite3
- Web Automation: Selenium with Chrome WebDriver

## CLI Commands

The application provides CLI commands for administrative tasks:

```bash
# Setup admin master password
python -m autovpn.cli setup-admin

# Create a new app password for users
python -m autovpn.cli create-password

# List all app passwords
python -m autovpn.cli list-passwords

# Verify admin password
python -m autovpn.cli verify-admin
```

## Deployment

The application is designed to run on free hosting platforms like Railway or Render.
