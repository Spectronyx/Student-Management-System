from fastapi import APIRouter, Depends
from schemas.api_schemas import StandardResponse
from database import fetch_all, fetch_one
from utils.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/subject-performance", response_model=StandardResponse)
def get_subject_performance_analytics(current_user: dict = Depends(get_current_user)):
    """Computes average class performance per subject."""
    stats = fetch_all("""
        SELECT 
            sub.subject_id,
            sub.subject_code,
            sub.subject_name,
            sub.credits,
            COUNT(m.mark_id) AS total_enrolled,
            ROUND(AVG(m.total_marks), 2) AS average_score,
            MAX(m.total_marks) AS max_score,
            MIN(m.total_marks) AS min_score,
            SUM(CASE WHEN m.grade = 'A+' THEN 1 ELSE 0 END) AS count_a_plus,
            SUM(CASE WHEN m.grade = 'A' THEN 1 ELSE 0 END) AS count_a,
            SUM(CASE WHEN m.grade = 'B+' THEN 1 ELSE 0 END) AS count_b_plus,
            SUM(CASE WHEN m.grade = 'F' THEN 1 ELSE 0 END) AS count_f
        FROM subjects sub
        LEFT JOIN marks m ON sub.subject_id = m.subject_id
        GROUP BY sub.subject_id, sub.subject_code, sub.subject_name, sub.credits
        ORDER BY average_score DESC
    """)

    return StandardResponse(
        success=True,
        message="Subject performance analytics generated",
        data=stats
    )

@router.get("/department-performance", response_model=StandardResponse)
def get_department_performance_analytics(current_user: dict = Depends(get_current_user)):
    """Computes average GPA and attendance across departments."""
    stats = fetch_all("""
        SELECT 
            d.department_id,
            d.department_code,
            d.department_name,
            COUNT(DISTINCT s.student_id) AS total_students,
            ROUND(AVG(m.total_marks), 2) AS avg_department_score,
            ROUND(AVG(a.attendance_percentage), 2) AS avg_department_attendance
        FROM departments d
        LEFT JOIN students s ON d.department_id = s.department_id
        LEFT JOIN marks m ON s.student_id = m.student_id
        LEFT JOIN attendance a ON s.student_id = a.student_id
        GROUP BY d.department_id, d.department_code, d.department_name
    """)

    return StandardResponse(
        success=True,
        message="Department performance analytics generated",
        data=stats
    )

@router.get("/top-students", response_model=StandardResponse)
def get_top_performing_students(limit: int = 5, current_user: dict = Depends(get_current_user)):
    """Retrieves top performing rankers."""
    top_students = fetch_all("""
        SELECT 
            s.student_id,
            s.enrollment_number,
            CONCAT(s.first_name, ' ', s.last_name) AS student_name,
            d.department_code,
            s.course,
            s.semester,
            ROUND(AVG(m.total_marks), 2) AS overall_percentage,
            ROUND(AVG(m.grade_point), 2) AS cgpa
        FROM students s
        JOIN departments d ON s.department_id = d.department_id
        JOIN marks m ON s.student_id = m.student_id
        GROUP BY s.student_id, s.enrollment_number, student_name, d.department_code, s.course, s.semester
        ORDER BY overall_percentage DESC
        LIMIT %s
    """, (limit,))

    return StandardResponse(
        success=True,
        message=f"Retrieved top {len(top_students)} students",
        data=top_students
    )

@router.get("/attendance-warning", response_model=StandardResponse)
def get_attendance_warning_list(threshold: float = 75.0, current_user: dict = Depends(get_current_user)):
    """Retrieves students whose subject or overall attendance is strictly below threshold (< 75%)."""
    warnings = fetch_all("""
        SELECT 
            a.attendance_id,
            s.student_id,
            s.enrollment_number,
            CONCAT(s.first_name, ' ', s.last_name) AS student_name,
            s.email,
            s.phone,
            sub.subject_code,
            sub.subject_name,
            a.classes_held,
            a.classes_attended,
            a.attendance_percentage
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        JOIN subjects sub ON a.subject_id = sub.subject_id
        WHERE a.attendance_percentage < %s
        ORDER BY a.attendance_percentage ASC
    """, (threshold,))

    return StandardResponse(
        success=True,
        message=f"Found {len(warnings)} attendance warning records below {threshold}% threshold",
        data=warnings
    )
