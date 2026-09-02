from typing import Optional, Dict, Any, List
from repositories.base_repository import BaseRepository

class UserRepository(BaseRepository):
    """Repository for User entity database operations."""

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE username = %s"
        return self.fetch_one(query, (username,))

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE user_id = %s"
        return self.fetch_one(query, (user_id,))

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE email = %s"
        return self.fetch_one(query, (email,))

    def create_user(self, username: str, password_hash: str, role: str, email: str) -> int:
        query = """
            INSERT INTO users (username, password_hash, role, email)
            VALUES (%s, %s, %s, %s)
        """
        return self.execute_insert(query, (username, password_hash, role, email))

    def update_password(self, user_id: int, new_password_hash: str) -> bool:
        query = "UPDATE users SET password_hash = %s WHERE user_id = %s"
        return self.execute_update_delete(query, (new_password_hash, user_id)) > 0

    def get_all_users(self) -> List[Dict[str, Any]]:
        query = "SELECT user_id, username, role, email, is_active, created_at FROM users ORDER BY user_id DESC"
        return self.execute_query(query)
