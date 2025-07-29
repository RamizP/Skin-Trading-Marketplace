from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from auth.services import AuthService
from auth.schemas import UserResponse
from auth.models import User
from database import get_db
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.headers.get('Authentication') or request.cookies.get('Authentication')
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    user = AuthService().current_user(token, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user

def is_admin(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return True
