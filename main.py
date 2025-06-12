from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

# OPENAPI_URLの処理を修正
openapi_url = f"{settings.OPENAPI_URL}/openapi.json" if settings.OPENAPI_URL else "/openapi.json"

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=openapi_url,
    openapi_version="3.0.2",
)

origins = []

if settings.ALLOWED_ORIGINS:
    origins.extend(settings.ALLOWED_ORIGINS.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(api_router, prefix=settings.API_V1_STR)
