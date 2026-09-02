from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import date

@dataclass
class Student:
    student_id: Optional[int]
    user_id: int
    roll_number: str
    first_name: str
    last_name: str
    dob: date
    gender: str  # 'Male', 'Female', 'Other'
    email: str
    phone: str
    address: str
    department_id: int
    course_id: int
    semester: int
    admission_date: date
    department_name: Optional[str] = None
    course_name: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "user_id": self.user_id,
            "roll_number": self.roll_number,
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "dob": str(self.dob),
            "gender": self.gender,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "department_id": self.department_id,
            "department_name": self.department_name,
            "course_id": self.course_id,
            "course_name": self.course_name,
            "semester": self.semester,
            "admission_date": str(self.admission_date)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        return cls(
            student_id=data.get('student_id'),
            user_id=data.get('user_id', 0),
            roll_number=data.get('roll_number', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            dob=data.get('dob'),
            gender=data.get('gender', 'Male'),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            department_id=data.get('department_id', 0),
            course_id=data.get('course_id', 0),
            semester=data.get('semester', 1),
            admission_date=data.get('admission_date'),
            department_name=data.get('department_name'),
            course_name=data.get('course_name')
        )
