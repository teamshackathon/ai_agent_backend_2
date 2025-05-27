from fastapi import APIRouter

from .endpoints import auth, chat, healthcheck

api_router = APIRouter()

# Include the healthcheck router
api_router.include_router(healthcheck.router, prefix="/healthcheck", tags=["healthcheck"])

# Include the auth router
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include the chat router
api_router.include_router(chat.router, tags=["chat"])
