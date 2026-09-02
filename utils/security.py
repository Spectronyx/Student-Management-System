import hashlib
from config import config

def hash_password(password: str, salt: str = None) -> str:
    """Hashes a plain-text password using PBKDF2 HMAC SHA-256."""
    if not password:
        raise ValueError("Password cannot be empty.")
    if salt is None:
        salt = config.PASSWORD_SALT
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()

def verify_password(plain_password: str, stored_hash: str, salt: str = None) -> bool:
    """Verifies a plain-text password against a stored PBKDF2 hash."""
    if not plain_password or not stored_hash:
        return False
    computed_hash = hash_password(plain_password, salt=salt)
    return computed_hash.lower() == stored_hash.lower()

def validate_password_strength(password: str) -> bool:
    """Ensures password meets minimum security requirements (at least 6 chars)."""
    if not password or len(password) < 6:
        return False
    return True
