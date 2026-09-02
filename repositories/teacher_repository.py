from typing import Optional, Dict, Any, List
from repositories.base_repository import BaseRepository

class TeacherRepository(BaseRepository):
    """Repository for Teacher entity SQL operations."""

    def add_teacher(self, user_id: int, first_name: str, last_name: str,
                    email: str, phone: str, department_id: int, hire_date: str) -> int:
        query = """
            INSERT INTO teachers (user_id, first_name, last_name, email, phone, department_id, hire_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_insert(query, (user_id, first_name, last_name, email, phone, department_id, hire_date))

    def get_by_id(self, teacher_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT t.*, d.department_name
            FROM teachers t
            JOIN departments d ON t.department_id = d.department_id
            WHERE t.teacher_id = %s
        """
        return self.fetch_one(query, (teacher_id,))

    def get_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT t.*, d.department_name
            FROM teachers t
            JOIN departments d ON t.department_id = d.department_id
            WHERE t.user_id = %s
        """
        return self.fetch_one(query, (user_id,))

    def get_all_teachers(self) -> List[Dict[str, Any]]:
        query = """
            SELECT t.teacher_id, CONCAT(t.first_name, ' ', t.last_name) AS full_name,
                   t.email, t.phone, d.department_name, t.hire_date
            FROM teachers t
            JOIN departments d ON t.department_id = d.department_id
            ORDER BY t.teacher_id DESC
        """
        return self.execute_query(query)
