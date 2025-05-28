from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.schemas.auth import UserResponse
from app.services.user_service import UserService

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    """認証済みユーザーの情報を取得"""
    try:
        # Firebase AuthのユーザーIDを取得
        uid = current_user.uid
        
        # Firestoreからユーザープロファイルを取得
        user_profile = UserService.get_user_by_id(uid)
        
        if user_profile:
            # Firestoreのデータを優先し、不足している部分をFirebase Authから補完
            return {
                "id": uid,
                "email": user_profile.get("email") or current_user.email,
                "display_name": user_profile.get("display_name") or current_user.display_name,
                "photo_url": user_profile.get("photo_url") or current_user.photo_url,
                "username": user_profile.get("username", ""),
                "bio": user_profile.get("bio", ""),
                "auth_provider": user_profile.get("auth_provider", ""),
                "created_at": user_profile.get("created_at"),
                "last_login": user_profile.get("last_login")
            }
        else:
            # Firestoreにデータがない場合はFirebase Authのデータのみを返す
            return {
                "id": current_user.uid,
                "email": current_user.email,
                "display_name": current_user.display_name,
                "photo_url": current_user.photo_url
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ユーザー情報の取得に失敗しました: {str(e)}"
        )