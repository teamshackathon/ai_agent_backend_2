from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """認証トークンスキーマ"""
    id_token: str = Field(..., description="Firebase ID Token")

class TokenPayload(BaseModel):
    """トークンのペイロードスキーマ"""
    sub: Optional[str] = None
    exp: Optional[int] = None

class UserBase(BaseModel):
    """ユーザー基本情報スキーマ"""
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    photo_url: Optional[str] = None

class UserCreate(UserBase):
    """ユーザー作成用スキーマ"""
    email: EmailStr = Field(..., description="ユーザーメールアドレス")
    password: str = Field(..., min_length=6, description="パスワード（6文字以上）")
    display_name: Optional[str] = Field(None, description="表示名")

class UserLogin(BaseModel):
    """ユーザーログイン用スキーマ"""
    email: EmailStr
    password: str

class PasswordReset(BaseModel):
    """パスワードリセット用スキーマ"""
    email: EmailStr

class UserUpdate(UserBase):
    """ユーザー更新用スキーマ"""
    preferences: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    """APIレスポンス用ユーザースキーマ"""
    id: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    photo_url: Optional[str] = None

    class Config:
        from_attributes = True