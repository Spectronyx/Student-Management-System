from fastapi import APIRouter, HTTPException, status, Depends
from schemas.api_schemas import AttendanceEntryRequest, AttendanceUpdateRequest, StandardResponse
from database import fetch_all, fetch_one, execute_query
from services.gpa_service import calculate_attendance_pct
from utils.dependencies import get_current_user, require_role

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.get("/student/{student_id}", response_model=StandardResponse)
def get_attendance_for_student(student_id: int, current_user: dict = Depends(get_current_user)):
    """Retrieves all attendance records for a student."""
    records = fetch_all("""
        SELECT a.*, sub.subject_code, sub.subject_name
        FROM attendance a
        JOIN subjects sub ON a.subject_id = sub.subject_id
        WHERE a.student_id = %s
        ORDER BY sub.subject_code
    """, (student_id,))

    return StandardResponse(
        success=True,
        message=f"Retrieved {len(records)} attendance records for student ID {student_id}",
        data=records
    )

@router.get("/subject/{subject_id}", response_model=StandardResponse)
def get_attendance_for_subject(subject_id: int, current_user: dict = Depends(get_current_user)):
    """Retrieves attendance records for all students in a subject."""
    records = fetch_all("""
        SELECT a.*, s.enrollment_number, s.first_name, s.last_name, u.name AS student_name
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        JOIN users u ON s.user_id = u.user_id
        WHERE a.subject_id = %s
        ORDER BY s.enrollment_number
    """, (subject_id,))

    return StandardResponse(
        success=True,
        message=f"Retrieved {len(records)} attendance records for subject ID {subject_id}",
        data=records
    )

@router.post("", response_model=StandardResponse)
def record_attendance(
    req: AttendanceEntryRequest,
    current_user: dict = Depends(require_role("Admin", "Faculty"))
):
    """
    Records or updates attendance for a student.
    Backend validates classes_attended <= classes_held and calculates percentage.
    """
    if req.classes_attended > req.classes_held:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "Classes attended cannot be greater than classes held", "error": "INVALID_ATTENDANCE_COUNT"}
        )

    student = fetch_one("SELECT student_id FROM students WHERE student_id = %s", (req.student_id,))
    if not student:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Student not found", "error": "STUDENT_NOT_FOUND"})

    subject = fetch_one("SELECT subject_id, semester FROM subjects WHERE subject_id = %s", (req.subject_id,))
    if not subject:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Subject not found", "error": "SUBJECT_NOT_FOUND"})

    # If Faculty, verify subject assignment
    if current_user["role"] == "Faculty":
        faculty = fetch_one("SELECT faculty_id FROM faculty WHERE user_id = %s", (current_user["user_id"],))
        if faculty:
            assignment = fetch_one("SELECT id FROM faculty_subjects WHERE faculty_id = %s AND subject_id = %s", (faculty["faculty_id"], req.subject_id))
            if not assignment:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={"success": False, "message": "Faculty is not assigned to teach this subject", "error": "FORBIDDEN"}
                )

    pct = calculate_attendance_pct(req.classes_attended, req.classes_held)

    query = """
        INSERT INTO attendance (student_id, subject_id, semester, classes_held, classes_attended, attendance_percentage)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            classes_held = VALUES(classes_held),
            classes_attended = VALUES(classes_attended),
            attendance_percentage = VALUES(attendance_percentage)
    """
    execute_query(query, (req.student_id, req.subject_id, subject['semester'], req.classes_held, req.classes_attended, pct))

    record = fetch_one("SELECT * FROM attendance WHERE student_id = %s AND subject_id = %s", (req.student_id, req.subject_id))
    return StandardResponse(
        success=True,
        message="Attendance recorded successfully",
        data=record
    )

@router.put("/{attendance_id}", response_model=StandardResponse)
def update_attendance(
    attendance_id: int,
    req: AttendanceUpdateRequest,
    current_user: dict = Depends(require_role("Admin", "Faculty"))
):
    """Updates attendance record by attendance ID."""
    record = fetch_one("SELECT * FROM attendance WHERE attendance_id = %s", (attendance_id,))
    if not record:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Attendance record not found", "error": "RECORD_NOT_FOUND"})

    held = req.classes_held if req.classes_held is not None else int(record['classes_held'])
    attended = req.classes_attended if req.classes_attended is not None else int(record['classes_attended'])

    if attended > held:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "Classes attended cannot be greater than classes held", "error": "INVALID_ATTENDANCE_COUNT"}
        )

    pct = calculate_attendance_pct(attended, held)

    execute_query("""
        UPDATE attendance
        SET classes_held = %s, classes_attended = %s, attendance_percentage = %s
        WHERE attendance_id = %s
    """, (held, attended, pct, attendance_id))

    updated_record = fetch_one("SELECT * FROM attendance WHERE attendance_id = %s", (attendance_id,))
    return StandardResponse(
        success=True,
        message="Attendance record updated successfully",
        data=updated_record
    )
