from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import date

@dataclass
class Teacher:
    teacher_id: Optional[int]
    user_id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    department_id: int
    hire_date: date
    department_name: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "teacher_id": self.teacher_id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "department_id": self.department_id,
            "department_name": self.department_name,
            "hire_date": str(self.hire_date)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Teacher':
        return cls(
            teacher_id=data.get('teacher_id'),
            user_id=data.get('user_id', 0),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            department_id=data.get('department_id', 0),
            hire_date=data.get('hire_date'),
            department_name=data.get('department_name')
        )
