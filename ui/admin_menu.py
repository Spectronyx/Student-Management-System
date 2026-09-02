from services.student_service import StudentService
from services.course_service import CourseService
from services.attendance_service import AttendanceService
from services.examination_service import ExaminationService
from services.fee_service import FeeService
from utils.helpers import (
    Color, print_header, print_success, print_error, print_info, print_warning, format_table
)
from ui.common import (
    prompt_menu_choice, prompt_input, prompt_int, prompt_float
)

class AdminMenu:
    """CLI Menu Interface for Admin users."""

    def __init__(self, auth_service):
        self.auth = auth_service
        self.student_service = StudentService()
        self.course_service = CourseService()
        self.attendance_service = AttendanceService()
        self.exam_service = ExaminationService()
        self.fee_service = FeeService()

    def run(self):
        while True:
            options = [
                ("1", "Student Management (Add, View, Update, Delete)"),
                ("2", "Department & Course Management"),
                ("3", "Attendance Management"),
                ("4", "Examination & Marks Management"),
                ("5", "Fees & Payments Management"),
                ("6", "Reports & Analytics"),
                ("0", "Logout")
            ]
            choice = prompt_menu_choice("ADMINISTRATION DASHBOARD", options)

            if choice == "1":
                self.student_menu()
            elif choice == "2":
                self.course_menu()
            elif choice == "3":
                self.attendance_menu()
            elif choice == "4":
                self.exam_menu()
            elif choice == "5":
                self.fee_menu()
            elif choice == "6":
                self.reports_menu()
            elif choice == "0":
                self.auth.logout()
                print_info("Logged out successfully.")
                break
            else:
                print_error("Invalid option. Please select a valid menu choice.")

    # =========================================================================
    # 1. STUDENT MANAGEMENT
    # =========================================================================
    def student_menu(self):
        while True:
            options = [
                ("1", "Add New Student"),
                ("2", "View All Students"),
                ("3", "Search Student (by Roll or Name)"),
                ("4", "View Student Profile"),
                ("5", "Update Student Info"),
                ("6", "Delete Student"),
                ("0", "Back to Main Menu")
            ]
            choice = prompt_menu_choice("STUDENT MANAGEMENT", options)

            if choice == "1":
                self.add_student()
            elif choice == "2":
                self.view_all_students()
            elif choice == "3":
                self.search_students()
            elif choice == "4":
                self.view_student_profile()
            elif choice == "5":
                self.update_student()
            elif choice == "6":
                self.delete_student()
            elif choice == "0":
                break
            else:
                print_error("Invalid selection.")

    def add_student(self):
        try:
            print_header("REGISTER NEW STUDENT")
            fname = prompt_input("First Name")
            lname = prompt_input("Last Name")
            roll = prompt_input("Roll Number (e.g. BCA2026001)")
            dob = prompt_input("Date of Birth (YYYY-MM-DD)", default="2004-01-01")
            
            print("Select Gender: [1] Male  [2] Female  [3] Other")
            g_choice = prompt_input("Gender Option", default="1")
            gender = {"1": "Male", "2": "Female", "3": "Other"}.get(g_choice, "Male")

            email = prompt_input("Email Address")
            phone = prompt_input("Phone Number")
            address = prompt_input("Residential Address")

            # Show available departments & courses
            depts = self.course_service.list_departments()
            print("\nAvailable Departments:")
            for d in depts:
                print(f"  [{d['department_id']}] {d['department_code']} - {d['department_name']}")
            dept_id = prompt_int("Select Department ID")

            courses = self.course_service.list_courses()
            print("\nAvailable Courses:")
            for c in courses:
                print(f"  [{c['course_id']}] {c['course_code']} - {c['course_name']}")
            course_id = prompt_int("Select Course ID")

            semester = prompt_int("Semester", default=1)
            admission_date = prompt_input("Admission Date (YYYY-MM-DD)", default="2026-08-01")
            pwd = prompt_input("Initial Password", default="student123")

            student = self.student_service.create_student(
                fname, lname, roll, dob, gender, email, phone, address,
                dept_id, course_id, semester, admission_date, pwd
            )
            print_success(f"Student '{student['first_name']} {student['last_name']}' ({student['roll_number']}) registered successfully!")
        except Exception as e:
            print_error(str(e))

    def view_all_students(self):
        try:
            students = self.student_service.list_all_students()
            print_header("ALL REGISTERED STUDENTS")
            headers = ["ID", "Roll No", "Full Name", "Gender", "Department", "Course", "Sem", "Email", "Phone"]
            rows = [[s['student_id'], s['roll_number'], s['full_name'], s['gender'], s['department_name'], s['course_name'], s['semester'], s['email'], s['phone']] for s in students]
            print(format_table(headers, rows))
        except Exception as e:
            print_error(str(e))

    def search_students(self):
        try:
            term = prompt_input("Enter Search Keyword (Roll / Name / Email)")
            results = self.student_service.search_students(term)
            print_header(f"SEARCH RESULTS ({len(results)} MATCHES)")
            headers = ["ID", "Roll No", "Full Name", "Department", "Course", "Sem", "Email"]
            rows = [[s['student_id'], s['roll_number'], s['full_name'], s['department_name'], s['course_name'], s['semester'], s['email']] for s in results]
            print(format_table(headers, rows))
        except Exception as e:
            print_error(str(e))

    def view_student_profile(self):
        try:
            roll = prompt_input("Enter Student Roll Number or ID")
            if roll.isdigit():
                student = self.student_service.get_student_by_id(int(roll))
            else:
                student = self.student_service.get_student_by_roll(roll)

            print_header("STUDENT COMPLETE PROFILE")
            print(f" {Color.BOLD}Student ID:{Color.END}      {student['student_id']}")
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

    def update_student(self):
        try:
            student_id = prompt_int("Enter Student ID to Update")
            student = self.student_service.get_student_by_id(student_id)
            print_info(f"Updating info for '{student['first_name']} {student['last_name']}' (Press Enter to keep existing value).")

            fname = prompt_input("First Name", default=student['first_name'])
            lname = prompt_input("Last Name", default=student['last_name'])
            email = prompt_input("Email", default=student['email'])
            phone = prompt_input("Phone", default=student['phone'])
            address = prompt_input("Address", default=student['address'])
            semester = prompt_int("Semester", default=student['semester'])

            updates = {
                "first_name": fname,
                "last_name": lname,
                "email": email,
                "phone": phone,
                "address": address,
                "semester": semester
            }

            if self.student_service.update_student(student_id, updates):
                print_success(f"Student ID {student_id} updated successfully!")
        except Exception as e:
            print_error(str(e))

    def delete_student(self):
        try:
            student_id = prompt_int("Enter Student ID to Delete")
            student = self.student_service.get_student_by_id(student_id)
            confirm = prompt_input(f"{Color.RED}Are you sure you want to permanently delete '{student['first_name']} {student['last_name']}'? (yes/no){Color.END}")
            if confirm.lower() in ('yes', 'y'):
                self.student_service.delete_student(student_id)
                print_success(f"Student ID {student_id} and associated user account deleted successfully!")
            else:
                print_info("Deletion cancelled.")
        except Exception as e:
            print_error(str(e))

    # =========================================================================
    # 2. COURSE & DEPARTMENT MANAGEMENT
    # =========================================================================
    def course_menu(self):
        while True:
            options = [
                ("1", "Add Department"),
                ("2", "View Departments"),
                ("3", "Add Course"),
                ("4", "View Courses"),
                ("5", "Add Subject to Course"),
                ("0", "Back to Main Menu")
            ]
            choice = prompt_menu_choice("DEPARTMENT & COURSE MANAGEMENT", options)

            if choice == "1":
                self.add_department()
            elif choice == "2":
                self.view_departments()
            elif choice == "3":
                self.add_course()
            elif choice == "4":
                self.view_courses()
            elif choice == "5":
                self.add_subject()
            elif choice == "0":
                break
            else:
                print_error("Invalid selection.")

    def add_department(self):
        try:
            code = prompt_input("Department Code (e.g. CS, EE, ME)")
            name = prompt_input("Department Full Name")
            dept = self.course_service.add_department(code, name)
            print_success(f"Department '{dept['department_name']}' added successfully!")
        except Exception as e:
            print_error(str(e))

    def view_departments(self):
        try:
            depts = self.course_service.list_departments()
            print_header("ALL DEPARTMENTS")
            headers = ["ID", "Code", "Department Name"]
            rows = [[d['department_id'], d['department_code'], d['department_name']] for d in depts]
            print(format_table(headers, rows))
        except Exception as e:
            print_error(str(e))

    def add_course(self):
        try:
            code = prompt_input("Course Code (e.g. BCA, BTech)")
            name = prompt_input("Course Full Name")
            dept_id = prompt_int("Department ID")
            credits = prompt_int("Course Credits", default=120)
            course = self.course_service.add_course(code, name, dept_id, credits)
            print_success(f"Course '{course['course_name']}' added successfully!")
        except Exception as e:
            print_error(str(e))

    def view_courses(self):
        try:
            courses = self.course_service.list_courses()
            print_header("ALL COURSES")
            headers = ["ID", "Code", "Course Name", "Department", "Credits"]
            rows = [[c['course_id'], c['course_code'], c['course_name'], c['department_name'], c['credits']] for c in courses]
            print(format_table(headers, rows))
        except Exception as e:
            print_error(str(e))

    def add_subject(self):
        try:
            code = prompt_input("Subject Code (e.g. BCA101)")
            name = prompt_input("Subject Name")
            course_id = prompt_int("Course ID")
            semester = prompt_int("Semester", default=1)
            credits = prompt_int("Subject Credits", default=4)
            self.course_service.add_subject(code, name, course_id, semester, credits)
            print_success(f"Subject '{name}' added successfully!")
        except Exception as e:
            print_error(str(e))

    # =========================================================================
    # 3. ATTENDANCE MANAGEMENT
    # =========================================================================
    def attendance_menu(self):
        while True:
            options = [
                ("1", "Mark Student Attendance"),
                ("2", "View Student Attendance History"),
                ("3", "View Students Below Attendance Threshold (< 75%)"),
                ("0", "Back to Main Menu")
            ]
            choice = prompt_menu_choice("ATTENDANCE MANAGEMENT", options)

            if choice == "1":
                self.mark_attendance()
            elif choice == "2":
                self.view_student_attendance()
            elif choice == "3":
                self.view_low_attendance()
            elif choice == "0":
                break
            else:
                print_error("Invalid selection.")

    def mark_attendance(self):
        try:
            student_id = prompt_int("Enter Student ID")
            course_id = prompt_int("Enter Course ID")
            att_date = prompt_input("Date (YYYY-MM-DD)", default="2026-02-01")
            
            print("Status Options: [1] Present  [2] Absent  [3] Late  [4] Excused")
            st_choice = prompt_input("Status Option", default="1")
            status = {"1": "Present", "2": "Absent", "3": "Late", "4": "Excused"}.get(st_choice, "Present")

            remarks = prompt_input("Remarks", default="Marked by admin")
            self.attendance_service.mark_student_attendance(student_id, course_id, att_date, status, remarks)
            print_success(f"Attendance recorded for Student ID {student_id} as '{status}'!")
        except Exception as e:
            print_error(str(e))

    def view_student_attendance(self):
        try:
            student_id = prompt_int("Enter Student ID")
            summary = self.attendance_service.get_attendance_percentage(student_id)
            records = self.attendance_service.get_student_attendance_records(student_id)

            print_header(f"ATTENDANCE SUMMARY FOR STUDENT ID {student_id}")
            print(f" Attended: {summary.get('total_attended', 0)} / {summary.get('total_classes', 0)} classes ({summary.get('attendance_percentage', 0.0)}%)")
            headers = ["Date", "Course", "Status", "Remarks"]
            rows = [[r['date'], r['course_name'], r['status'], r.get('remarks') or ''] for r in records]
            print(format_table(headers, rows))
        except Exception as e:
            print_error(str(e))

    def view_low_attendance(self):
        try:
            threshold = prompt_float("Enter Attendance Threshold Percentage", default=75.0)
            low_students = self.attendance_service.get_low_attendance_students(threshold)
            print_header(f"STUDENTS BELOW {threshold}% ATTENDANCE THRESHOLD")
            headers = ["Student ID", "Roll No", "Student Name", "Course", "Total Classes", "Attended", "Attendance %"]
            rows = [[s['student_id'], s['roll_number'], s['student_name'], s['course_name'], s['total_classes'], s['total_attended'], f"{Color.RED}{s['attendance_pct']}%{Color.END}"] for s in low_students]
            print(format_table(headers, rows))
        except Exception as e:
            print_error(str(e))

    # =========================================================================
    # 4. EXAMINATION & MARKS MANAGEMENT
    # =========================================================================
    def exam_menu(self):
        while True:
            options = [
                ("1", "Create Examination"),
                ("2", "Enter Subject Marks"),
                ("3", "Generate Student Result Card"),
                ("0", "Back to Main Menu")
            ]
            choice = prompt_menu_choice("EXAMINATION & MARKS MANAGEMENT", options)

            if choice == "1":
                self.create_exam()
            elif choice == "2":
                self.enter_marks()
            elif choice == "3":
                self.generate_result_card()
            elif choice == "0":
                break
            else:
                print_error("Invalid selection.")

    def create_exam(self):
        try:
            name = prompt_input("Examination Name (e.g. Mid-Term 2026)")
            course_id = prompt_int("Course ID")
            semester = prompt_int("Semester", default=1)
            exam_date = prompt_input("Exam Date (YYYY-MM-DD)", default="2026-02-15")
            total_marks = prompt_float("Total Max Marks", default=100.0)

            exam_id = self.exam_service.create_examination(name, course_id, semester, exam_date, total_marks)
            print_success(f"Examination '{name}' created with ID {exam_id}!")
        except Exception as e:
            print_error(str(e))

    def enter_marks(self):
        try:
            exam_id = prompt_int("Exam ID")
            subject_id = prompt_int("Subject ID")
            student_id = prompt_int("Student ID")
            marks_obtained = prompt_float("Marks Obtained")
            remarks = prompt_input("Remarks", default="Graded")

            self.exam_service.enter_marks(exam_id, subject_id, student_id, marks_obtained, remarks)
            print_success(f"Marks ({marks_obtained}) saved successfully!")
        except Exception as e:
            print_error(str(e))

    def generate_result_card(self):
        try:
            student_id = prompt_int("Student ID")
            exam_id = prompt_int("Exam ID")

            result = self.exam_service.generate_student_result(student_id, exam_id)
            print_header(f"OFFICIAL RESULT CARD: {result['exam_info']['exam_name']}")
            print(f" Student: {result['student_info']['first_name']} {result['student_info']['last_name']} ({result['student_info']['roll_number']})")
            print(f" Course: {result['student_info']['course_name']} | Semester: {result['student_info']['semester']}")

            sub_headers = ["Subject Code", "Subject Name", "Marks Obtained", "Max Marks", "Grade"]
            sub_rows = [[m['subject_code'], m['subject_name'], m['marks_obtained'], m['total_marks'], m['grade']] for m in result['subject_marks']]
            print(format_table(sub_headers, sub_rows))

            s = result['summary']
            print(f"\n Total Marks: {s['total_obtained']} / {s['total_max_marks']} | Percentage: {s['overall_percentage']}% | Grade: {s['overall_grade']} | Result: {s['status']}")
        except Exception as e:
            print_error(str(e))

    # =========================================================================
    # 5. FEES & PAYMENTS MANAGEMENT
    # =========================================================================
    def fee_menu(self):
        while True:
            options = [
                ("1", "Assign Fee Structure to Student"),
                ("2", "Record Fee Payment"),
                ("3", "View Pending Fees"),
                ("4", "View Paid Fees"),
                ("5", "View Overall Fee Financial Summary"),
                ("0", "Back to Main Menu")
            ]
            choice = prompt_menu_choice("FEES & PAYMENTS MANAGEMENT", options)

            if choice == "1":
                self.assign_fee()
            elif choice == "2":
                self.record_payment()
            elif choice == "3":
                self.view_pending_fees()
            elif choice == "4":
                self.view_paid_fees()
            elif choice == "5":
                self.view_fee_summary()
            elif choice == "0":
                break
            else:
                print_error("Invalid selection.")

    def assign_fee(self):
        try:
            student_id = prompt_int("Student ID")
            semester = prompt_int("Semester", default=1)
            academic_year = prompt_input("Academic Year", default="2025-2026")
            total_amount = prompt_float("Total Fee Amount")
            due_date = prompt_input("Due Date (YYYY-MM-DD)", default="2026-09-01")

            fee = self.fee_service.assign_fee_record(student_id, semester, academic_year, total_amount, due_date)
            print_success(f"Fee record assigned to Student ID {student_id} with Total Amount {total_amount:.2f}!")
        except Exception as e:
            print_error(str(e))

    def record_payment(self):
        try:
            fee_id = prompt_int("Fee Record ID")
            amount = prompt_float("Amount Paid")
            method = prompt_input("Payment Method (UPI/Card/NetBanking/Cash)", default="UPI")
            ref = prompt_input("Transaction Ref Number (leave blank for auto-gen)", default="")

            fee = self.fee_service.record_payment(fee_id, amount, method, ref if ref else None)
            print_success(f"Payment of {amount:.2f} recorded! New Remaining Balance: {fee['remaining_balance']:.2f} (Status: {fee['status']})")
        except Exception as e:
            print_error(str(e))

    def view_pending_fees(self):
        try:
            pending = self.fee_service.get_pending_fees_report()
            print_header("PENDING & PARTIAL FEE RECORDS")
            headers = ["Fee ID", "Roll No", "Student Name", "Course", "Sem", "Total Fee", "Paid Amount", "Remaining Balance", "Due Date", "Status"]
            rows = [[f['fee_id'], f['roll_number'], f['student_name'], f['course_name'], f['semester'], f"{float(f['total_amount']):.2f}", f"{float(f['paid_amount']):.2f}", f"{float(f['remaining_balance']):.2f}", f['due_date'], f['status']] for f in pending]
            print(format_table(headers, rows))
        except Exception as e:
            print_error(str(e))

    def view_paid_fees(self):
        try:
            paid = self.fee_service.get_paid_fees_report()
            print_header("FULLY PAID FEE RECORDS")
            headers = ["Fee ID", "Roll No", "Student Name", "Course", "Semester", "Academic Year", "Total Amount", "Status"]
            rows = [[f['fee_id'], f['roll_number'], f['student_name'], f['course_name'], f['semester'], f['academic_year'], f"{float(f['total_amount']):.2f}", f"{Color.GREEN}Paid{Color.END}"] for f in paid]
            print(format_table(headers, rows))
        except Exception as e:
            print_error(str(e))

    def view_fee_summary(self):
        try:
            summary = self.fee_service.get_fee_summary()
            print_header("FEE FINANCIAL TELEMETRY SUMMARY")
            print(f" Total Fee Records Issued: {summary.get('total_fee_records', 0)}")
            print(f" Total Receivable Amount:  ₹{float(summary.get('total_receivable') or 0):.2f}")
            print(f" Total Collected Amount:   {Color.GREEN}₹{float(summary.get('total_collected') or 0):.2f}{Color.END}")
            print(f" Total Outstanding Balance:{Color.RED} ₹{float(summary.get('total_pending') or 0):.2f}{Color.END}")
        except Exception as e:
            print_error(str(e))

    # =========================================================================
    # 6. REPORTS & ANALYTICS
    # =========================================================================
    def reports_menu(self):
        while True:
            options = [
                ("1", "Department-wise Student List"),
                ("2", "Course-wise Student List"),
                ("3", "Low Attendance Alert Report (< 75%)"),
                ("4", "Fee Pending Defaulter List"),
                ("0", "Back to Main Menu")
            ]
            choice = prompt_menu_choice("SYSTEM REPORTS & ANALYTICS", options)

            if choice == "1":
                self.department_report()
            elif choice == "2":
                self.course_report()
            elif choice == "3":
                self.view_low_attendance()
            elif choice == "4":
                self.view_pending_fees()
            elif choice == "0":
                break
            else:
                print_error("Invalid selection.")

    def department_report(self):
        try:
            dept_id = prompt_int("Enter Department ID")
            students = self.student_service.student_repo.get_department_students(dept_id)
            print_header(f"DEPARTMENT STUDENT REPORT (ID: {dept_id})")
            headers = ["Student ID", "Roll No", "Full Name", "Course", "Semester", "Email"]
            rows = [[s['student_id'], s['roll_number'], s['full_name'], s['course_name'], s['semester'], s['email']] for s in students]
            print(format_table(headers, rows))
        except Exception as e:
            print_error(str(e))

    def course_report(self):
        try:
            course_id = prompt_int("Enter Course ID")
            students = self.student_service.student_repo.get_course_students(course_id)
            print_header(f"COURSE STUDENT REPORT (ID: {course_id})")
            headers = ["Student ID", "Roll No", "Full Name", "Semester", "Email"]
            rows = [[s['student_id'], s['roll_number'], s['full_name'], s['semester'], s['email']] for s in students]
            print(format_table(headers, rows))
        except Exception as e:
            print_error(str(e))
