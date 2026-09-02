from typing import Optional, Dict, Any, List
from repositories.attendance_repository import AttendanceRepository
from repositories.student_repository import StudentRepository
from repositories.course_repository import CourseRepository
from utils.validators import validate_date, ValidationError
from config import config

class AttendanceService:
    """Service handling Attendance tracking, percentage calculation, and low-attendance thresholds."""

    def __init__(self):
        self.attendance_repo = AttendanceRepository()
        self.student_repo = StudentRepository()
        self.course_repo = CourseRepository()

    def mark_student_attendance(self, student_id: int, course_id: int, date_input: str, status: str, remarks: str = None) -> int:
        if not self.student_repo.get_by_id(student_id):
            raise ValidationError(f"Student ID {student_id} not found.")

        if not self.course_repo.get_course_by_id(course_id):
            raise ValidationError(f"Course ID {course_id} not found.")

        att_date = validate_date(date_input, "Attendance Date")
        
        valid_statuses = ('Present', 'Absent', 'Late', 'Excused')
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status '{status}'. Must be one of {valid_statuses}.")

        return self.attendance_repo.mark_attendance(student_id, course_id, str(att_date), status, remarks)

    def get_student_attendance_records(self, student_id: int, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.attendance_repo.get_student_attendance(student_id, course_id)

    def get_attendance_percentage(self, student_id: int) -> Dict[str, Any]:
        return self.attendance_repo.get_attendance_summary(student_id)

    def get_low_attendance_students(self, threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        target_threshold = threshold if threshold is not None else config.ATTENDANCE_THRESHOLD
        return self.attendance_repo.get_low_attendance_students(target_threshold)
