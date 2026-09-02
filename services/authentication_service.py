from typing import Optional, Dict, Any, Tuple
from repositories.user_repository import UserRepository
from repositories.student_repository import StudentRepository
from repositories.teacher_repository import TeacherRepository
from utils.security import verify_password
from utils.validators import ValidationError
from models.user import User

class AuthenticationService:
    """Manages user authentication, session state, and role authorization."""

    def __init__(self):
        self.user_repo = UserRepository()
        self.student_repo = StudentRepository()
        self.teacher_repo = TeacherRepository()
        self.current_user: Optional[User] = None
        self.profile_data: Optional[Dict[str, Any]] = None

    def login(self, username: str, password: str) -> Tuple[User, Optional[Dict[str, Any]]]:
        if not username or not password:
            raise ValidationError("Username and password are required.")

        user_dict = self.user_repo.get_by_username(username.strip())
        if not user_dict:
            raise ValidationError("Invalid username or password.")

        if not user_dict.get('is_active', True):
            raise ValidationError("Account is deactivated. Please contact the administrator.")

        if not verify_password(password.strip(), user_dict['password_hash']):
            raise ValidationError("Invalid username or password.")

        user = User.from_dict(user_dict)
        self.current_user = user

        # Fetch associated role profile details
        profile = None
        if user.role == 'Student':
            profile = self.student_repo.get_by_user_id(user.user_id)
        elif user.role == 'Teacher':
            profile = self.teacher_repo.get_by_user_id(user.user_id)
        elif user.role == 'Admin':
            profile = {"user_id": user.user_id, "username": user.username, "role": "Admin", "email": user.email}

        self.profile_data = profile
        return user, profile

    def logout(self):
        self.current_user = None
        self.profile_data = None

    def is_logged_in(self) -> bool:
        return self.current_user is not None

    def require_role(self, *allowed_roles: str):
        if not self.is_logged_in():
            raise PermissionError("User is not authenticated. Please log in first.")
        if self.current_user.role not in allowed_roles:
            raise PermissionError(f"Access denied. Requires role: {', '.join(allowed_roles)}.")
