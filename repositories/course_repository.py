from typing import Optional, Dict, Any, List
from repositories.base_repository import BaseRepository

class CourseRepository(BaseRepository):
    """Repository for Department, Course, Subject, and Enrollment SQL operations."""

    # --- DEPARTMENT OPERATIONS ---
    def add_department(self, code: str, name: str) -> int:
        query = "INSERT INTO departments (department_code, department_name) VALUES (%s, %s)"
        return self.execute_insert(query, (code, name))

    def get_all_departments(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM departments ORDER BY department_name"
        return self.execute_query(query)

    def get_department_by_id(self, dept_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM departments WHERE department_id = %s"
        return self.fetch_one(query, (dept_id,))

    def get_department_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM departments WHERE department_code = %s"
        return self.fetch_one(query, (code,))

    # --- COURSE OPERATIONS ---
    def add_course(self, code: str, name: str, dept_id: int, credits: int) -> int:
        query = "INSERT INTO courses (course_code, course_name, department_id, credits) VALUES (%s, %s, %s, %s)"
        return self.execute_insert(query, (code, name, dept_id, credits))

    def get_all_courses(self) -> List[Dict[str, Any]]:
        query = """
            SELECT c.*, d.department_name
            FROM courses c
            JOIN departments d ON c.department_id = d.department_id
            ORDER BY c.course_name
        """
        return self.execute_query(query)

    def get_course_by_id(self, course_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT c.*, d.department_name
            FROM courses c
            JOIN departments d ON c.department_id = d.department_id
            WHERE c.course_id = %s
        """
        return self.fetch_one(query, (course_id,))

    def get_courses_by_department(self, dept_id: int) -> List[Dict[str, Any]]:
        query = "SELECT * FROM courses WHERE department_id = %s ORDER BY course_name"
        return self.execute_query(query, (dept_id,))

    def update_course(self, course_id: int, fields: Dict[str, Any]) -> bool:
        if not fields:
            return False
        set_clauses = [f"{k} = %s" for k in fields.keys()]
        values = list(fields.values())
        values.append(course_id)
        query = f"UPDATE courses SET {', '.join(set_clauses)} WHERE course_id = %s"
        return self.execute_update_delete(query, tuple(values)) > 0

    def delete_course(self, course_id: int) -> bool:
        query = "DELETE FROM courses WHERE course_id = %s"
        return self.execute_update_delete(query, (course_id,)) > 0

    # --- SUBJECT OPERATIONS ---
    def add_subject(self, code: str, name: str, course_id: int, semester: int, credits: int) -> int:
        query = """
            INSERT INTO subjects (subject_code, subject_name, course_id, semester, credits)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_insert(query, (code, name, course_id, semester, credits))

    def get_subjects_by_course(self, course_id: int, semester: Optional[int] = None) -> List[Dict[str, Any]]:
        if semester:
            query = "SELECT * FROM subjects WHERE course_id = %s AND semester = %s ORDER BY subject_code"
            return self.execute_query(query, (course_id, semester))
        query = "SELECT * FROM subjects WHERE course_id = %s ORDER BY semester, subject_code"
        return self.execute_query(query, (course_id,))

    # --- ENROLLMENT OPERATIONS ---
    def enroll_student(self, student_id: int, course_id: int, semester: int, date_str: str) -> int:
        query = """
            INSERT INTO enrollments (student_id, course_id, semester, enrollment_date, status)
            VALUES (%s, %s, %s, %s, 'Active')
            ON DUPLICATE KEY UPDATE status = 'Active'
        """
        return self.execute_insert(query, (student_id, course_id, semester, date_str))
