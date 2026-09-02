from .user import User
from .student import Student
from .teacher import Teacher
from .course import Department, Course, Subject
from .attendance import Attendance
from .examination import Examination, Mark
from .fees import Fee, Payment

__all__ = [
    'User',
    'Student',
    'Teacher',
    'Department',
    'Course',
    'Subject',
    'Attendance',
    'Examination',
    'Mark',
    'Fee',
    'Payment'
]
