"""Admin API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Form, Header
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from typing import List, Optional

from autovpn.core.database import get_session
from autovpn.models.automation import Automation, AutomationStep
from autovpn.models.user_login import UserLogin
from autovpn.models.app_password import AppPassword
from autovpn.models.generation_request import GenerationRequest
from autovpn.core.security import hash_password, verify_password, verify_token
from autovpn.core.config import settings

router = APIRouter()


def verify_admin_token(authorization: str = Header(None)):
    """Verify admin JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)

    if not payload or payload.get("sub") != "admin":
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload


@router.post("/auth")
async def admin_auth(
    password: str = Form(...), session: Session = Depends(get_session)
):
    """Authenticate admin with master password."""
    # Find admin password
    admin_password = session.exec(
        select(AppPassword).where(AppPassword.name == "admin_master")
    ).first()

    if not admin_password:
        raise HTTPException(status_code=401, detail="Admin not configured")

    # Verify password
    if not verify_password(password, admin_password.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Generate token (simple approach for now)
    from autovpn.core.security import create_access_token

    token = create_access_token(data={"sub": "admin"})

    return {"access_token": token, "token_type": "bearer"}


# App Password Management


@router.get("/passwords")
async def list_app_passwords(
    session: Session = Depends(get_session), _: dict = Depends(verify_admin_token)
):
    """List all app passwords."""
    statement = select(AppPassword)
    passwords = session.exec(statement).all()

    if not passwords:
        return HTMLResponse("<p class='text-gray-500'>No app passwords found.</p>")

    html = """
    <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-300">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
    """

    for password in passwords:
        html += f"""
                <tr id="password-{password.id}">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{password.id}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{password.name}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {'bg-green-100 text-green-800' if password.is_active else 'bg-red-100 text-red-800'}">
                            {'Active' if password.is_active else 'Inactive'}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{password.created_at.strftime('%Y-%m-%d %H:%M')}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button 
                            onclick="deletePassword({password.id})"
                            class="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                        >
                            Delete
                        </button>
                    </td>
                </tr>
        """

    html += """
            </tbody>
        </table>
    </div>
    """

    return HTMLResponse(html)


@router.post("/passwords")
async def create_app_password(
    name: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin_token),
):
    """Create a new app password."""
    # Check if password with this name already exists
    existing = session.exec(select(AppPassword).where(AppPassword.name == name)).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Password with this name already exists"
        )

    app_password = AppPassword(
        name=name, password_hash=hash_password(password), is_active=True
    )
    session.add(app_password)
    session.commit()
    session.refresh(app_password)

    return HTMLResponse(
        f"""
    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
        App password '{name}' created successfully!
    </div>
    """
    )


@router.delete("/passwords/{password_id}")
async def delete_app_password(
    password_id: int,
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin_token),
):
    """Delete an app password."""
    password = session.exec(
        select(AppPassword).where(AppPassword.id == password_id)
    ).first()
    if not password:
        raise HTTPException(status_code=404, detail="Password not found")

    session.delete(password)
    session.commit()

    return HTMLResponse("")


# Automation Management


@router.get("/automations")
async def list_automations(
    session: Session = Depends(get_session), _: dict = Depends(verify_admin_token)
):
    """List all automations with step counts."""
    statement = select(Automation)
    automations = session.exec(statement).all()

    if not automations:
        return HTMLResponse("<p class='text-gray-500'>No automations found.</p>")

    html = """
    <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-300">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Base URL</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Steps</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
    """

    for automation in automations:
        # Get step count properly
        steps = session.exec(
            select(AutomationStep).where(AutomationStep.automation_id == automation.id)
        ).all()
        steps_count = len(steps)

        html += f"""
                <tr id="automation-{automation.id}">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{automation.id}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{automation.name}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{automation.description or 'No description'}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{automation.base_url}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {'bg-green-100 text-green-800' if automation.is_active else 'bg-red-100 text-red-800'}">
                            {'Active' if automation.is_active else 'Inactive'}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{steps_count}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{automation.created_at.strftime('%Y-%m-%d %H:%M')}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div class="flex space-x-2">
                            <button 
                                onclick="navigator.clipboard.writeText('{automation.id}').then(() => {{ this.textContent = 'Copied!'; setTimeout(() => {{ this.textContent = 'Copy ID'; }}, 2000); }}).catch(() => {{ alert('Failed to copy ID'); }});"
                                class="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                            >
                                Copy ID
                            </button>
                            <button 
                                onclick="deleteAutomation({automation.id})"
                                class="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                            >
                                Delete
                            </button>
                        </div>
                    </td>
                </tr>
        """

    html += """
            </tbody>
        </table>
    </div>
    """

    return HTMLResponse(html)


@router.delete("/automations/{automation_id}")
async def delete_automation(
    automation_id: int,
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin_token),
):
    """Delete an automation and all its steps."""
    automation = session.exec(
        select(Automation).where(Automation.id == automation_id)
    ).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    automation_name = automation.name

    # Delete all generation requests first (foreign key constraint)
    generation_requests = session.exec(
        select(GenerationRequest).where(
            GenerationRequest.automation_id == automation_id
        )
    ).all()
    for request in generation_requests:
        session.delete(request)

    # Delete all user logins (foreign key constraint)
    user_logins = session.exec(
        select(UserLogin).where(UserLogin.automation_id == automation_id)
    ).all()
    for login in user_logins:
        session.delete(login)

    # Delete all steps
    steps = session.exec(
        select(AutomationStep).where(AutomationStep.automation_id == automation_id)
    ).all()
    for step in steps:
        session.delete(step)

    # Delete the automation
    session.delete(automation)
    session.commit()

    return HTMLResponse(
        f"""
    <tr class="bg-green-50">
        <td colspan="8" class="px-6 py-4 text-center text-sm text-green-700">
            Automation '{automation_name}' deleted successfully!
        </td>
    </tr>
    """
    )


# Import Scripts Management


@router.get("/import-scripts")
async def list_import_scripts(
    session: Session = Depends(get_session), _: dict = Depends(verify_admin_token)
):
    """List available automation import scripts."""
    import os
    import importlib.util
    from pathlib import Path

    scripts_dir = Path("automations")
    scripts = []

    if scripts_dir.exists():
        for script_file in scripts_dir.glob("*.py"):
            if script_file.name.startswith("create_") and script_file.name.endswith(
                "_automation.py"
            ):
                # Extract automation name from filename
                name = (
                    script_file.stem.replace("create_", "")
                    .replace("_automation", "")
                    .upper()
                )

                # Check if already imported
                existing = session.exec(
                    select(Automation).where(Automation.name == name)
                ).first()

                scripts.append(
                    {
                        "filename": script_file.name,
                        "name": name,
                        "description": f"Import {name} automation from script",
                        "imported": existing is not None,
                    }
                )

    return scripts


@router.post("/import-automation")
async def import_automation(
    filename: str = Form(...),
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin_token),
):
    """Import an automation from a script file."""
    import os
    import importlib.util
    import asyncio
    from pathlib import Path

    script_path = Path("automations") / filename

    if not script_path.exists():
        raise HTTPException(status_code=404, detail="Script file not found")

    try:
        # Import the script module
        spec = importlib.util.spec_from_file_location("automation_script", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find the recreate function
        recreate_func = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr) and "recreate" in attr_name and "automation" in attr_name:
                recreate_func = attr
                break

        if not recreate_func:
            raise HTTPException(
                status_code=400, detail="No recreate function found in script"
            )

        # Run the recreate function
        if asyncio.iscoroutinefunction(recreate_func):
            automation_id = await recreate_func()
        else:
            automation_id = recreate_func()

        return {
            "message": "Automation imported successfully",
            "automation_id": automation_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to import automation: {str(e)}"
        )


# User Login Management


@router.get("/logins")
async def list_user_logins(
    session: Session = Depends(get_session), _: dict = Depends(verify_admin_token)
):
    """List all user logins with automation names."""
    statement = select(UserLogin)
    logins = session.exec(statement).all()

    if not logins:
        return HTMLResponse("<p class='text-gray-500'>No user logins found.</p>")

    html = """
    <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-300">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Display Name</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Username</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Automation</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
    """

    for login in logins:
        automation = session.exec(
            select(Automation).where(Automation.id == login.automation_id)
        ).first()
        automation_name = automation.name if automation else "Unknown"

        html += f"""
                <tr id="login-{login.id}">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{login.id}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{login.display_name or 'N/A'}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{login.username}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{automation_name}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {'bg-green-100 text-green-800' if login.is_active else 'bg-red-100 text-red-800'}">
                            {'Active' if login.is_active else 'Inactive'}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{login.created_at.strftime('%Y-%m-%d %H:%M')}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button 
                            onclick="deleteLogin({login.id})"
                            class="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                        >
                            Delete
                        </button>
                    </td>
                </tr>
        """

    html += """
            </tbody>
        </table>
    </div>
    """

    return HTMLResponse(html)


@router.post("/logins")
async def create_user_login(
    automation_id: int = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    display_name: str = Form(""),
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin_token),
):
    """Create a new user login."""
    # Verify automation exists
    automation = session.exec(
        select(Automation).where(Automation.id == automation_id)
    ).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    user_login = UserLogin(
        automation_id=automation_id,
        username=username,
        password=password,
        display_name=display_name or username,
        is_active=True,
    )
    session.add(user_login)
    session.commit()
    session.refresh(user_login)

    return HTMLResponse(
        f"""
    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
        User login '{username}' created successfully!
    </div>
    """
    )


@router.delete("/logins/{login_id}")
async def delete_user_login(
    login_id: int,
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin_token),
):
    """Delete a user login."""
    login = session.exec(select(UserLogin).where(UserLogin.id == login_id)).first()
    if not login:
        raise HTTPException(status_code=404, detail="User login not found")

    login_name = login.display_name or login.username

    # Delete all generation requests that reference this login
    generation_requests = session.exec(
        select(GenerationRequest).where(GenerationRequest.user_login_id == login_id)
    ).all()
    for request in generation_requests:
        session.delete(request)

    # Delete the user login
    session.delete(login)
    session.commit()

    return HTMLResponse(
        f"""
    <tr class="bg-green-50">
        <td colspan="7" class="px-6 py-4 text-center text-sm text-green-700">
            User login '{login_name}' deleted successfully!
        </td>
    </tr>
    """
    )
