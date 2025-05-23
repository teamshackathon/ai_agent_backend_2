from fastapi import APIRouter
from .endpoints import healthcheck
from .endpoints import auth

api_router = APIRouter()

# Include the healthcheck router
api_router.include_router(
    healthcheck.router,
    prefix="/healthcheck",
    tags=["healthcheck"]
)

# Include the auth router
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)