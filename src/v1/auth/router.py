from fastapi import FastAPI, Depends, HTTPException, status, Response, Request, Cookie
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from auth.models import Base, User
from auth.repository import AuthRepository
from auth.services import AuthService
from auth.schemas import UserResponse, UserCreate, UserLogin
from auth.utils import AuthUtils

from database import SessionLocal, engine, get_db
from sqlalchemy.orm import Session

from Dependencies import is_admin, get_current_user

import Exceptions
import bcrypt


# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My API",
    description="This is a custom API using OpenAPI with FastAPI",
    version="1.0.0",
    openapi_url="/custom_openapi.json",
)

origins = ["http://127.0.0.1:5500", "http://192.168.1.6:5500"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    created_user = AuthRepository().create_user(user, db)
    token = AuthService().create_token(created_user.id)
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

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user is None:
        raise Exceptions.FALSE_CREDENTIALS()

    AuthUtils.password_check(user.password, existing_user.password_hashed)

    token = AuthService().create_token(existing_user.id)
    content = {"token": token}
    response = JSONResponse(content=content)
    response.set_cookie(
        key="Authentication", value=token, httponly=True, samesite="lax", secure=True
    )
    return response


@app.post("/logout/")
def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("Authentication")
    return response


@app.get("/me/", response_model=UserResponse)
def me(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return user
