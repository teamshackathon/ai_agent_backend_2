from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas import user as schemas
from app.services.user_service import UserService

router = APIRouter()

def get_user_service(db: Session = Depends(deps.get_db)) -> UserService:
    """
    ユーザーサービスの依存関係
    """
    return UserService(db=db)

# 自分のユーザー情報を取得するエンドポイント
@router.get("/me", response_model=schemas.UserMe)
def read_users_me(current_user = Depends(deps.get_current_user)) -> Any:
    """
    現在ログインしているユーザー情報を取得
    """
    # 返却するカラムを制限
    current_user = schemas.User.from_orm(current_user)
    return current_user

# ユーザー情報を更新するエンドポイント
@router.put("/me", response_model=schemas.UserMe)
def update_user_me(
    user_update: schemas.UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    現在ログインしているユーザー情報を更新
    """
    updated_user = user_service.update(db_obj=current_user, obj_in=user_update)
    return schemas.UserMe.from_orm(updated_user)