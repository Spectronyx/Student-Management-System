from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Department:
    department_id: Optional[int]
    department_code: str
    department_name: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "department_id": self.department_id,
            "department_code": self.department_code,
            "department_name": self.department_name
        }

@dataclass
class Course:
    course_id: Optional[int]
    course_code: str
    course_name: str
    department_id: int
    credits: int = 3
    department_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "course_id": self.course_id,
            "course_code": self.course_code,
            "course_name": self.course_name,
            "department_id": self.department_id,
            "credits": self.credits,
            "department_name": self.department_name
        }

@dataclass
class Subject:
    subject_id: Optional[int]
    subject_code: str
    subject_name: str
    course_id: int
    semester: int = 1
    credits: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "subject_code": self.subject_code,
            "subject_name": self.subject_name,
            "course_id": self.course_id,
            "semester": self.semester,
            "credits": self.credits
        }
