from typing import Dict, Any, Optional, List
from app.core.firebase_utils import (
    get_document, 
    get_documents,
    add_document, 
    update_document, 
    delete_document
)

USERS_COLLECTION = "users"

class UserService:
    """ユーザー関連のビジネスロジックを処理するサービス"""
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """指定されたIDのユーザーを取得する"""
        user_data = get_document(USERS_COLLECTION, user_id)
        if not user_data:
            return None
            
        return {
            "id": user_id,
            **user_data
        }
    
    @staticmethod
    def get_users(filters: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        """条件に一致するユーザーのリストを取得する"""
        return get_documents(USERS_COLLECTION, filters)
    
    @staticmethod
    def create_user(user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """新しいユーザーをFirestoreに作成する"""
        # ユーザーデータからIDフィールドを削除（もし存在する場合）
        if "id" in user_data:
            del user_data["id"]
            
        # ユーザーデータを保存
        add_document(USERS_COLLECTION, user_data, user_id)
        
        # 保存したデータを返却
        return {
            "id": user_id,
            **user_data
        }
    
    @staticmethod
    def update_user(user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """ユーザー情報を更新する"""
        # IDフィールドが含まれている場合は削除
        if "id" in update_data:
            del update_data["id"]
        
        # 現在のデータを取得して存在確認
        current_user = get_document(USERS_COLLECTION, user_id)
        if not current_user:
            raise ValueError(f"User {user_id} not found")
        
        # 更新するフィールドだけを更新
        update_document(USERS_COLLECTION, user_id, update_data)
        
        # 更新後のデータを取得して返却
        updated_user = get_document(USERS_COLLECTION, user_id)
        return {
            "id": user_id,
            **updated_user
        }
    
    @staticmethod
    def delete_user(user_id: str) -> bool:
        """ユーザーを削除する"""
        # 存在確認
        user = get_document(USERS_COLLECTION, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # 削除実行
        delete_document(USERS_COLLECTION, user_id)
        return True
    
    @staticmethod
    def user_exists(user_id: str) -> bool:
        """ユーザーが存在するか確認する"""
        user = get_document(USERS_COLLECTION, user_id)
        return user is not None