import bcrypt
from auth.models import User
from auth.schemas import UserCreate


class AuthRepository:
    def __init__(self, db):
        self.db = db

    def create_user(self, user: UserCreate):

        password_hashed = bcrypt.hashpw(
            user.password.encode("utf-8"), bcrypt.gensalt(14)
        )

        db_post = User(
            username=user.username,
            password_hashed=password_hashed.decode("utf-8"),
            email=user.email,
            bio=user.bio,
            location=user.location,
        )

        self.db.add(db_post)
        self.db.commit()
        self.db.refresh(db_post)

        return db_post

    def get_user_by_id(self, user_id):
        return self.db.query(User).with_for_update().filter(User.id == user_id).first()
