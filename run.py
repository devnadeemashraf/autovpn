#!/usr/bin/env python3
"""Run the AutoVPN application."""

import os
import uvicorn
from autovpn.core.config import ensure_directories

if __name__ == "__main__":
    # Ensure directories exist
    ensure_directories()

    # Get host and port from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    # Run the application
    uvicorn.run(
        "autovpn.main:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info",
    )
