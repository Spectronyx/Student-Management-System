from typing import Optional, Dict, Any, List
from repositories.student_repository import StudentRepository
from repositories.user_repository import UserRepository
from repositories.course_repository import CourseRepository
from utils.validators import (
    validate_email,
    validate_phone,
    validate_date,
    validate_roll_number,
    validate_required,
    ValidationError
)
from utils.security import hash_password
from database.connection import db_manager

class StudentService:
    """Service handling Student management business logic and transactions."""

    def __init__(self):
        self.student_repo = StudentRepository()
        self.user_repo = UserRepository()
        self.course_repo = CourseRepository()

    def create_student(self, first_name: str, last_name: str, roll_number: str,
                       dob_input: str, gender: str, email_input: str, phone_input: str,
                       address: str, department_id: int, course_id: int, semester: int,
                       admission_date_input: str, default_password: str = "student123") -> Dict[str, Any]:
        """Validates student inputs and creates User account + Student profile in a single atomic transaction."""
        
        # 1. Validation
        fname = validate_required(first_name, "First Name")
        lname = validate_required(last_name, "Last Name")
        roll = validate_roll_number(roll_number)
        email = validate_email(email_input)
        phone = validate_phone(phone_input)
        addr = validate_required(address, "Address")
        dob = validate_date(dob_input, "Date of Birth")
        admission_date = validate_date(admission_date_input, "Admission Date")

        if gender not in ('Male', 'Female', 'Other'):
            raise ValidationError("Gender must be 'Male', 'Female', or 'Other'.")

        # Check existing duplicates
        if self.student_repo.get_by_roll_number(roll):
            raise ValidationError(f"Student with roll number '{roll}' already exists.")

        if self.user_repo.get_by_email(email):
            raise ValidationError(f"Email '{email}' is already registered.")

        # Check department & course validity
        dept = self.course_repo.get_department_by_id(department_id)
        if not dept:
            raise ValidationError(f"Department ID {department_id} does not exist.")

        course = self.course_repo.get_course_by_id(course_id)
        if not course:
            raise ValidationError(f"Course ID {course_id} does not exist.")

        # Generate username from roll number
        username = roll.lower().replace(" ", "")
        pwd_hash = hash_password(default_password)

        # 2. Atomic Transaction: Create User + Create Student
        with db_manager.transaction() as cursor:
            # Create User Account
            user_sql = """
                INSERT INTO users (username, password_hash, role, email)
                VALUES (%s, %s, 'Student', %s)
            """
            cursor.execute(user_sql, (username, pwd_hash, email))
            user_id = cursor.lastrowid

            # Create Student Record
            student_sql = """
                INSERT INTO students (
                    user_id, roll_number, first_name, last_name, dob, gender,
                    email, phone, address, department_id, course_id, semester, admission_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(student_sql, (
                user_id, roll, fname, lname, str(dob), gender,
                email, phone, addr, department_id, course_id, semester, str(admission_date)
            ))
            student_id = cursor.lastrowid

            # Auto-enroll student into the course
            enroll_sql = """
                INSERT INTO enrollments (student_id, course_id, semester, enrollment_date, status)
                VALUES (%s, %s, %s, %s, 'Active')
            """
            cursor.execute(enroll_sql, (student_id, course_id, semester, str(admission_date)))

        return self.student_repo.get_by_id(student_id)

    def get_student_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise ValidationError(f"Student ID {student_id} not found.")
        return student

    def get_student_by_roll(self, roll_number: str) -> Optional[Dict[str, Any]]:
        student = self.student_repo.get_by_roll_number(roll_number)
        if not student:
            raise ValidationError(f"Student with roll number '{roll_number}' not found.")
        return student

    def list_all_students(self) -> List[Dict[str, Any]]:
        return self.student_repo.get_all_students()

    def search_students(self, query: str) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return self.list_all_students()
        return self.student_repo.search_students(query.strip())

    def update_student(self, student_id: int, update_fields: Dict[str, Any]) -> bool:
        existing = self.student_repo.get_by_id(student_id)
        if not existing:
            raise ValidationError(f"Student ID {student_id} not found.")

        valid_updates = {}
        if 'first_name' in update_fields:
            valid_updates['first_name'] = validate_required(update_fields['first_name'], "First Name")
        if 'last_name' in update_fields:
            valid_updates['last_name'] = validate_required(update_fields['last_name'], "Last Name")
        if 'email' in update_fields:
            valid_updates['email'] = validate_email(update_fields['email'])
        if 'phone' in update_fields:
            valid_updates['phone'] = validate_phone(update_fields['phone'])
        if 'address' in update_fields:
            valid_updates['address'] = validate_required(update_fields['address'], "Address")
        if 'semester' in update_fields:
            valid_updates['semester'] = int(update_fields['semester'])

        return self.student_repo.update_student(student_id, valid_updates)

    def delete_student(self, student_id: int) -> bool:
        existing = self.student_repo.get_by_id(student_id)
        if not existing:
            raise ValidationError(f"Student ID {student_id} not found.")
        return self.student_repo.delete_student(student_id)
