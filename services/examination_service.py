from typing import Optional, Dict, Any, List
from repositories.marks_repository import MarksRepository
from repositories.student_repository import StudentRepository
from repositories.course_repository import CourseRepository
from utils.validators import validate_marks, validate_date, validate_required, ValidationError
from utils.helpers import calculate_grade

class ExaminationService:
    """Service handling Examinations, Marks entry, centralized Grading, and Result Cards."""

    def __init__(self):
        self.marks_repo = MarksRepository()
        self.student_repo = StudentRepository()
        self.course_repo = CourseRepository()

    def create_examination(self, exam_name: str, course_id: int, semester: int, exam_date_input: str, total_marks: float = 100.0) -> int:
        name = validate_required(exam_name, "Examination Name")
        exam_date = validate_date(exam_date_input, "Examination Date")

        if not self.course_repo.get_course_by_id(course_id):
            raise ValidationError(f"Course ID {course_id} does not exist.")

        return self.marks_repo.create_examination(name, course_id, int(semester), str(exam_date), float(total_marks))

    def list_examinations(self, course_id: Optional[int] = None, semester: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.marks_repo.get_examinations(course_id, semester)

    def enter_marks(self, exam_id: int, subject_id: int, student_id: int, marks_obtained_input: float, remarks: str = None) -> int:
        marks_obtained = validate_marks(marks_obtained_input)

        exam = self.marks_repo.get_examination_by_id(exam_id)
        if not exam:
            raise ValidationError(f"Examination ID {exam_id} not found.")

        if not self.student_repo.get_by_id(student_id):
            raise ValidationError(f"Student ID {student_id} not found.")

        # Calculate grade using centralized logic
        total_marks = float(exam['total_marks'])
        if marks_obtained > total_marks:
            raise ValidationError(f"Marks obtained ({marks_obtained}) cannot exceed total exam marks ({total_marks}).")

        percentage, grade = calculate_grade(marks_obtained, total_marks)

        return self.marks_repo.enter_marks(exam_id, subject_id, student_id, marks_obtained, grade, remarks)

    def get_student_marks(self, student_id: int, exam_id: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.marks_repo.get_student_marks(student_id, exam_id)

    def generate_student_result(self, student_id: int, exam_id: int) -> Dict[str, Any]:
        """Generates a complete report card for a student for a specific examination."""
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise ValidationError(f"Student ID {student_id} not found.")

        exam = self.marks_repo.get_examination_by_id(exam_id)
        if not exam:
            raise ValidationError(f"Examination ID {exam_id} not found.")

        marks_list = self.marks_repo.get_student_marks(student_id, exam_id)
        summary = self.marks_repo.get_student_result_summary(student_id, exam_id)

        overall_pct = float(summary.get('overall_percentage') or 0.0)
        overall_grade = calculate_grade(overall_pct)[1]
        status = "PASSED" if overall_pct >= 40.0 and all(m['grade'] != 'F' for m in marks_list) else "FAILED"

        return {
            "student_info": student,
            "exam_info": exam,
            "subject_marks": marks_list,
            "summary": {
                "total_subjects": summary.get('total_subjects', 0),
                "total_obtained": float(summary.get('total_obtained') or 0.0),
                "total_max_marks": float(summary.get('total_max_marks') or 0.0),
                "overall_percentage": overall_pct,
                "overall_grade": overall_grade,
                "status": status
            }
        }
