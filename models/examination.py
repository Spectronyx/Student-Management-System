from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import date

@dataclass
class Examination:
    exam_id: Optional[int]
    exam_name: str
    course_id: int
    semester: int
    exam_date: date
    total_marks: float = 100.0
    course_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exam_id": self.exam_id,
            "exam_name": self.exam_name,
            "course_id": self.course_id,
            "semester": self.semester,
            "exam_date": str(self.exam_date),
            "total_marks": self.total_marks,
            "course_name": self.course_name
        }

@dataclass
class Mark:
    mark_id: Optional[int]
    exam_id: int
    subject_id: int
    student_id: int
    marks_obtained: float
    grade: str
    remarks: Optional[str] = None
    subject_name: Optional[str] = None
    student_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mark_id": self.mark_id,
            "exam_id": self.exam_id,
            "subject_id": self.subject_id,
            "student_id": self.student_id,
            "marks_obtained": self.marks_obtained,
            "grade": self.grade,
            "remarks": self.remarks,
            "subject_name": self.subject_name,
            "student_name": self.student_name
        }
