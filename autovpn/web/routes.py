"""Web routes for serving HTML pages."""

import os
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from autovpn.core.config import settings

# Setup templates
templates = Jinja2Templates(directory="autovpn/web/templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Admin panel."""
    return templates.TemplateResponse("admin.html", {"request": request})


@router.get("/user", response_class=HTMLResponse)
async def user_panel(request: Request):
    """User panel."""
    return templates.TemplateResponse("user.html", {"request": request})


@router.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """Download a file from the downloads directory."""
    # Ensure the file path is safe (no directory traversal)
    if ".." in file_path or file_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid file path")

    # Handle both relative and absolute paths
    if file_path.startswith("./downloads/") or file_path.startswith("downloads/"):
        # Extract just the filename from the path
        filename = file_path.split("/")[-1]
        full_path = Path(settings.download_dir) / filename
    else:
        # Assume it's just a filename
        full_path = Path(settings.download_dir) / file_path

    print(f"🔍 Looking for file: {full_path}")
    print(f"🔍 File exists: {full_path.exists()}")

    # Check if file exists
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {full_path}")

    # Return the file
    return FileResponse(
        path=str(full_path),
        filename=file_path.split("/")[-1],  # Get just the filename
        media_type="application/octet-stream",
    )
