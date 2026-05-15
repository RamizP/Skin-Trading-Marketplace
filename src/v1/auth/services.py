import os
from dotenv import load_dotenv
from fastapi import HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pytest import Session
from auth.models import User
from auth.utils import AuthUtils
from auth.repository import AuthRepository
import Exceptions
from auth.schemas import UserResponse
from auth.strategy.AuthStrategy import JWTAuthStrategy, TYPO3AuthStrategy
from auth.strategy import AuthStrategyInterface

load_dotenv()


class AuthService:
    def __init__(self, auth_strategy: AuthStrategyInterface = None):
        self._secret_key = os.getenv("SECRET_KEY")
        self.token_live_time = int(os.getenv("TOKEN_LIVE_TIME", 60))  # in minutes
        self._algorithm = "HS256"
        self.auth_strategy: AuthStrategyInterface = auth_strategy or JWTAuthStrategy(self._secret_key, self._algorithm)

    def login(self, user, db):
        return self.auth_strategy.login(user, db)

    def register(self, user, db):
        return self.auth_strategy.register(user, db)

    def logout(self):
        return self.auth_strategy.logout()

    def current_user(self, token: str, db: Session = None) -> UserResponse:
        return self.auth_strategy.current_user(token, db)

    def user_balance_charge(self, balance_charge, db, user):
        existing_user = db.query(User).filter(User.id == user.id).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        existing_user.balance += balance_charge.amount
        user.balance += balance_charge.amount
        db.commit()
        db.refresh(existing_user)
        return user