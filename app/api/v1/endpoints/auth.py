from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from firebase_admin import firestore

from app.api.dependencies.auth import get_current_user
from app.core.config import settings
from app.core.firebase_utils import create_custom_token, create_user_with_email_password, get_user, update_firebase_user, verify_id_token
from app.schemas.auth import Token, UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter()

@router.get("/github/login")
async def login_github():
    """GitHubログイン用のリダイレクトURL"""
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub OAuth not configured"
        )
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&scope=user:email"
    return RedirectResponse(url=github_auth_url)

@router.get("/github/callback")
async def github_callback(code: str):
    """GitHub OAuth2コールバック処理"""
    # GitHubからアクセストークンを取得
    token_url = "https://github.com/login/oauth/access_token"
    payload = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code
    }
    headers = {"Accept": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(token_url, json=payload, headers=headers)
            github_token_data = response.json()
            if "error" in github_token_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"GitHub OAuth error: {github_token_data['error']}"
                )
                
            github_token = github_token_data["access_token"]
            
            # GitHubユーザー情報を取得
            user_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {github_token}",
                    "Accept": "application/json"
                }
            )
            user_data = user_response.json()
            
            try:
                # GitHubユーザーIDをFirebaseのユーザーIDとして使用
                firebase_uid = f"github_{user_data['id']}"
                
                # メールアドレスを取得（GitHubから取得できる場合）
                email = user_data.get('email')
                
                # メールアドレスが非公開の場合、追加のAPIコールで取得を試みる
                if not email:
                    emails_response = await client.get(
                        "https://api.github.com/user/emails",
                        headers={
                            "Authorization": f"token {github_token}",
                            "Accept": "application/json"
                        }
                    )
                    emails_data = emails_response.json()
                    # プライマリーメールを探す
                    for email_obj in emails_data:
                        if email_obj.get('primary'):
                            email = email_obj.get('email')
                            break
                
                # # Firebase認証にユーザーが存在するか確認
                try:
                    get_user(firebase_uid)
                except Exception:
                    # ユーザーが存在しない場合は無視
                    pass
                
                # # ユーザーがFirebaseに存在しない場合、カスタムクレームを作成
                user_claims = {
                    "github_id": user_data['id'],
                    "github_username": user_data['login'],
                    "avatar_url": user_data.get('avatar_url'),
                    "name": user_data.get('name')
                }
                
                # カスタムトークンを生成
                custom_token = create_custom_token(firebase_uid, user_claims)
                
                # # Firestoreにユーザーデータを保存/更新
                user_profile = {
                    "id": str(user_data['id']),
                    "username": user_data['login'],
                    "display_name": user_data.get('name') or user_data['login'],
                    "email": email,
                    "photo_url": user_data.get('avatar_url'),
                    "bio": user_data.get('bio'),
                    "auth_provider": "github",
                    "last_login": firestore.SERVER_TIMESTAMP,
                    "updated_at": firestore.SERVER_TIMESTAMP
                }
                
                if not UserService.user_exists(firebase_uid):
                    # 新規ユーザーの場合、作成日時を追加
                    user_profile["created_at"] = firestore.SERVER_TIMESTAMP
                    UserService.create_user(firebase_uid, user_profile)
                else:
                    # 既存ユーザーの場合、データを更新
                    UserService.update_user(firebase_uid, user_profile)
                
                # フロントエンドにリダイレクト（カスタムトークンを含む）
                redirect_url = f"{settings.FRONTEND_REDIRECT_URL}?token={custom_token}"
                
                return RedirectResponse(url=redirect_url)
            except Exception as e:
                # エラーが発生した場合、必要最低限の情報をフロントエンドに渡す
                error_redirect = f"{settings.FRONTEND_REDIRECT_URL}?error=firebase_auth_error&message={str(e)}"
                return RedirectResponse(url=error_redirect)
    except Exception as e:
        print(f"Exception in GitHub callback: {str(e)}")
        error_redirect = f"{settings.FRONTEND_REDIRECT_URL}?error=server_error&message={str(e)}"
        return RedirectResponse(url=error_redirect, status_code=302)

@router.post("/verify", response_model=Dict[str, Any])
async def verify_token(token: Token):
    """Firebase IDトークンを検証"""
    try:
        decoded_token = verify_id_token(token.id_token)
        return {"valid": True, "uid": decoded_token["uid"], "payload": decoded_token}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """新規ユーザーを登録"""
    try:
        # Firebase Authでユーザー作成
        firebase_user = create_user_with_email_password(
            user_data.email, 
            user_data.password, 
            user_data.display_name
        )
        
        # Firestoreにユーザープロフィール作成
        user_profile = {
            "username": "",
            "email": user_data.email,
            "display_name": user_data.display_name or user_data.email.split("@")[0],
            "photo_url": "",                                           # 空文字列で初期化
            "bio": "",                                                 # 空文字列で初期化
            "auth_provider": "email",
            "last_login": firestore.SERVER_TIMESTAMP,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        UserService.create_user(firebase_user["uid"], user_profile)
        
        return {
            "id": firebase_user["uid"],
            "email": firebase_user["email"],
            "display_name": firebase_user["display_name"],
            "photo_url": firebase_user["photo_url"]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ユーザー登録エラー: {str(e)}"
        )

@router.put("/update-profile", response_model=UserResponse)
async def update_profile(
    display_name: str = None, 
    photo_url: str = None,
    current_user = Depends(get_current_user)
):
    """ユーザープロフィールを更新"""
    properties = {}
    if display_name:
        properties["display_name"] = display_name
    if photo_url:
        properties["photo_url"] = photo_url
    
    if not properties:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="更新するプロパティが指定されていません"
        )
    
    try:
        # Firebase Authユーザー情報を更新
        updated_user = update_firebase_user(current_user.uid, properties)
        
        # Firestoreのプロフィールも更新
        user_profile_update = {
            **properties,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        UserService.update_user(current_user.uid, user_profile_update)
        
        return {
            "id": updated_user["uid"],
            "email": updated_user["email"],
            "display_name": updated_user["display_name"],
            "photo_url": updated_user["photo_url"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"プロフィール更新エラー: {str(e)}"
        )