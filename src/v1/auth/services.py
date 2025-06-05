import os
from dotenv import load_dotenv
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pytest import Session
from auth.models import User
from auth.utils import AuthUtils
from auth.repository import AuthRepository
import Exceptions
from auth.schemas import UserResponse
from auth.strategy.AuthStrategy import JWTAuthStrategy

load_dotenv()


class AuthService:
    def __init__(self):
        self._secret_key = os.getenv("SECRET_KEY")
        self._algorithm = "HS256"

    def login(self, user, db):
        return JWTAuthStrategy(self._secret_key, self._algorithm).login(user, db)

    def register(self, user, db):
        return JWTAuthStrategy(self._secret_key, self._algorithm).register(user, db)
    
    def logout(self):
        return JWTAuthStrategy(self._secret_key, self._algorithm).logout()
    
    def current_user(self, token: str, db: Session) -> UserResponse:
        return JWTAuthStrategy(self._secret_key, self._algorithm).current_user(token, db)

    def user_balance_charge(self, balance_charge, db, user):
        existing_user = db.query(User).filter(User.id == user.id).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        existing_user.balance += balance_charge.amount
        user.balance += balance_charge.amount
        db.commit()
        db.refresh(existing_user)
        return user
    