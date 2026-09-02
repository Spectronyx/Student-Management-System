from fastapi import APIRouter, HTTPException, status, Depends
from schemas.api_schemas import StandardResponse
from services.performance_service import get_student_performance_summary
from database import fetch_all, fetch_one
from utils.dependencies import get_current_user

router = APIRouter(prefix="/performance", tags=["Performance"])

@router.get("/student/{student_id}", response_model=StandardResponse)
def get_student_performance(student_id: int, current_user: dict = Depends(get_current_user)):
    """Returns complete academic performance dashboard metrics for a student."""
    perf = get_student_performance_summary(student_id)
    if not perf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": f"Student ID {student_id} not found", "error": "STUDENT_NOT_FOUND"}
        )

    return StandardResponse(
        success=True,
        message="Student performance retrieved successfully",
        data=perf
    )

@router.get("/student/{student_id}/gpa", response_model=StandardResponse)
def get_student_gpa(student_id: int, current_user: dict = Depends(get_current_user)):
    """Returns GPA and semester-wise GPA breakdown."""
    perf = get_student_performance_summary(student_id)
    if not perf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": f"Student ID {student_id} not found", "error": "STUDENT_NOT_FOUND"}
        )

    return StandardResponse(
        success=True,
        message="GPA retrieved successfully",
        data={
            "student_id": student_id,
            "enrollment_number": perf["enrollment_number"],
            "name": perf["name"],
            "gpa": perf["gpa"],
            "cgpa": perf["cgpa"],
            "overall_percentage": perf["overall_percentage"]
        }
    )

@router.get("/student/{student_id}/ranking", response_model=StandardResponse)
def get_student_ranking(student_id: int, current_user: dict = Depends(get_current_user)):
    """Returns student class and department ranking."""
    perf = get_student_performance_summary(student_id)
    if not perf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": f"Student ID {student_id} not found", "error": "STUDENT_NOT_FOUND"}
        )

    tot_students = fetch_one("SELECT COUNT(*) AS cnt FROM students WHERE semester = %s", (perf["semester"],))
    total_count = tot_students["cnt"] if tot_students else 1

    return StandardResponse(
        success=True,
        message="Ranking retrieved successfully",
        data={
            "student_id": student_id,
            "name": perf["name"],
            "rank": perf["rank"],
            "total_students_in_class": total_count,
            "percentile": round(((total_count - perf["rank"] + 1) / total_count) * 100.0, 2)
        }
    )
