import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):

    # アプリケーションの設定
    APP_NAME: str = "FURNIAIZER API"
    OPENAPI_URL: str | None = os.getenv("OPENAPI_URL", "")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")

    # Github OAuthの設定
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET")
    FRONTEND_REDIRECT_URL: str = os.getenv("FRONTEND_REDIRECT_URL")

    # Firebaseの設定
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")

    # GEMINIの設定
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CHAT_MODEL: str = os.getenv("GOOGLE_CHAT_MODEL", "gemini-1.5-flash")

settings = Settings()