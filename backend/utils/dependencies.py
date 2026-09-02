from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.security import decode_access_token
from database import fetch_one

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency that verifies Bearer JWT token and returns current user dict."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "Invalid or expired authentication token", "error": "UNAUTHORIZED"}
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "Malformed token payload", "error": "UNAUTHORIZED"}
        )

    user = fetch_one("SELECT user_id, username, email, role, name, is_active FROM users WHERE user_id = %s", (user_id,))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "User associated with token no longer exists", "error": "USER_NOT_FOUND"}
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": "User account is inactive", "error": "ACCOUNT_INACTIVE"}
        )

    return user

def require_role(*roles: str):
    """Dependency factory for role-based authorization."""
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"success": False, "message": f"Access denied. Requires one of roles: {list(roles)}", "error": "FORBIDDEN"}
            )
        return current_user
    return role_checker
