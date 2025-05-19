from auth.models import Base, User
from auth.schemas import UserResponse, UserCreate, UserLogin
from database import SessionLocal, engine
import bcrypt

class AuthRepository:

    def create_user(self, user: UserCreate, db):

        password_hashed = bcrypt.hashpw(
            user.password.encode("utf-8"), bcrypt.gensalt(14)
        )

        db_post = User(
            username=user.username,
            password_hashed=password_hashed.decode("utf-8"),
            email=user.email,
            bio=user.bio, 
            location=user.location
        )

        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        return db_post