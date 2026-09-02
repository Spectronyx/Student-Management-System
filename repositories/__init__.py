from .base_repository import BaseRepository
from .user_repository import UserRepository
from .student_repository import StudentRepository
from .teacher_repository import TeacherRepository
from .course_repository import CourseRepository
from .attendance_repository import AttendanceRepository
from .marks_repository import MarksRepository
from .fee_repository import FeeRepository

__all__ = [
    'BaseRepository',
    'UserRepository',
    'StudentRepository',
    'TeacherRepository',
    'CourseRepository',
    'AttendanceRepository',
    'MarksRepository',
    'FeeRepository'
]
