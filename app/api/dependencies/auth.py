from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.firebase_utils import get_user, verify_id_token

# OAuth2のトークンスキーマを設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """現在認証されているユーザーを取得"""
    try:
        # Firebase IDトークンを検証
        decoded_token = verify_id_token(token)
        uid = decoded_token["uid"]
        
        # Firebaseからユーザー情報を取得
        firebase_user = get_user(uid)
        if not firebase_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firebase user not found",
            )
        
        return firebase_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
        )

async def get_current_active_user(current_user = Depends(get_current_user)):
    """アクティブな認証済みユーザーを取得"""
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user