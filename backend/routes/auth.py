from fastapi import APIRouter, HTTPException, status, Depends
from schemas.api_schemas import LoginRequest, SignupRequest, StandardResponse
from database import fetch_one, get_db
from utils.security import verify_password, hash_password, create_access_token
from utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=StandardResponse)
def signup(req: SignupRequest):
    """Registers a new user account (Student, Faculty, or Admin) with phone support."""
    username = req.username.strip()
    email = req.email.strip()
    phone = req.phone.strip() if req.phone else "9876543210"

    # Check for existing user by username, email, or phone
    existing = fetch_one("""
        SELECT u.user_id 
        FROM users u
        LEFT JOIN students s ON u.user_id = s.user_id
        LEFT JOIN faculty f ON u.user_id = f.user_id
        WHERE u.username = %s OR u.email = %s OR s.phone = %s OR f.phone = %s
    """, (username, email, phone, phone))

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "Username, Email, or Phone already registered", "error": "DUPLICATE_ENTRY"}
        )

    pwd_hash = hash_password(req.password)
    role = req.role if req.role in ["Admin", "Faculty", "Student"] else "Student"

    with get_db() as cursor:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, name, is_active)
            VALUES (%s, %s, %s, %s, %s, TRUE)
        """, (username, email, pwd_hash, role, req.name.strip()))
        user_id = cursor.lastrowid

        role_id = user_id
        if role == "Student":
            name_parts = req.name.strip().split()
            first_name = name_parts[0]
            last_name = name_parts[-1] if len(name_parts) > 1 else ''
            cursor.execute("""
                INSERT INTO students (
                    user_id, enrollment_number, first_name, last_name, email, phone,
                    department_id, course, year, semester, admission_date
                ) VALUES (%s, %s, %s, %s, %s, %s, 1, 'B.Tech', 1, 1, NOW())
            """, (user_id, username, first_name, last_name, email, phone))
            role_id = cursor.lastrowid
        elif role == "Faculty":
            cursor.execute("""
                INSERT INTO faculty (
                    user_id, employee_id, name, email, phone, department_id, hire_date
                ) VALUES (%s, %s, %s, %s, %s, 1, CURDATE())
            """, (user_id, f"EMP{user_id}", req.name.strip(), email, phone))
            role_id = cursor.lastrowid

    token = create_access_token(data={"sub": str(user_id), "role": role})

    return StandardResponse(
        success=True,
        message="Account registered successfully",
        data={
            "access_token": token,
            "token_type": "bearer",
            "user_id": user_id,
            "role_id": role_id,
            "role": role,
            "name": req.name.strip(),
            "email": email,
            "phone": phone
        }
    )

@router.post("/login", response_model=StandardResponse)
def login(req: LoginRequest):
    """Authenticates Admin, Faculty, or Student by username, email, or phone number."""
    login_id = req.username_or_email.strip()
    clean_phone = ''.join(c for c in login_id if c.isdigit())

    # Query user by username, email, or phone number
    user = fetch_one("""
        SELECT u.user_id, u.username, u.email, u.password_hash, u.role, u.name, u.is_active
        FROM users u
        LEFT JOIN students s ON u.user_id = s.user_id
        LEFT JOIN faculty f ON u.user_id = f.user_id
        WHERE u.username = %s 
           OR u.email = %s 
           OR s.phone = %s 
           OR f.phone = %s
           OR (%s != '' AND (REPLACE(s.phone, ' ', '') = %s OR REPLACE(f.phone, ' ', '') = %s))
        LIMIT 1
    """, (login_id, login_id, login_id, login_id, clean_phone, clean_phone, clean_phone))

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
