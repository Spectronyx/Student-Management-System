import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_NAME: str = os.getenv("DB_NAME", "defaultdb")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_SSL: bool = os.getenv("DB_SSL", "true").lower() in ("true", "1", "yes")
    
    JWT_SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_student_tracker_jwt_key_2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

settings = Settings()
