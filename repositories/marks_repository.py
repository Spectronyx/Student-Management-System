from typing import Optional, Dict, Any, List
from repositories.base_repository import BaseRepository

class MarksRepository(BaseRepository):
    """Repository for Examinations and Marks SQL database operations."""

    def create_examination(self, exam_name: str, course_id: int, semester: int, exam_date: str, total_marks: float = 100.0) -> int:
        query = """
            INSERT INTO examinations (exam_name, course_id, semester, exam_date, total_marks)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_insert(query, (exam_name, course_id, semester, exam_date, total_marks))

    def get_examinations(self, course_id: Optional[int] = None, semester: Optional[int] = None) -> List[Dict[str, Any]]:
        if course_id and semester:
            query = """
                SELECT e.*, c.course_name
                FROM examinations e
                JOIN courses c ON e.course_id = c.course_id
                WHERE e.course_id = %s AND e.semester = %s
                ORDER BY e.exam_date DESC
            """
            return self.execute_query(query, (course_id, semester))
        query = """
            SELECT e.*, c.course_name
            FROM examinations e
            JOIN courses c ON e.course_id = c.course_id
            ORDER BY e.exam_date DESC
        """
        return self.execute_query(query)

    def get_examination_by_id(self, exam_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT e.*, c.course_name
            FROM examinations e
            JOIN courses c ON e.course_id = c.course_id
            WHERE e.exam_id = %s
        """
        return self.fetch_one(query, (exam_id,))

    def enter_marks(self, exam_id: int, subject_id: int, student_id: int, marks_obtained: float, grade: str, remarks: str = None) -> int:
        query = """
            INSERT INTO marks (exam_id, subject_id, student_id, marks_obtained, grade, remarks)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE marks_obtained = VALUES(marks_obtained), grade = VALUES(grade), remarks = VALUES(remarks)
        """
        return self.execute_insert(query, (exam_id, subject_id, student_id, marks_obtained, grade, remarks))

    def update_marks(self, mark_id: int, marks_obtained: float, grade: str, remarks: str = None) -> bool:
        query = "UPDATE marks SET marks_obtained = %s, grade = %s, remarks = %s WHERE mark_id = %s"
        return self.execute_update_delete(query, (marks_obtained, grade, remarks, mark_id)) > 0

    def get_student_marks(self, student_id: int, exam_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if exam_id:
            query = """
                SELECT m.*, sub.subject_code, sub.subject_name, e.exam_name, e.total_marks
                FROM marks m
                JOIN subjects sub ON m.subject_id = sub.subject_id
                JOIN examinations e ON m.exam_id = e.exam_id
                WHERE m.student_id = %s AND m.exam_id = %s
                ORDER BY sub.subject_code
            """
            return self.execute_query(query, (student_id, exam_id))
        query = """
            SELECT m.*, sub.subject_code, sub.subject_name, e.exam_name, e.total_marks
            FROM marks m
            JOIN subjects sub ON m.subject_id = sub.subject_id
            JOIN examinations e ON m.exam_id = e.exam_id
            WHERE m.student_id = %s
            ORDER BY e.exam_date DESC, sub.subject_code
        """
        return self.execute_query(query, (student_id,))

    def get_student_result_summary(self, student_id: int, exam_id: int) -> Dict[str, Any]:
        """Calculates total marks, percentage, and overall grade for a student in an exam."""
        query = """
            SELECT 
                COUNT(m.mark_id) AS total_subjects,
                SUM(m.marks_obtained) AS total_obtained,
                SUM(e.total_marks) AS total_max_marks,
                ROUND((SUM(m.marks_obtained) / SUM(e.total_marks)) * 100.0, 2) AS overall_percentage
            FROM marks m
            JOIN examinations e ON m.exam_id = e.exam_id
            WHERE m.student_id = %s AND m.exam_id = %s
        """
        return self.fetch_one(query, (student_id, exam_id)) or {}

    def get_course_examination_results(self, exam_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT 
                s.student_id,
                s.roll_number,
                CONCAT(s.first_name, ' ', s.last_name) AS student_name,
                COUNT(m.mark_id) AS total_subjects,
                SUM(m.marks_obtained) AS total_obtained,
                ROUND(AVG(m.marks_obtained), 2) AS average_score
            FROM marks m
            JOIN students s ON m.student_id = s.student_id
            WHERE m.exam_id = %s
            GROUP BY s.student_id, s.roll_number, student_name
            ORDER BY total_obtained DESC
        """
        return self.execute_query(query, (exam_id,))
