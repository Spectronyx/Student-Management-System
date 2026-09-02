from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import date

@dataclass
class Attendance:
    attendance_id: Optional[int]
    student_id: int
    course_id: int
    date: date
    status: str  # 'Present', 'Absent', 'Late', 'Excused'
    remarks: Optional[str] = None
    student_name: Optional[str] = None
    course_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attendance_id": self.attendance_id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "date": str(self.date),
            "status": self.status,
            "remarks": self.remarks,
            "student_name": self.student_name,
            "course_name": self.course_name
        }
