from datetime import datetime
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserOAuthCreate, UserUpdate


class UserService:
    """ユーザー関連のビジネスロジックを処理するサービス"""

    def __init__(self, db: Session):
        self.db = db
    
    def get(self, user_id: int) -> Optional[User]:
        """
        IDでユーザーを取得
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update(self, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        """
        ユーザー情報を更新
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
            
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
                
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get_by_email(self, email: str) -> Optional[User]:
        """メールアドレスでユーザーを取得"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_oauth_id(self, provider: str, oauth_id: str) -> Optional[User]:
        """OAuth IDでユーザーを取得"""
        return self.db.query(User).filter(
            User.oauth_provider == provider,
            User.oauth_id == oauth_id
        ).first()
    
    def create(self, obj_in: UserCreate) -> User:
        """パスワード認証ユーザーを作成"""
        db_obj = User(
            email=obj_in.email,
            name=obj_in.name,
            hashed_password=get_password_hash(obj_in.password),
            is_active=True,
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def create_oauth_user(self, obj_in: UserOAuthCreate) -> User:
        """OAuthユーザーを作成"""
        db_obj = User(
            email=obj_in.email,
            name=obj_in.name,
            oauth_provider=obj_in.oauth_provider,
            oauth_id=obj_in.oauth_id,
            github_username=obj_in.github_username,
            github_avatar_url=obj_in.github_avatar_url,
            is_active=True,
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj


    def authenticate(self, email: str, password: str) -> Optional[User]:
        """パスワード認証"""
        user = self.get_by_email(self.db, email=email)
        if not user:
            return None
        if not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


    def update_login_time(self, user: User) -> User:
        """最終ログイン日時を更新"""
        from datetime import datetime
        user.last_login = datetime.utcnow()
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


    def update_refresh_token(self, user: User, 
                            token: Optional[str], expires: Optional[datetime]) -> User:
        """リフレッシュトークンを更新"""
        user.refresh_token = token
        user.token_expires = expires
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user