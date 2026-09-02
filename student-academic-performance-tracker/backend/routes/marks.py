from fastapi import APIRouter, HTTPException, status, Depends
from schemas.api_schemas import MarkEntryRequest, MarkUpdateRequest, StandardResponse
from database import fetch_all, fetch_one, execute_query
from services.gpa_service import calculate_grade_and_point
from utils.dependencies import get_current_user, require_role

router = APIRouter(prefix="/marks", tags=["Marks"])

@router.get("/student/{student_id}", response_model=StandardResponse)
def get_marks_for_student(student_id: int, current_user: dict = Depends(get_current_user)):
    """Retrieves all mark records for a student."""
    marks = fetch_all("""
        SELECT m.*, sub.subject_code, sub.subject_name, sub.credits
        FROM marks m
        JOIN subjects sub ON m.subject_id = sub.subject_id
        WHERE m.student_id = %s
        ORDER BY sub.subject_code
    """, (student_id,))

    return StandardResponse(
        success=True,
        message=f"Retrieved {len(marks)} mark records for student ID {student_id}",
        data=marks
    )

@router.get("/subject/{subject_id}", response_model=StandardResponse)
def get_marks_for_subject(subject_id: int, current_user: dict = Depends(get_current_user)):
    """Retrieves all student mark records for a subject."""
    marks = fetch_all("""
        SELECT m.*, s.enrollment_number, s.first_name, s.last_name, u.name AS student_name
        FROM marks m
        JOIN students s ON m.student_id = s.student_id
        JOIN users u ON s.user_id = u.user_id
        WHERE m.subject_id = %s
        ORDER BY s.enrollment_number
    """, (subject_id,))

    return StandardResponse(
        success=True,
        message=f"Retrieved {len(marks)} mark records for subject ID {subject_id}",
        data=marks
    )

@router.post("", response_model=StandardResponse)
def add_or_update_marks(
    req: MarkEntryRequest,
    current_user: dict = Depends(require_role("Admin", "Faculty"))
):
    """
    Enters student subject marks.
    Backend automatically calculates total_marks, letter grade, and grade_point.
    """
    # Verify student & subject
    student = fetch_one("SELECT student_id FROM students WHERE student_id = %s", (req.student_id,))
    if not student:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Student not found", "error": "STUDENT_NOT_FOUND"})

    subject = fetch_one("SELECT subject_id, semester FROM subjects WHERE subject_id = %s", (req.subject_id,))
    if not subject:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Subject not found", "error": "SUBJECT_NOT_FOUND"})

    # If Faculty, check subject assignment
    if current_user["role"] == "Faculty":
        faculty = fetch_one("SELECT faculty_id FROM faculty WHERE user_id = %s", (current_user["user_id"],))
        if faculty:
            assignment = fetch_one("SELECT id FROM faculty_subjects WHERE faculty_id = %s AND subject_id = %s", (faculty["faculty_id"], req.subject_id))
            if not assignment:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={"success": False, "message": "Faculty is not assigned to teach this subject", "error": "FORBIDDEN"}
                )

    # 1. Total calculation
    total_marks = round(req.internal_marks + req.assignment_marks + req.practical_marks + req.final_exam_marks, 2)
    
    # 2. Grade & Grade point calculation on Backend
    grade, grade_point = calculate_grade_and_point(total_marks)

    # 3. Upsert into database
    query = """
        INSERT INTO marks (
            student_id, subject_id, semester, internal_marks, assignment_marks,
            practical_marks, final_exam_marks, total_marks, grade, grade_point
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            internal_marks = VALUES(internal_marks),
            assignment_marks = VALUES(assignment_marks),
            practical_marks = VALUES(practical_marks),
            final_exam_marks = VALUES(final_exam_marks),
            total_marks = VALUES(total_marks),
            grade = VALUES(grade),
            grade_point = VALUES(grade_point)
    """
    execute_query(query, (
        req.student_id, req.subject_id, subject['semester'], req.internal_marks,
        req.assignment_marks, req.practical_marks, req.final_exam_marks,
        total_marks, grade, grade_point
    ))

    record = fetch_one("SELECT * FROM marks WHERE student_id = %s AND subject_id = %s", (req.student_id, req.subject_id))
    return StandardResponse(
        success=True,
        message="Marks recorded and graded successfully",
        data=record
    )

@router.put("/{mark_id}", response_model=StandardResponse)
def update_marks(
    mark_id: int,
    req: MarkUpdateRequest,
    current_user: dict = Depends(require_role("Admin", "Faculty"))
):
    """Updates mark record by mark ID."""
    mark = fetch_one("SELECT * FROM marks WHERE mark_id = %s", (mark_id,))
    if not mark:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Mark record not found", "error": "MARK_NOT_FOUND"})

    internal = req.internal_marks if req.internal_marks is not None else float(mark['internal_marks'])
    assignment = req.assignment_marks if req.assignment_marks is not None else float(mark['assignment_marks'])
    practical = req.practical_marks if req.practical_marks is not None else float(mark['practical_marks'])
    final_exam = req.final_exam_marks if req.final_exam_marks is not None else float(mark['final_exam_marks'])

    total_marks = round(internal + assignment + practical + final_exam, 2)
    grade, grade_point = calculate_grade_and_point(total_marks)

    execute_query("""
        UPDATE marks
        SET internal_marks = %s, assignment_marks = %s, practical_marks = %s,
            final_exam_marks = %s, total_marks = %s, grade = %s, grade_point = %s
        WHERE mark_id = %s
    """, (internal, assignment, practical, final_exam, total_marks, grade, grade_point, mark_id))

    updated_mark = fetch_one("SELECT * FROM marks WHERE mark_id = %s", (mark_id,))
    return StandardResponse(
        success=True,
        message="Mark record updated successfully",
        data=updated_mark
    )

@router.delete("/{mark_id}", response_model=StandardResponse)
def delete_marks(mark_id: int, current_user: dict = Depends(require_role("Admin"))):
    """Deletes mark record by mark ID."""
    mark = fetch_one("SELECT * FROM marks WHERE mark_id = %s", (mark_id,))
    if not mark:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Mark record not found", "error": "MARK_NOT_FOUND"})

    execute_query("DELETE FROM marks WHERE mark_id = %s", (mark_id,))
    return StandardResponse(
        success=True,
        message="Mark record deleted successfully"
    )
