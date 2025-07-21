"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlmodel import Session, select

from autovpn.core.database import get_session
from autovpn.models.app_password import AppPassword
from autovpn.core.security import verify_password

router = APIRouter()


@router.post("/verify")
async def verify_app_password(
    password: str = Form(...), session: Session = Depends(get_session)
):
    """Verify app password."""
    statement = select(AppPassword).where(AppPassword.is_active == True)
    app_passwords = session.exec(statement).all()

    for app_password in app_passwords:
        is_valid = verify_password(password, app_password.password_hash)
        if is_valid:
            return {"valid": True, "message": "Password verified"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
    )
