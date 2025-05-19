import os
from dotenv import load_dotenv
from fastapi import HTTPException, Request
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta
from auth.schemas import JwtData, UserResponse
from auth.models import Base, User
from sqlalchemy.orm import Session
load_dotenv()


class AuthService:
    def __init__(self):
        self._secret_key = os.getenv("SECRET_KEY")
        self._algorithm = "HS256"

    def create_token(self, user_id) -> str:
        expire = datetime.utcnow() + timedelta(minutes=60)
        payload = {"sub": str(user_id), "exp": expire}
        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return token

    def validate_jwt(self, token: str) -> JwtData:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=self._algorithm)
            
            return JwtData(**payload)

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has been expired")

        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def current_user(self, token: str, db: Session) -> UserResponse:
        jwt_data = self.validate_jwt(token)
        try:
            user = db.query(User).filter(User.id == int(jwt_data.sub)).first()

            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                status=user.status,
                image_url=user.image_url,
                bio=user.bio,
                location=user.location,
                created_at=user.created_at,
            )

        except Exception as e:

            print(f"Error fetching user: {e}")
            raise HTTPException(
                status_code=401, detail="Invalid token or user not found"
            )
