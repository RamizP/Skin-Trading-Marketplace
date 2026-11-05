from fastapi import HTTPException


def FALSE_CREDENTIALS():
    return HTTPException(status_code=401, detail="false username or password")
