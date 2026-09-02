from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any, Dict

# Standard JSON API Wrapper
class StandardResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error: str

# Authentication Schemas
class LoginRequest(BaseModel):
    username_or_email: str = Field(..., description="Username or Email address")
    password: str = Field(..., description="Password")

class SignupRequest(BaseModel):
    username: str = Field(..., description="Username or Enrollment number")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")
    name: str = Field(..., description="Full Name")
    role: Optional[str] = Field("Student", description="User Role: Admin, Faculty, or Student")

class LoginResponseData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    name: str
    email: str

# Student Schemas
class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    enrollment_number: str
    email: EmailStr
    phone: Optional[str] = None
    department_id: int
    course: str
    year: int = 1
    semester: int = 1
    password: Optional[str] = "student123"

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    course: Optional[str] = None
    year: Optional[int] = None
    semester: Optional[int] = None

# Subject Schemas
class SubjectCreate(BaseModel):
    subject_code: str
    subject_name: str
    department_id: int
    semester: int = 1
    credits: int = 3

class SubjectUpdate(BaseModel):
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    department_id: Optional[int] = None
    semester: Optional[int] = None
    credits: Optional[int] = None

# Marks Schemas
class MarkEntryRequest(BaseModel):
    student_id: int
    subject_id: int
    semester: int = 1
    internal_marks: float = Field(0.0, ge=0.0, le=30.0)
    assignment_marks: float = Field(0.0, ge=0.0, le=20.0)
    practical_marks: float = Field(0.0, ge=0.0, le=20.0)
    final_exam_marks: float = Field(0.0, ge=0.0, le=50.0)

class MarkUpdateRequest(BaseModel):
    internal_marks: Optional[float] = Field(None, ge=0.0, le=30.0)
    assignment_marks: Optional[float] = Field(None, ge=0.0, le=20.0)
    practical_marks: Optional[float] = Field(None, ge=0.0, le=20.0)
    final_exam_marks: Optional[float] = Field(None, ge=0.0, le=50.0)

# Attendance Schemas
class AttendanceEntryRequest(BaseModel):
    student_id: int
    subject_id: int
    semester: int = 1
    classes_held: int = Field(..., ge=0)
    classes_attended: int = Field(..., ge=0)

class AttendanceUpdateRequest(BaseModel):
    classes_held: Optional[int] = Field(None, ge=0)
    classes_attended: Optional[int] = Field(None, ge=0)
