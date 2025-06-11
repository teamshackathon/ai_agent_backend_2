import os
from typing import Any, Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # アプリケーションの設定
    PROJECT_NAME: str = "HT SB API"
    API_V1_STR: str = "/api/v1"
    VERSION: str = os.getenv("VERSION", "development")
    OPENAPI_URL: str | None = os.getenv("OPENAPI_URL", "")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # JWT認証
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))  # 1日

    # Github OAuthの設定
    GITHUB_CLIENT_ID: Optional[str] = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: Optional[str] = os.getenv("GITHUB_CLIENT_SECRET")
    GITHUB_REDIRECT_URI: Optional[str] = os.getenv("GITHUB_REDIRECT_URI")

    FRONTEND_REDIRECT_URL: Optional[str] = os.getenv("FRONTEND_REDIRECT_URL")

    # データベース設定
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")  # Docker環境ではサービス名を使用
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "furniaizer")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Redis設定
    REDIS_URL: Optional[str] = None  # RedisのURLが設定されている場合
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")  # Docker環境ではサービス名を使用
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_IMAGE_CACHE_TTL: int = 3600  # 1時間
    REDIS_MAX_IMAGE_SIZE: int = 1024 * 1024 * 5  # 最大5MB

    # MinIO設定
    MINIO_ENDPOINT_URL: str = os.getenv("MINIO_ENDPOINT_URL")
    MINIO_ACCESS_KEY_ID: str = os.getenv("MINIO_ACCESS_KEY_ID", "minioadmin")
    MINIO_SECRET_ACCESS_KEY: str = os.getenv("MINIO_SECRET_ACCESS_KEY", "minioadmin")
    STORAGE_BUCKET_NAME: str = os.getenv("STORAGE_BUCKET_NAME", "furniaizer-bucket")

    # GEMINIの設定
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CHAT_MODEL: str = os.getenv("GOOGLE_CHAT_MODEL", "gemini-1.5-flash")

    # MongoDB設定
    MONGODB_URL: Optional[str] = None
    MONGODB_HOST: Optional[str] = os.getenv("MONGODB_HOST", "mongo")  # Docker環境ではサービス名を使用
    MONGODB_USERNAME: Optional[str] = os.getenv("MONGODB_USERNAME", "mongdb")
    MONGODB_PASSWORD: Optional[str] = os.getenv("MONGODB_PASSWORD", "mongdb")
    MONGODB_DB_NAME: Optional[str] = os.getenv("MONGODB_DB_NAME", "furniaizer")

    def __init__(self, **data: Any):
        super().__init__(**data)

        # 環境に基づいてDBのURIを設定
        if self.ENVIRONMENT == "production":
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        else:
            # 開発環境ではSQLiteも使用可能
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
            # または: self.SQLALCHEMY_DATABASE_URI = "sqlite:///./test.db"

        self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

        # MongoDB接続設定
        if self.MONGODB_HOST == "localhost":
            # ローカル環境では認証なしでMongoDBに接続
            self.MONGODB_URL = f"mongodb://{self.MONGODB_HOST}:27017"
        else:
            # Docker環境などでは認証情報を使用
            self.MONGODB_URL = f"mongodb://{self.MONGODB_USERNAME}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}:27017"

    class Config:
        case_sensitive = True


settings = Settings()
