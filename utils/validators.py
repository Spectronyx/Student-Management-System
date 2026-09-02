import re
from datetime import datetime, date
from typing import Union

class ValidationError(Exception):
    """Custom exception raised when input validation fails."""
    pass

def validate_email(email: str) -> str:
    if not email or not isinstance(email, str):
        raise ValidationError("Email address is required.")
    email = email.strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email format: '{email}'")
    return email

def validate_phone(phone: str) -> str:
    if not phone or not isinstance(phone, str):
        raise ValidationError("Phone number is required.")
    phone = phone.strip()
    pattern = r'^\+?[0-9]{10,15}$'
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    if not re.match(pattern, clean_phone):
        raise ValidationError(f"Invalid phone number format: '{phone}'. Expected 10-15 digits.")
    return clean_phone

def validate_date(date_input: Union[str, date], field_name: str = "Date") -> date:
    if isinstance(date_input, date):
        return date_input
    if not date_input or not isinstance(date_input, str):
        raise ValidationError(f"{field_name} is required.")
    date_str = date_input.strip()
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValidationError(f"Invalid date for {field_name}: '{date_str}'. Expected format YYYY-MM-DD or DD/MM/YYYY.")

def validate_marks(marks_input: Union[str, float, int]) -> float:
    try:
        marks = float(marks_input)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid marks value: '{marks_input}'. Must be a number.")
    if marks < 0.0 or marks > 100.0:
        raise ValidationError(f"Marks must be between 0.0 and 100.0, got {marks}.")
    return marks

def validate_roll_number(roll: str) -> str:
    if not roll or not isinstance(roll, str):
        raise ValidationError("Roll number is required.")
    roll = roll.strip()
    if len(roll) < 3 or len(roll) > 30:
        raise ValidationError("Roll number must be between 3 and 30 characters.")
    return roll

def validate_required(val: str, field_name: str) -> str:
    if not val or not str(val).strip():
        raise ValidationError(f"Field '{field_name}' is required and cannot be empty.")
    return str(val).strip()

def validate_positive_number(val: Union[str, float, int], field_name: str) -> float:
    try:
        num = float(val)
        if num < 0:
            raise ValueError()
        return num
    except Exception:
        raise ValidationError(f"{field_name} must be a positive number.")
