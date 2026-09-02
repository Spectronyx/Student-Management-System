from fastapi import APIRouter, HTTPException, status, Depends
from schemas.api_schemas import LoginRequest, StandardResponse
from database import fetch_one
from utils.security import verify_password, create_access_token
from utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=StandardResponse)
def login(req: LoginRequest):
    """Authenticates Admin, Faculty, or Student and returns JWT bearer token."""
    login_id = req.username_or_email.strip()

    # Query user by username or email
    user = fetch_one("""
        SELECT user_id, username, email, password_hash, role, name, is_active
        FROM users
        WHERE username = %s OR email = %s
    """, (login_id, login_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "Invalid credentials", "error": "INVALID_CREDENTIALS"}
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": "Account is deactivated", "error": "ACCOUNT_INACTIVE"}
        )

    if not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "Invalid credentials", "error": "INVALID_CREDENTIALS"}
        )

    # Fetch role-specific details
    role_id = user["user_id"]
    if user["role"] == "Student":
        student = fetch_one("SELECT student_id FROM students WHERE user_id = %s", (user["user_id"],))
        if student:
            role_id = student["student_id"]
    elif user["role"] == "Faculty":
        faculty = fetch_one("SELECT faculty_id FROM faculty WHERE user_id = %s", (user["user_id"],))
        if faculty:
            role_id = faculty["faculty_id"]

    # Generate JWT token
    token = create_access_token(data={"sub": str(user["user_id"]), "role": user["role"]})

    return StandardResponse(
        success=True,
        message="Login successful",
        data={
            "access_token": token,
            "token_type": "bearer",
            "user_id": user["user_id"],
            "role_id": role_id,
            "role": user["role"],
            "name": user["name"],
            "email": user["email"]
        }
    )

@router.post("/logout", response_model=StandardResponse)
def logout(current_user: dict = Depends(get_current_user)):
    """Logs out current authenticated session."""
    return StandardResponse(
        success=True,
        message="Successfully logged out"
    )

@router.get("/me", response_model=StandardResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """Retrieves authenticated user details."""
    return StandardResponse(
        success=True,
        message="User profile retrieved",
        data=current_user
    )
