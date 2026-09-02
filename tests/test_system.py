import unittest
from datetime import date
from config import config
from database.connection import db_manager, get_connection
from utils.security import hash_password, verify_password
from utils.validators import (
    validate_email, validate_phone, validate_date, validate_marks, ValidationError
)
from utils.helpers import calculate_grade
from services.authentication_service import AuthenticationService
from services.student_service import StudentService
from services.attendance_service import AttendanceService
from services.examination_service import ExaminationService
from services.fee_service import FeeService

class TestStudentManagementSystem(unittest.TestCase):
    """Automated test suite verifying core system features, data logic, and database transactions."""

    @classmethod
    def setUpClass(cls):
        """Initializes database schema before running test suite."""
        db_manager.initialize_schema()
        cls.auth_service = AuthenticationService()
        cls.student_service = StudentService()
        cls.attendance_service = AttendanceService()
        cls.exam_service = ExaminationService()
        cls.fee_service = FeeService()

    def test_01_database_connection(self):
        """Test database connection and verify table structures."""
        conn = get_connection(use_db=True)
        self.assertIsNotNone(conn)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = [t[0] for t in cursor.fetchall()]
        required_tables = {'users', 'students', 'teachers', 'courses', 'departments', 'attendance', 'examinations', 'marks', 'fees', 'payments'}
        self.assertTrue(required_tables.issubset(set(tables)))
        cursor.close()
        conn.close()

    def test_02_password_hashing(self):
        """Test PBKDF2 password hashing and verification."""
        password = "secret_password_123"
        hashed = hash_password(password)
        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrong_password", hashed))

    def test_03_input_validators(self):
        """Test input validators for email, phone, date, and marks."""
        self.assertEqual(validate_email("test@student.edu"), "test@student.edu")
        with self.assertRaises(ValidationError):
            validate_email("invalid-email-format")

        self.assertEqual(validate_phone("+919876543210"), "+919876543210")
        with self.assertRaises(ValidationError):
            validate_phone("abc1234")

        self.assertEqual(validate_date("2026-05-20"), date(2026, 5, 20))
        with self.assertRaises(ValidationError):
            validate_date("invalid-date")

        self.assertEqual(validate_marks(85.5), 85.5)
        with self.assertRaises(ValidationError):
            validate_marks(150.0)

    def test_04_authentication(self):
        """Test login for Admin, Teacher, and Student credentials."""
        admin_user, admin_profile = self.auth_service.login("admin", "admin123")
        self.assertEqual(admin_user.role, "Admin")

        teacher_user, teacher_profile = self.auth_service.login("prof_sharma", "teacher123")
        self.assertEqual(teacher_user.role, "Teacher")

        student_user, student_profile = self.auth_service.login("student1", "student123")
        self.assertEqual(student_user.role, "Student")

    def test_05_grade_calculation(self):
        """Test centralized grading system logic."""
        pct, grade = calculate_grade(95.0, 100.0)
        self.assertEqual(grade, "A+")

        pct, grade = calculate_grade(85.0, 100.0)
        self.assertEqual(grade, "A")

        pct, grade = calculate_grade(65.0, 100.0)
        self.assertEqual(grade, "B")

        pct, grade = calculate_grade(35.0, 100.0)
        self.assertEqual(grade, "F")

    def test_06_student_crud(self):
        """Test student creation, search, update, and deletion."""
        roll = f"TEST{int(date.today().strftime('%M%S'))}"
        email = f"unittest_{roll.lower()}@student.edu"

        # Create
        student = self.student_service.create_student(
            "UnitTest", "Student", roll, "2004-01-01", "Male",
            email, "+919999988888", "Test Address", 1, 1, 1, "2026-08-01"
        )
        self.assertIsNotNone(student)
        student_id = student['student_id']

        # Search
        results = self.student_service.search_students("UnitTest")
        self.assertTrue(any(s['student_id'] == student_id for s in results))

        # Update
        self.student_service.update_student(student_id, {"first_name": "UpdatedName"})
        updated_student = self.student_service.get_student_by_id(student_id)
        self.assertEqual(updated_student['first_name'], "UpdatedName")

        # Delete
        self.student_service.delete_student(student_id)
        with self.assertRaises(ValidationError):
            self.student_service.get_student_by_id(student_id)

    def test_07_fee_payment_transaction(self):
        """Test fee payment recording and balance calculation."""
        fee = self.fee_service.assign_fee_record(1, 1, "2025-2026", 10000.00, "2026-09-01")
        fee_id = fee['fee_id']

        updated_fee = self.fee_service.record_payment(fee_id, 4000.00, "UPI", "TXN_TEST_001")
        self.assertEqual(float(updated_fee['paid_amount']), 4000.00)
        self.assertEqual(float(updated_fee['remaining_balance']), 6000.00)
        self.assertEqual(updated_fee['status'], "Partial")

        final_fee = self.fee_service.record_payment(fee_id, 6000.00, "UPI", "TXN_TEST_002")
        self.assertEqual(float(final_fee['remaining_balance']), 0.00)
        self.assertEqual(final_fee['status'], "Paid")

if __name__ == "__main__":
    unittest.main()
