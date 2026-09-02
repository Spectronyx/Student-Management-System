from typing import Optional, Dict, Any, List
from repositories.course_repository import CourseRepository
from utils.validators import validate_required, ValidationError

class CourseService:
    """Service handling Department, Course, and Subject business logic."""

    def __init__(self):
        self.course_repo = CourseRepository()

    def add_department(self, code: str, name: str) -> Dict[str, Any]:
        c_code = validate_required(code, "Department Code").upper()
        c_name = validate_required(name, "Department Name")

        if self.course_repo.get_department_by_code(c_code):
            raise ValidationError(f"Department with code '{c_code}' already exists.")

        dept_id = self.course_repo.add_department(c_code, c_name)
        return self.course_repo.get_department_by_id(dept_id)

    def list_departments(self) -> List[Dict[str, Any]]:
        return self.course_repo.get_all_departments()

    def add_course(self, code: str, name: str, department_id: int, credits: int = 3) -> Dict[str, Any]:
        c_code = validate_required(code, "Course Code").upper()
        c_name = validate_required(name, "Course Name")
        credits_val = int(credits)

        if not self.course_repo.get_department_by_id(department_id):
            raise ValidationError(f"Department ID {department_id} does not exist.")

        course_id = self.course_repo.add_course(c_code, c_name, department_id, credits_val)
        return self.course_repo.get_course_by_id(course_id)

    def list_courses(self) -> List[Dict[str, Any]]:
        return self.course_repo.get_all_courses()

    def add_subject(self, code: str, name: str, course_id: int, semester: int, credits: int = 3) -> int:
        s_code = validate_required(code, "Subject Code").upper()
        s_name = validate_required(name, "Subject Name")
        
        if not self.course_repo.get_course_by_id(course_id):
            raise ValidationError(f"Course ID {course_id} does not exist.")

        return self.course_repo.add_subject(s_code, s_name, course_id, int(semester), int(credits))

    def get_subjects_for_course(self, course_id: int, semester: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.course_repo.get_subjects_by_course(course_id, semester)
