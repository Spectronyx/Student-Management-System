import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """System configuration parameters."""
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'student_management')
    DB_SSL = os.getenv('DB_SSL', 'false').lower() in ('true', '1', 'yes')
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'super_secret_student_management_key_2026')
    PASSWORD_SALT = os.getenv('PASSWORD_SALT', 'sms_salt_2026')
    
    # Business logic constants
    ATTENDANCE_THRESHOLD = float(os.getenv('ATTENDANCE_THRESHOLD', 75.0))
    PAGE_SIZE = int(os.getenv('PAGE_SIZE', 10))

config = Config()
