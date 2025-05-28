
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="FURNIAIZER API",
    version="1.0.0",
    openapi_url=settings.OPENAPI_URL + "/openapi.json"
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

app.include_router(api_router, prefix="/api/v1")

