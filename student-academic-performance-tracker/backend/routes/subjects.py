from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from schemas.api_schemas import SubjectCreate, SubjectUpdate, StandardResponse
from database import fetch_all, fetch_one, execute_query
from utils.dependencies import get_current_user, require_role

router = APIRouter(prefix="/subjects", tags=["Subjects"])

@router.get("", response_model=StandardResponse)
def get_subjects(
    department_id: Optional[int] = None,
    semester: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """Retrieves list of subjects with optional filters."""
    query = """
        SELECT sub.*, d.department_name, d.department_code
        FROM subjects sub
        JOIN departments d ON sub.department_id = d.department_id
        WHERE 1=1
    """
    params = []

    if department_id:
        query += " AND sub.department_id = %s"
        params.append(department_id)

    if semester:
        query += " AND sub.semester = %s"
        params.append(semester)

    query += " ORDER BY sub.subject_code"

    subjects = fetch_all(query, tuple(params))
    return StandardResponse(
        success=True,
        message=f"Retrieved {len(subjects)} subjects",
        data=subjects
    )

@router.get("/{subject_id}", response_model=StandardResponse)
def get_subject_by_id(subject_id: int, current_user: dict = Depends(get_current_user)):
    """Retrieves subject by ID."""
    subject = fetch_one("""
        SELECT sub.*, d.department_name, d.department_code
        FROM subjects sub
        JOIN departments d ON sub.department_id = d.department_id
        WHERE sub.subject_id = %s
    """, (subject_id,))

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": f"Subject ID {subject_id} not found", "error": "SUBJECT_NOT_FOUND"}
        )

    return StandardResponse(
        success=True,
        message="Subject retrieved successfully",
        data=subject
    )

@router.post("", response_model=StandardResponse)
def create_subject(
    req: SubjectCreate,
    current_user: dict = Depends(require_role("Admin"))
):
    """Creates a new academic subject."""
    existing = fetch_one("SELECT subject_id FROM subjects WHERE subject_code = %s", (req.subject_code,))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": f"Subject code '{req.subject_code}' already exists", "error": "DUPLICATE_ENTRY"}
        )

    subject_id = execute_query("""
        INSERT INTO subjects (subject_code, subject_name, department_id, semester, credits)
        VALUES (%s, %s, %s, %s, %s)
    """, (req.subject_code.upper(), req.subject_name, req.department_id, req.semester, req.credits))

    subject = fetch_one("SELECT * FROM subjects WHERE subject_id = %s", (subject_id,))
    return StandardResponse(
        success=True,
        message="Subject created successfully",
        data=subject
    )

@router.put("/{subject_id}", response_model=StandardResponse)
def update_subject(
    subject_id: int,
    req: SubjectUpdate,
    current_user: dict = Depends(require_role("Admin"))
):
    """Updates subject information."""
    subject = fetch_one("SELECT * FROM subjects WHERE subject_id = %s", (subject_id,))
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": f"Subject ID {subject_id} not found", "error": "SUBJECT_NOT_FOUND"}
        )

    updates = {}
    if req.subject_code is not None: updates['subject_code'] = req.subject_code.upper()
    if req.subject_name is not None: updates['subject_name'] = req.subject_name
    if req.department_id is not None: updates['department_id'] = req.department_id
    if req.semester is not None: updates['semester'] = req.semester
    if req.credits is not None: updates['credits'] = req.credits

    if updates:
        set_str = ", ".join([f"{k} = %s" for k in updates.keys()])
        params = list(updates.values())
        params.append(subject_id)
        execute_query(f"UPDATE subjects SET {set_str} WHERE subject_id = %s", tuple(params))

    updated_subject = fetch_one("SELECT * FROM subjects WHERE subject_id = %s", (subject_id,))
    return StandardResponse(
        success=True,
        message="Subject updated successfully",
        data=updated_subject
    )

@router.delete("/{subject_id}", response_model=StandardResponse)
def delete_subject(
    subject_id: int,
    current_user: dict = Depends(require_role("Admin"))
):
    """Deletes subject by ID."""
    subject = fetch_one("SELECT * FROM subjects WHERE subject_id = %s", (subject_id,))
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": f"Subject ID {subject_id} not found", "error": "SUBJECT_NOT_FOUND"}
        )

    execute_query("DELETE FROM subjects WHERE subject_id = %s", (subject_id,))
    return StandardResponse(
        success=True,
        message="Subject deleted successfully"
    )
