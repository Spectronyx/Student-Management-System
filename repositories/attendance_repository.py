from typing import Optional, Dict, Any, List
from repositories.base_repository import BaseRepository

class AttendanceRepository(BaseRepository):
    """Repository for Attendance tracking database operations."""

    def mark_attendance(self, student_id: int, course_id: int, date_str: str, status: str, remarks: str = None) -> int:
        query = """
            INSERT INTO attendance (student_id, course_id, date, status, remarks)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE status = VALUES(status), remarks = VALUES(remarks)
        """
        return self.execute_insert(query, (student_id, course_id, date_str, status, remarks))

    def update_attendance(self, attendance_id: int, status: str, remarks: str = None) -> bool:
        query = "UPDATE attendance SET status = %s, remarks = %s WHERE attendance_id = %s"
        return self.execute_update_delete(query, (status, remarks, attendance_id)) > 0

    def get_student_attendance(self, student_id: int, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if course_id:
            query = """
                SELECT a.*, c.course_name
                FROM attendance a
                JOIN courses c ON a.course_id = c.course_id
                WHERE a.student_id = %s AND a.course_id = %s
                ORDER BY a.date DESC
            """
            return self.execute_query(query, (student_id, course_id))
        query = """
            SELECT a.*, c.course_name
            FROM attendance a
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.student_id = %s
            ORDER BY a.date DESC
        """
        return self.execute_query(query, (student_id,))

    def get_course_attendance(self, course_id: int, date_str: Optional[str] = None) -> List[Dict[str, Any]]:
        if date_str:
            query = """
                SELECT a.*, s.roll_number, CONCAT(s.first_name, ' ', s.last_name) AS student_name
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.course_id = %s AND a.date = %s
                ORDER BY s.roll_number
            """
            return self.execute_query(query, (course_id, date_str))
        query = """
            SELECT a.*, s.roll_number, CONCAT(s.first_name, ' ', s.last_name) AS student_name
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.course_id = %s
            ORDER BY a.date DESC, s.roll_number
        """
        return self.execute_query(query, (course_id,))

    def get_attendance_summary(self, student_id: int) -> Dict[str, Any]:
        """Calculates attendance statistics for a specific student."""
        query = """
            SELECT 
                COUNT(*) AS total_classes,
                SUM(CASE WHEN status IN ('Present', 'Late') THEN 1 ELSE 0 END) AS total_attended,
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) AS total_absent,
                ROUND((SUM(CASE WHEN status IN ('Present', 'Late') THEN 1 ELSE 0 END) / COUNT(*)) * 100.0, 2) AS attendance_percentage
            FROM attendance
            WHERE student_id = %s
        """
        result = self.fetch_one(query, (student_id,))
        if not result or result['total_classes'] == 0:
            return {
                "total_classes": 0,
                "total_attended": 0,
                "total_absent": 0,
                "attendance_percentage": 0.0
            }
        return result

    def get_low_attendance_students(self, threshold_pct: float = 75.0) -> List[Dict[str, Any]]:
        """Identifies students whose attendance is strictly below the given percentage threshold."""
        query = """
            SELECT 
                s.student_id,
                s.roll_number,
                CONCAT(s.first_name, ' ', s.last_name) AS student_name,
                c.course_name,
                COUNT(a.attendance_id) AS total_classes,
                SUM(CASE WHEN a.status IN ('Present', 'Late') THEN 1 ELSE 0 END) AS total_attended,
                ROUND((SUM(CASE WHEN a.status IN ('Present', 'Late') THEN 1 ELSE 0 END) / COUNT(a.attendance_id)) * 100.0, 2) AS attendance_pct
            FROM students s
            JOIN courses c ON s.course_id = c.course_id
            JOIN attendance a ON s.student_id = a.student_id
            GROUP BY s.student_id, s.roll_number, student_name, c.course_name
            HAVING attendance_pct < %s
            ORDER BY attendance_pct ASC
        """
        return self.execute_query(query, (threshold_pct,))
