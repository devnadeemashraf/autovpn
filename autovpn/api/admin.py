"""Admin API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from typing import List, Optional

from autovpn.core.database import get_session
from autovpn.models.automation import Automation, AutomationStep
from autovpn.models.user_login import UserLogin
from autovpn.models.app_password import AppPassword
from autovpn.models.generation_request import GenerationRequest
from autovpn.core.security import hash_password

router = APIRouter()


# App Password Management
@router.post("/passwords")
async def create_app_password(
    name: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    """Create new app password."""
    app_password = AppPassword(
        name=name, password_hash=hash_password(password), is_active=True
    )
    session.add(app_password)
    session.commit()
    # Return HTML for HTMX to insert
    return HTMLResponse(
        f"""
    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
        App password '{name}' created successfully!
    </div>
    """
    )


@router.get("/passwords")
async def list_app_passwords(session: Session = Depends(get_session)):
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
                            hx-delete="/api/admin/passwords/{password.id}"
                            hx-target="#password-{password.id}"
                            hx-swap="outerHTML"
                            class="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                            onclick="return confirm('Are you sure you want to delete this password?')"
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


@router.delete("/passwords/{password_id}")
async def delete_app_password(
    password_id: int, session: Session = Depends(get_session)
):
    """Delete app password."""
    statement = select(AppPassword).where(AppPassword.id == password_id)
    password = session.exec(statement).first()
    if not password:
        raise HTTPException(status_code=404, detail="Password not found")

    password_name = password.name
    session.delete(password)
    session.commit()

    # Return empty string to remove the row completely
    return HTMLResponse("")


# Automation Management
@router.get("/automations")
async def list_automations(session: Session = Depends(get_session)):
    """List all automations."""
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
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
    """

    for automation in automations:
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
                                hx-delete="/api/admin/automations/{automation.id}"
                                hx-target="#automation-{automation.id}"
                                hx-swap="outerHTML"
                                class="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                                onclick="return confirm('Are you sure you want to delete this automation?')"
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
    automation_id: int, session: Session = Depends(get_session)
):
    """Delete automation."""
    statement = select(Automation).where(Automation.id == automation_id)
    automation = session.exec(statement).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    automation_name = automation.name

    # First delete all generation requests for this automation
    requests_statement = select(GenerationRequest).where(
        GenerationRequest.automation_id == automation_id
    )
    requests = session.exec(requests_statement).all()
    for request in requests:
        session.delete(request)

    # Then delete all automation steps
    steps_statement = select(AutomationStep).where(
        AutomationStep.automation_id == automation_id
    )
    steps = session.exec(steps_statement).all()
    for step in steps:
        session.delete(step)

    # Then delete all user logins for this automation
    logins_statement = select(UserLogin).where(UserLogin.automation_id == automation_id)
    logins = session.exec(logins_statement).all()
    for login in logins:
        session.delete(login)

    # Finally delete the automation
    session.delete(automation)
    session.commit()

    # Return HTML for HTMX to replace the element
    return HTMLResponse(
        f"""
    <tr class="bg-green-50">
        <td colspan="7" class="px-6 py-4 text-center text-sm text-green-700">
            Automation '{automation_name}' deleted successfully!
        </td>
    </tr>
    """
    )


# User Login Management
@router.get("/user-logins")
async def list_user_logins(session: Session = Depends(get_session)):
    """List all user logins."""
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
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Automation ID</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
    """

    for login in logins:
        html += f"""
                <tr id="login-{login.id}">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{login.id}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{login.display_name or 'N/A'}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{login.username}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{login.automation_id}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {'bg-green-100 text-green-800' if login.is_active else 'bg-red-100 text-red-800'}">
                            {'Active' if login.is_active else 'Inactive'}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{login.created_at.strftime('%Y-%m-%d %H:%M')}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button 
                            hx-delete="/api/admin/user-logins/{login.id}"
                            hx-target="#login-{login.id}"
                            hx-swap="outerHTML"
                            class="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                            onclick="return confirm('Are you sure you want to delete this login?')"
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


@router.post("/user-logins")
async def create_user_login(
    automation_id: int = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    display_name: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    """Create new user login."""
    user_login = UserLogin(
        automation_id=automation_id,
        username=username,
        password=password,  # In production, this should be encrypted
        display_name=display_name or username,
        is_active=True,
    )
    session.add(user_login)
    session.commit()
    # Return HTML for HTMX to insert
    return HTMLResponse(
        f"""
    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
        User login '{username}' created successfully!
    </div>
    """
    )


@router.delete("/user-logins/{login_id}")
async def delete_user_login(login_id: int, session: Session = Depends(get_session)):
    """Delete user login."""
    statement = select(UserLogin).where(UserLogin.id == login_id)
    login = session.exec(statement).first()
    if not login:
        raise HTTPException(status_code=404, detail="Login not found")

    login_name = login.display_name or login.username
    session.delete(login)
    session.commit()

    # Return HTML for HTMX to replace the element
    return HTMLResponse(
        f"""
    <tr class="bg-green-50">
        <td colspan="7" class="px-6 py-4 text-center text-sm text-green-700">
            User login '{login_name}' deleted successfully!
        </td>
    </tr>
    """
    )
