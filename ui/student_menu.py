from services.student_service import StudentService
from services.attendance_service import AttendanceService
from services.examination_service import ExaminationService
from services.fee_service import FeeService
from utils.helpers import (
    Color, print_header, print_success, print_error, print_info, format_table
)
from ui.common import prompt_menu_choice, prompt_int

class StudentMenu:
    """CLI Menu Interface for Student users."""

    def __init__(self, auth_service):
        self.auth = auth_service
        self.student_service = StudentService()
        self.attendance_service = AttendanceService()
        self.exam_service = ExaminationService()
        self.fee_service = FeeService()

    def run(self):
        profile = self.auth.profile_data
        if not profile:
            print_error("Student profile data not found.")
            return

        student_id = profile['student_id']

        while True:
            options = [
                ("1", "View My Profile"),
                ("2", "View My Attendance"),
                ("3", "View My Exam Marks & Result Card"),
                ("4", "View My Fee Status & Balance"),
                ("0", "Logout")
            ]
            choice = prompt_menu_choice(f"STUDENT DASHBOARD - {profile.get('first_name', '')} ({profile.get('roll_number', '')})", options)

            if choice == "1":
                self.view_profile(student_id)
            elif choice == "2":
                self.view_attendance(student_id)
            elif choice == "3":
                self.view_marks(student_id)
            elif choice == "4":
                self.view_fees(student_id)
            elif choice == "0":
                self.auth.logout()
                print_info("Logged out successfully.")
                break
            else:
                print_error("Invalid option. Please select a valid menu choice.")

    def view_profile(self, student_id: int):
        try:
            student = self.student_service.get_student_by_id(student_id)
            print_header("STUDENT PROFILE DETAILS")
            print(f" {Color.BOLD}Roll Number:{Color.END}     {student['roll_number']}")
            print(f" {Color.BOLD}Full Name:{Color.END}       {student['first_name']} {student['last_name']}")
            print(f" {Color.BOLD}Department:{Color.END}      {student['department_name']}")
            print(f" {Color.BOLD}Course:{Color.END}          {student['course_name']}")
            print(f" {Color.BOLD}Semester:{Color.END}        {student['semester']}")
            print(f" {Color.BOLD}Date of Birth:{Color.END}   {student['dob']}")
            print(f" {Color.BOLD}Gender:{Color.END}          {student['gender']}")
            print(f" {Color.BOLD}Email:{Color.END}           {student['email']}")
            print(f" {Color.BOLD}Phone:{Color.END}           {student['phone']}")
            print(f" {Color.BOLD}Address:{Color.END}         {student['address']}")
            print(f" {Color.BOLD}Admission Date:{Color.END}  {student['admission_date']}")
        except Exception as e:
            print_error(str(e))

    def view_attendance(self, student_id: int):
        try:
            summary = self.attendance_service.get_attendance_percentage(student_id)
            records = self.attendance_service.get_student_attendance_records(student_id)

            print_header("MY ATTENDANCE SUMMARY")
            print(f" Total Classes Held:     {summary.get('total_classes', 0)}")
            print(f" Classes Attended:       {summary.get('total_attended', 0)}")
            print(f" Classes Absent:         {summary.get('total_absent', 0)}")
            pct = summary.get('attendance_percentage', 0.0)
            color = Color.GREEN if pct >= 75.0 else Color.RED
            print(f" Overall Percentage:     {color}{pct}%{Color.END}")

            headers = ["Date", "Course", "Status", "Remarks"]
            rows = [[r['date'], r['course_name'], r['status'], r.get('remarks') or ''] for r in records]
            print("\n" + format_table(headers, rows))
        except Exception as e:
            print_error(str(e))

    def view_marks(self, student_id: int):
        try:
            exams = self.exam_service.list_examinations()
            if not exams:
                print_info("No examinations registered yet.")
                return

            print_header("AVAILABLE EXAMINATIONS")
            headers = ["ID", "Exam Name", "Course", "Semester", "Exam Date"]
            rows = [[e['exam_id'], e['exam_name'], e['course_name'], e['semester'], e['exam_date']] for e in exams]
            print(format_table(headers, rows))

            exam_id = prompt_int("\nEnter Exam ID to view result card (or 0 to cancel)")
            if exam_id == 0:
                return

            result = self.exam_service.generate_student_result(student_id, exam_id)
            print_header(f"RESULT CARD: {result['exam_info']['exam_name']}")
            print(f" Student: {result['student_info']['first_name']} {result['student_info']['last_name']} ({result['student_info']['roll_number']})")
            print(f" Course: {result['student_info']['course_name']} | Semester: {result['student_info']['semester']}")

            sub_headers = ["Subject Code", "Subject Name", "Marks Obtained", "Total Marks", "Grade"]
            sub_rows = [[m['subject_code'], m['subject_name'], m['marks_obtained'], m['total_marks'], m['grade']] for m in result['subject_marks']]
            print(format_table(sub_headers, sub_rows))

            s = result['summary']
            status_color = Color.GREEN if s['status'] == "PASSED" else Color.RED
            print(f"\n {Color.BOLD}Total Marks Obtained:{Color.END} {s['total_obtained']} / {s['total_max_marks']}")
            print(f" {Color.BOLD}Overall Percentage:{Color.END}   {s['overall_percentage']}%")
            print(f" {Color.BOLD}Overall Grade:{Color.END}        {s['overall_grade']}")
            print(f" {Color.BOLD}Result Status:{Color.END}        {status_color}{s['status']}{Color.END}")
        except Exception as e:
            print_error(str(e))

    def view_fees(self, student_id: int):
        try:
            fees = self.fee_service.get_student_fee_status(student_id)
            print_header("MY FEE STATUS & BALANCES")
            headers = ["Fee ID", "Semester", "Academic Year", "Total Amount", "Paid Amount", "Remaining Balance", "Due Date", "Status"]
            rows = []
            for f in fees:
                status_str = f"{Color.GREEN}Paid{Color.END}" if f['status'] == 'Paid' else f"{Color.YELLOW}{f['status']}{Color.END}"
                rows.append([
                    f['fee_id'], f['semester'], f['academic_year'],
                    f"{float(f['total_amount']):.2f}",
                    f"{float(f['paid_amount']):.2f}",
                    f"{float(f['remaining_balance']):.2f}",
                    f['due_date'], status_str
                ])
            print(format_table(headers, rows))
        except Exception as e:
            print_error(str(e))
