"""Main FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from autovpn.core.config import settings, ensure_directories
from autovpn.core.database import create_tables
from autovpn.api.routes import router as api_router
from autovpn.web.routes import router as web_router
from autovpn.core.rate_limiter import rate_limiter, get_client_ip


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await create_tables()
    ensure_directories()  # Ensure required directories exist

    # Check if admin is setup
    from autovpn.core.database import engine
    from autovpn.models.app_password import AppPassword
    from sqlmodel import Session, select

    with Session(engine) as session:
        statement = select(AppPassword).where(AppPassword.name == "admin_master")
        admin_exists = session.exec(statement).first()

        if not admin_exists and settings.admin_master_password:
            # Auto-setup admin from environment variable
            from autovpn.core.security import hash_password

            admin_password = AppPassword(
                name="admin_master",
                password_hash=hash_password(settings.admin_master_password),
                is_active=True,
            )
            session.add(admin_password)
            session.commit()
            print("✅ Admin setup completed from environment variable")
        elif not admin_exists:
            print(
                "⚠️ Admin not setup. Set ADMIN_MASTER_PASSWORD environment variable to configure"
            )

    yield
    # Shutdown
    pass


app = FastAPI(
    title="AutoVPN",
    description="Automated VPN profile creation from websites",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    """Add rate limit headers to responses."""
    response = await call_next(request)

    # Add rate limit headers
    client_ip = get_client_ip(request)
    remaining_requests = rate_limiter.get_remaining_requests(client_ip)

    response.headers["X-RateLimit-Limit"] = "5"
    response.headers["X-RateLimit-Remaining"] = str(remaining_requests)
    response.headers["X-RateLimit-Reset"] = "60"

    return response


# Mount static files
app.mount("/static", StaticFiles(directory="autovpn/web/static"), name="static")

# Include routers
app.include_router(api_router, prefix="/api")
app.include_router(web_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for Render monitoring."""
    return {"status": "healthy", "service": "autovpn"}


@app.get("/setup-status")
async def setup_status():
    """Check if admin is setup."""
    from autovpn.core.database import engine
    from autovpn.models.app_password import AppPassword
    from sqlmodel import Session, select

    with Session(engine) as session:
        statement = select(AppPassword).where(AppPassword.name == "admin_master")
        admin_exists = session.exec(statement).first()

        return {
            "admin_setup": admin_exists is not None,
            "setup_method": "environment_variable",
            "instructions": "Set ADMIN_MASTER_PASSWORD environment variable to configure admin",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "autovpn.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
