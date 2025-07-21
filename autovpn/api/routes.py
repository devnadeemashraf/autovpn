"""Main API router."""

from fastapi import APIRouter, Depends

from autovpn.api.admin import router as admin_router
from autovpn.api.user import router as user_router
from autovpn.api.auth import router as auth_router
from autovpn.core.rate_limiter import check_rate_limit

router = APIRouter()

# Apply rate limiting to all API routes
router.include_router(
    auth_router,
    prefix="/auth",
    tags=["authentication"],
    dependencies=[Depends(check_rate_limit)],
)
router.include_router(
    admin_router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(check_rate_limit)],
)
router.include_router(
    user_router, prefix="/user", tags=["user"], dependencies=[Depends(check_rate_limit)]
)
