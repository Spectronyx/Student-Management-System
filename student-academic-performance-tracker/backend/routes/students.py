from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from schemas.api_schemas import StudentCreate, StudentUpdate, StandardResponse
from database import fetch_all, fetch_one, execute_query, get_db
from utils.security import hash_password
from utils.dependencies import get_current_user, require_role

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("", response_model=StandardResponse)
def get_students(
    department_id: Optional[int] = None,
    semester: Optional[int] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Retrieves list of students with optional search and filters."""
    query = """
        SELECT s.*, d.department_name, d.department_code, u.name AS full_name
        FROM students s
        JOIN departments d ON s.department_id = d.department_id
        JOIN users u ON s.user_id = u.user_id
        WHERE 1=1
    """
    params = []

    if department_id:
        query += " AND s.department_id = %s"
        params.append(department_id)

    if semester:
        query += " AND s.semester = %s"
        params.append(semester)

    if search:
        like_str = f"%{search.strip()}%"
        query += " AND (s.enrollment_number LIKE %s OR s.first_name LIKE %s OR s.last_name LIKE %s OR s.email LIKE %s)"
        params.extend([like_str, like_str, like_str, like_str])

    query += " ORDER BY s.student_id DESC"

    students = fetch_all(query, tuple(params))
    return StandardResponse(
        success=True,
        message=f"Retrieved {len(students)} students",
        data=students
    )

@router.get("/{student_id}", response_model=StandardResponse)
def get_student_by_id(student_id: int, current_user: dict = Depends(get_current_user)):
    """Retrieves student by ID."""
    student = fetch_one("""
        SELECT s.*, d.department_name, d.department_code, u.name AS full_name
        FROM students s
        JOIN departments d ON s.department_id = d.department_id
        JOIN users u ON s.user_id = u.user_id
        WHERE s.student_id = %s
    """, (student_id,))

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": f"Student ID {student_id} not found", "error": "STUDENT_NOT_FOUND"}
        )

    return StandardResponse(
        success=True,
        message="Student retrieved successfully",
        data=student
    )

@router.post("", response_model=StandardResponse)
def create_student(
    req: StudentCreate,
    current_user: dict = Depends(require_role("Admin"))
):
    """Registers a new student and creates a corresponding user account."""
    # Check duplicate enrollment or email
    existing = fetch_one("SELECT student_id FROM students WHERE enrollment_number = %s OR email = %s", (req.enrollment_number, req.email))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "Enrollment number or Email already registered", "error": "DUPLICATE_ENTRY"}
        )

    pwd_hash = hash_password(req.password or "student123")
    full_name = f"{req.first_name} {req.last_name}"

    with get_db() as cursor:
        # 1. Create User
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, name)
            VALUES (%s, %s, %s, 'Student', %s)
        """, (req.enrollment_number, req.email, pwd_hash, full_name))
        user_id = cursor.lastrowid

        # 2. Create Student Profile
        cursor.execute("""
            INSERT INTO students (
                user_id, enrollment_number, first_name, last_name, email, phone,
                department_id, course, year, semester, admission_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            user_id, req.enrollment_number, req.first_name, req.last_name, req.email,
            req.phone, req.department_id, req.course, req.year, req.semester
        ))
        student_id = cursor.lastrowid

    student = fetch_one("SELECT * FROM students WHERE student_id = %s", (student_id,))
    return StandardResponse(
        success=True,
        message="Student created successfully",
        data=student
    )

@router.put("/{student_id}", response_model=StandardResponse)
def update_student(
    student_id: int,
    req: StudentUpdate,
    current_user: dict = Depends(require_role("Admin", "Faculty"))
):
    """Updates student information."""
    student = fetch_one("SELECT * FROM students WHERE student_id = %s", (student_id,))
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": f"Student ID {student_id} not found", "error": "STUDENT_NOT_FOUND"}
        )

    updates = {}
    if req.first_name is not None: updates['first_name'] = req.first_name
    if req.last_name is not None: updates['last_name'] = req.last_name
    if req.email is not None: updates['email'] = req.email
    if req.phone is not None: updates['phone'] = req.phone
    if req.department_id is not None: updates['department_id'] = req.department_id
    if req.course is not None: updates['course'] = req.course
    if req.year is not None: updates['year'] = req.year
    if req.semester is not None: updates['semester'] = req.semester

    if updates:
        set_str = ", ".join([f"{k} = %s" for k in updates.keys()])
        params = list(updates.values())
        params.append(student_id)
        execute_query(f"UPDATE students SET {set_str} WHERE student_id = %s", tuple(params))

    updated_student = fetch_one("SELECT * FROM students WHERE student_id = %s", (student_id,))
    return StandardResponse(
        success=True,
        message="Student updated successfully",
        data=updated_student
    )

@router.delete("/{student_id}", response_model=StandardResponse)
def delete_student(
    student_id: int,
    current_user: dict = Depends(require_role("Admin"))
):
    """Deletes student and associated user account."""
    student = fetch_one("SELECT * FROM students WHERE student_id = %s", (student_id,))
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": f"Student ID {student_id} not found", "error": "STUDENT_NOT_FOUND"}
        )

    execute_query("DELETE FROM users WHERE user_id = %s", (student['user_id'],))
    return StandardResponse(
        success=True,
        message="Student deleted successfully"
    )
