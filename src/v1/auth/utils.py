import bcrypt
import Exceptions


class AuthUtils:
    def password_check(password, hashed_password):
        if (
            bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
            == False
        ):
            raise Exceptions.FALSE_CREDENTIALS()
