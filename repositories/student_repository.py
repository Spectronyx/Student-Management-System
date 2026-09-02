from typing import Optional, Dict, Any, List
from repositories.base_repository import BaseRepository

class StudentRepository(BaseRepository):
    """Repository for Student entity SQL operations."""

    def add_student(self, user_id: int, roll_number: str, first_name: str, last_name: str,
                    dob: str, gender: str, email: str, phone: str, address: str,
                    department_id: int, course_id: int, semester: int, admission_date: str) -> int:
        query = """
            INSERT INTO students (
                user_id, roll_number, first_name, last_name, dob, gender,
                email, phone, address, department_id, course_id, semester, admission_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_insert(query, (
            user_id, roll_number, first_name, last_name, dob, gender,
            email, phone, address, department_id, course_id, semester, admission_date
        ))

    def get_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT s.*, d.department_name, c.course_name
            FROM students s
            JOIN departments d ON s.department_id = d.department_id
            JOIN courses c ON s.course_id = c.course_id
            WHERE s.student_id = %s
        """
        return self.fetch_one(query, (student_id,))

    def get_by_roll_number(self, roll_number: str) -> Optional[Dict[str, Any]]:
        query = """
            SELECT s.*, d.department_name, c.course_name
            FROM students s
            JOIN departments d ON s.department_id = d.department_id
            JOIN courses c ON s.course_id = c.course_id
            WHERE s.roll_number = %s
        """
        return self.fetch_one(query, (roll_number,))

    def get_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT s.*, d.department_name, c.course_name
            FROM students s
            JOIN departments d ON s.department_id = d.department_id
            JOIN courses c ON s.course_id = c.course_id
            WHERE s.user_id = %s
        """
        return self.fetch_one(query, (user_id,))

    def get_all_students(self) -> List[Dict[str, Any]]:
        query = """
            SELECT s.student_id, s.roll_number, CONCAT(s.first_name, ' ', s.last_name) AS full_name,
                   s.email, s.phone, s.gender, d.department_name, c.course_name, s.semester
            FROM students s
            JOIN departments d ON s.department_id = d.department_id
            JOIN courses c ON s.course_id = c.course_id
            ORDER BY s.student_id DESC
        """
        return self.execute_query(query)

    def search_students(self, term: str) -> List[Dict[str, Any]]:
        like_term = f"%{term}%"
        query = """
            SELECT s.student_id, s.roll_number, CONCAT(s.first_name, ' ', s.last_name) AS full_name,
                   s.email, s.phone, d.department_name, c.course_name, s.semester
            FROM students s
            JOIN departments d ON s.department_id = d.department_id
            JOIN courses c ON s.course_id = c.course_id
            WHERE s.roll_number LIKE %s 
               OR s.first_name LIKE %s 
               OR s.last_name LIKE %s
               OR s.email LIKE %s
            ORDER BY s.student_id DESC
        """
        return self.execute_query(query, (like_term, like_term, like_term, like_term))

    def update_student(self, student_id: int, fields: Dict[str, Any]) -> bool:
        if not fields:
            return False
        set_clauses = [f"{k} = %s" for k in fields.keys()]
        values = list(fields.values())
        values.append(student_id)
        query = f"UPDATE students SET {', '.join(set_clauses)} WHERE student_id = %s"
        return self.execute_update_delete(query, tuple(values)) > 0

    def delete_student(self, student_id: int) -> bool:
        # Also deletes user account due to ON DELETE CASCADE
        student = self.get_by_id(student_id)
        if not student:
            return False
        user_id = student['user_id']
        query = "DELETE FROM users WHERE user_id = %s"
        return self.execute_update_delete(query, (user_id,)) > 0

    def get_department_students(self, department_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT s.student_id, s.roll_number, CONCAT(s.first_name, ' ', s.last_name) AS full_name,
                   s.email, c.course_name, s.semester
            FROM students s
            JOIN courses c ON s.course_id = c.course_id
            WHERE s.department_id = %s
            ORDER BY s.roll_number
        """
        return self.execute_query(query, (department_id,))

    def get_course_students(self, course_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT s.student_id, s.roll_number, CONCAT(s.first_name, ' ', s.last_name) AS full_name,
                   s.email, s.semester
            FROM students s
            WHERE s.course_id = %s
            ORDER BY s.roll_number
        """
        return self.execute_query(query, (course_id,))
