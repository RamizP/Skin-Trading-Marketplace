from datetime import UTC, datetime, timedelta

import Exceptions
import jwt
from auth.models import User
from auth.repository import AuthRepository
from auth.schemas import JwtData, UserResponse
from auth.strategy.AuthStrategyInterface import AuthStrategyInterface
from auth.utils import AuthUtils
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session


class JWTAuthStrategy(AuthStrategyInterface):
    """Strategy for JWT-based authentication."""

    def __init__(
        self, secret_key: str, algorithm: str = "HS256", token_duration: int = 600
    ):

        self._secret_key = secret_key
        self._algorithm = algorithm
        self.token_duration = token_duration

    def login(self, user_data, db):
        existing_user = (
            db.query(User).filter(User.username == user_data.username).first()
        )
        if existing_user is None:
            raise Exceptions.FALSE_CREDENTIALS()

        AuthUtils.password_check(user_data.password, existing_user.password_hashed)

        token = self.create_token(existing_user.id)
        content = {"token": token}
        response = JSONResponse(content=content)
        response.set_cookie(
            key="Authentication",
            value=token,
            httponly=True,
            secure=True,  # REQUIRED for HTTPS
            samesite="none",  # REQUIRED for cross-origin
            max_age=60 * 60 * 24,  # equal to 1 day
        )
        return response

    def register(self, user_data, db):
        existing_user = (
            db.query(User)
            .filter(
                or_(User.username == user_data.username, User.email == user_data.email)
            )
            .first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Something went wrong")

        created_user = AuthRepository(db).create_user(user_data)
        token = self.create_token(created_user.id)
        content = {"token": token}
        response = JSONResponse(content=content)
        response.set_cookie(
            key="Authentication",
            value=token,
            httponly=True,
            samesite="lax",
            secure=True,
        )

        return response

    def logout(self) -> JSONResponse:
        response = JSONResponse(content={"message": "Logout successful"})
        response.delete_cookie("Authentication")
        return response

    def create_token(self, user_id) -> str:
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")

        expire = datetime.now(UTC) + timedelta(minutes=self.token_duration)
        payload = {"sub": str(user_id), "exp": expire}
        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return token

    def validate_jwt(self, token: str) -> JwtData:
        if not token:
            raise HTTPException(status_code=401, detail="Token is missing")

        try:
            payload = jwt.decode(token, self._secret_key, algorithms=self._algorithm)

            return JwtData(**payload)

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has been expired")

        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def current_user(self, token: str, db: Session) -> UserResponse:
        if not token:
            raise HTTPException(status_code=401, detail="Token is missing")
        if not isinstance(token, str):
            raise HTTPException(status_code=400, detail="Token must be a string")

        jwt_data = self.validate_jwt(token)
        user = db.query(User).filter(User.id == int(jwt_data.sub)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return UserResponse.model_validate(user)
