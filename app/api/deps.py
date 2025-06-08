from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models import user as models
from app.schemas import user as schemas
from app.services.user_service import UserService

# トークン取得のためのエンドポイント
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db() -> Generator:
    """
    データベースセッションの依存関係
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

## MONGODBの依存関係はここでは定義
def get_mongo_db() -> Generator:
    """
    MongoDBセッションの依存関係
    """
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb = client[settings.MONGODB_DB_NAME]
        yield mongodb
    finally:
        client.close()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    ユーザーサービスの依存関係
    
    Args:
        db: データベースセッション
        
    Returns:
        UserService: ユーザーサービスインスタンス
    """
    return UserService(db=db)

def get_current_user(
    user_service: UserService = Depends(get_user_service), token: str = Depends(oauth2_scheme)
) -> models.User:
    """
    JWTトークンからユーザーを取得する依存関係
    
    Args:
        db: データベースセッション
        token: JWTトークン
        
    Returns:
        models.User: 現在のユーザー
        
    Raises:
        HTTPException: トークンが無効または期限切れの場合
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証情報が無効です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = user_service.get(user_id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="非アクティブユーザー")
    return user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    管理者権限を持つユーザーの依存関係
    
    Args:
        current_user: 現在のユーザー
        
    Returns:
        models.User: 管理者権限を持つユーザー
        
    Raises:
        HTTPException: ユーザーが管理者でない場合
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="十分な権限がありません"
        )
    return current_user