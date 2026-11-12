from fastapi import HTTPException


def FALSE_CREDENTIALS():
    return HTTPException(status_code=401, detail="false username or password")


class InsufficientBalance(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Not enough balance.",
        )