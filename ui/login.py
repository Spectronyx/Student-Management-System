from services.authentication_service import AuthenticationService
from ui.admin_menu import AdminMenu
from ui.teacher_menu import TeacherMenu
from ui.student_menu import StudentMenu
from ui.common import prompt_input, prompt_password
from utils.helpers import Color, print_header, print_error, print_success, print_info

class LoginUI:
    """Authentication and Role Routing UI Manager."""

    def __init__(self):
        self.auth_service = AuthenticationService()

    def start(self):
        while True:
            print_header("STUDENT MANAGEMENT SYSTEM - AUTHENTICATION")
            print(f" Demo Accounts:")
            print(f"   🔑 Admin:   username: {Color.BOLD}admin{Color.END}     password: {Color.BOLD}admin123{Color.END}")
            print(f"   🔑 Teacher: username: {Color.BOLD}prof_sharma{Color.END} password: {Color.BOLD}teacher123{Color.END}")
            print(f"   🔑 Student: username: {Color.BOLD}student1{Color.END}    password: {Color.BOLD}student123{Color.END}")
            print("-" * 70)
            
            username = prompt_input("Username (or 'exit' to quit)")
            if username.lower() in ('exit', 'quit', 'q'):
                print_info("Exiting application. Goodbye!")
                break

            password = prompt_password("Password")

            try:
                user, profile = self.auth_service.login(username, password)
                print_success(f"Welcome back, {user.username}! (Role: {user.role})")

                if user.role == 'Admin':
                    AdminMenu(self.auth_service).run()
                elif user.role == 'Teacher':
                    TeacherMenu(self.auth_service).run()
                elif user.role == 'Student':
                    StudentMenu(self.auth_service).run()
                else:
                    print_error(f"Unknown role '{user.role}'. Access denied.")

            except Exception as e:
                print_error(str(e))
