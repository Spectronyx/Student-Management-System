from services.student_service import StudentService
from services.course_service import CourseService
from services.attendance_service import AttendanceService
from services.examination_service import ExaminationService
from utils.helpers import (
    Color, print_header, print_success, print_error, print_info, format_table
)
from ui.common import (
    prompt_menu_choice, prompt_input, prompt_int, prompt_float
)

class TeacherMenu:
    """CLI Menu Interface for Teacher users."""

    def __init__(self, auth_service):
        self.auth = auth_service
        self.student_service = StudentService()
        self.course_service = CourseService()
        self.attendance_service = AttendanceService()
        self.exam_service = ExaminationService()

    def run(self):
        profile = self.auth.profile_data
        if not profile:
            print_error("Teacher profile data not found.")
            return

        while True:
            options = [
                ("1", "View All Students"),
                ("2", "Search Student"),
                ("3", "Mark Student Attendance"),
                ("4", "View Attendance Report"),
                ("5", "Enter Examination Marks"),
                ("6", "View Examination Results"),
                ("0", "Logout")
            ]
            choice = prompt_menu_choice(f"TEACHER DASHBOARD - Prof. {profile.get('first_name', '')} {profile.get('last_name', '')}", options)

            if choice == "1":
                self.view_students()
            elif choice == "2":
                self.search_student()
            elif choice == "3":
                self.mark_attendance()
            elif choice == "4":
                self.view_attendance_report()
            elif choice == "5":
                self.enter_marks()
            elif choice == "6":
                self.view_exam_results()
            elif choice == "0":
                self.auth.logout()
                print_info("Logged out successfully.")
                break
            else:
                print_error("Invalid option. Please select a valid menu choice.")

    def view_students(self):
        try:
            students = self.student_service.list_all_students()
            print_header("STUDENTS LIST")
            headers = ["ID", "Roll No", "Full Name", "Gender", "Course", "Semester", "Email", "Phone"]
            rows = [[s['student_id'], s['roll_number'], s['full_name'], s['gender'], s['course_name'], s['semester'], s['email'], s['phone']] for s in students]
            print(format_table(headers, rows))
        except Exception as e:
            print_error(str(e))

    def search_student(self):
        try:
            term = prompt_input("Enter Roll Number or Student Name to search")
            results = self.student_service.search_students(term)
            print_header(f"SEARCH RESULTS FOR '{term}'")
            headers = ["ID", "Roll No", "Full Name", "Department", "Course", "Semester", "Email"]
            rows = [[s['student_id'], s['roll_number'], s['full_name'], s['department_name'], s['course_name'], s['semester'], s['email']] for s in results]
            print(format_table(headers, rows))
        except Exception as e:
            print_error(str(e))

    def mark_attendance(self):
        try:
            print_header("MARK STUDENT ATTENDANCE")
            student_id = prompt_int("Enter Student ID")
            course_id = prompt_int("Enter Course ID")
            att_date = prompt_input("Enter Date (YYYY-MM-DD)", default="2026-02-01")
            
            print("\nSelect Attendance Status:")
            print("  1. Present")
            print("  2. Absent")
            print("  3. Late")
            print("  4. Excused")
            st_choice = prompt_input("Select status option (1-4)", default="1")
            st_map = {"1": "Present", "2": "Absent", "3": "Late", "4": "Excused"}
            status = st_map.get(st_choice, "Present")

            remarks = prompt_input("Enter Remarks (optional)", default="Class attendance")

            self.attendance_service.mark_student_attendance(student_id, course_id, att_date, status, remarks)
            print_success(f"Attendance marked successfully for Student ID {student_id} as '{status}'!")
        except Exception as e:
            print_error(str(e))

    def view_attendance_report(self):
        try:
            print_header("ATTENDANCE REPORT")
            student_id = prompt_int("Enter Student ID to view detailed attendance")
            records = self.attendance_service.get_student_attendance_records(student_id)
            summary = self.attendance_service.get_attendance_percentage(student_id)

            print(f"\n Total Attended: {summary.get('total_attended', 0)} / {summary.get('total_classes', 0)} ({summary.get('attendance_percentage', 0.0)}%)")
            headers = ["Date", "Course", "Status", "Remarks"]
            rows = [[r['date'], r['course_name'], r['status'], r.get('remarks') or ''] for r in records]
            print(format_table(headers, rows))
        except Exception as e:
            print_error(str(e))

    def enter_marks(self):
        try:
            print_header("ENTER STUDENT EXAMINATION MARKS")
            exam_id = prompt_int("Enter Exam ID")
            subject_id = prompt_int("Enter Subject ID")
            student_id = prompt_int("Enter Student ID")
            marks_obtained = prompt_float("Enter Marks Obtained (0 - 100)")
            remarks = prompt_input("Enter Remarks (optional)", default="Exam evaluated")

            self.exam_service.enter_marks(exam_id, subject_id, student_id, marks_obtained, remarks)
            print_success(f"Marks entered successfully for Student ID {student_id}!")
        except Exception as e:
            print_error(str(e))

    def view_exam_results(self):
        try:
            print_header("VIEW STUDENT RESULT CARD")
            student_id = prompt_int("Enter Student ID")
            exam_id = prompt_int("Enter Exam ID")

            result = self.exam_service.generate_student_result(student_id, exam_id)
            print_header(f"RESULT CARD: {result['exam_info']['exam_name']}")
            print(f" Student: {result['student_info']['first_name']} {result['student_info']['last_name']} ({result['student_info']['roll_number']})")
            print(f" Course: {result['student_info']['course_name']} | Semester: {result['student_info']['semester']}")

            sub_headers = ["Subject Code", "Subject Name", "Marks Obtained", "Total Marks", "Grade"]
            sub_rows = [[m['subject_code'], m['subject_name'], m['marks_obtained'], m['total_marks'], m['grade']] for m in result['subject_marks']]
            print(format_table(sub_headers, sub_rows))

            s = result['summary']
            print(f"\n Total Marks: {s['total_obtained']} / {s['total_max_marks']} | Percentage: {s['overall_percentage']}% | Grade: {s['overall_grade']} | Status: {s['status']}")
        except Exception as e:
            print_error(str(e))
