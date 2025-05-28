import os
from typing import Any, Dict, List, Optional

import firebase_admin
import jwt
from firebase_admin import auth, credentials, firestore

from app.core.config import settings


# Firebaseプロジェクト初期化
def initialize_firebase():
    """Firebase Adminを初期化する"""
    cred_path = settings.FIREBASE_CREDENTIALS_PATH
    
    is_prod = settings.ENVIRONMENT == "production"

    # すでに初期化済みかチェック
    if not firebase_admin._apps:
        if is_prod:
            print("Initializing Firebase Admin SDK in production mode")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            print("Initializing Firebase Admin SDK in emulator mode")
            cred = credentials.Certificate(cred_path)
            os.environ["FIRESTORE_EMULATOR_HOST"] = "host.docker.internal:8080"
            os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = "host.docker.internal:9099"
            firebase_admin.initialize_app(cred)
    
    return firebase_admin.get_app()

# アプリケーション起動時に初期化
firebase_app = initialize_firebase()
db = firestore.client()
print("Firebase Admin SDK initialized successfully")

# Firestoreのユーティリティ関数
def get_document(collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
    """指定したコレクションから特定のドキュメントを取得する"""
    doc_ref = db.collection(collection).document(doc_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

def get_documents(collection: str, filters: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
    """フィルタ条件に基づいてドキュメントを取得する"""
    query = db.collection(collection)
    
    if filters:
        for field, op, value in filters:
            query = query.where(field, op, value)
    
    docs = query.stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

def add_document(collection: str, data: Dict[str, Any], doc_id: Optional[str] = None) -> str:
    """ドキュメントを追加する"""
    if doc_id:
        db.collection(collection).document(doc_id).set(data)
        return doc_id
    else:
        doc_ref = db.collection(collection).add(data)
        return doc_ref[1].id

def update_document(collection: str, doc_id: str, data: Dict[str, Any]) -> str:
    """ドキュメントを更新する"""
    db.collection(collection).document(doc_id).update(data)
    return doc_id

def delete_document(collection: str, doc_id: str) -> None:
    """ドキュメントを削除する"""
    db.collection(collection).document(doc_id).delete()

# Firebase Authentication関連
def verify_id_token(id_token: str) -> Dict[str, Any]:
    """Firebase IDトークンを検証しデコードする"""
    is_production = settings.ENVIRONMENT == "production"
    
    try:
        if is_production:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        else:
            # エミュレータ環境では署名検証をスキップ
            print("Using Firebase Auth Emulator mode - skipping signature verification")
            # 署名を検証せずにトークンをデコード
            decoded_token = jwt.decode(
                id_token,
                options={"verify_signature": False},
                algorithms=["RS256", "none"]  # nonアルゴリズムも許可
            )
            decoded_token["uid"] = decoded_token.get("sub")
            return decoded_token
            
    except Exception as e:
        print(f"Token verification failed: {str(e)}")
        raise ValueError(f"Invalid Firebase ID token: {str(e)}")

def get_user(uid: str) -> Optional[auth.UserRecord]:
    """Firebase Authユーザーを取得する"""
    try:
        user = auth.get_user(uid)
        return user
    except auth.UserNotFoundError:
        return None

def create_custom_token(uid: str, claims: Optional[Dict[str, Any]] = None) -> str:
    """カスタムトークンを作成する（GitHubOAuth等で使用）"""
    try:
        token_bytes = auth.create_custom_token(uid, claims)
        custom_token = token_bytes.decode('utf-8')
        print(f"Custom token created for UID: {uid}")
        return custom_token
    except Exception as e:
        raise ValueError(f"Error creating custom token: {str(e)}")
    
def create_user_with_email_password(email: str, password: str, display_name: Optional[str] = None) -> Dict[str, Any]:
    """Firebase Authenticationでメールパスワードでユーザーを作成"""
    try:
        user_properties = {
            "email": email,
            "password": password,
            "email_verified": False,
        }
        
        if display_name:
            user_properties["display_name"] = display_name
            
        user = auth.create_user(**user_properties)
        return {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "photo_url": user.photo_url
        }
    except auth.EmailAlreadyExistsError:
        raise ValueError("このメールアドレスは既に使用されています")
    except Exception as e:
        raise ValueError(f"ユーザー作成エラー: {str(e)}")

def delete_firebase_user(uid: str) -> None:
    """Firebaseユーザーを削除する"""
    auth.delete_user(uid)

def update_firebase_user(uid: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    """Firebaseユーザーを更新する"""
    user = auth.update_user(uid, **properties)
    return {
        "uid": user.uid,
        "email": user.email,
        "display_name": user.display_name,
        "photo_url": user.photo_url
    }

def send_password_reset_email(email: str) -> None:
    """パスワードリセットメールを送信する"""
    # 注意: これはAdmin SDKでは直接サポートされていません
    # フロントエンドからFirebase Auth SDKを使用するか、
    # Firebase Auth REST APIを使用する必要があります
    raise NotImplementedError("Admin SDKでは直接パスワードリセットメールを送信できません")

def send_email_verification(uid: str) -> None:
    """メール検証リンクを送信する"""
    # 注意: これはAdmin SDKでは直接サポートされていません
    raise NotImplementedError("Admin SDKでは直接検証メールを送信できません")