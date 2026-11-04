from fastapi import APIRouter, Depends

from auth.services import AuthService
from auth.schemas import UserResponse, UserCreate, UserLogin, BalanceCharge

from database import get_db
from sqlalchemy.orm import Session

from Dependencies import get_current_user

router = APIRouter(tags=["Auth"])

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return AuthService().register(user, db)


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return AuthService().login(user, db)


@router.post("/logout")
def logout():
    return AuthService().logout()

@router.get("/user/me", response_model=UserResponse)
def me(user=Depends(get_current_user)):
    return user


@router.post("/me/balance/charge")
def balance_charge(
    balance_charge: BalanceCharge,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return AuthService().user_balance_charge(balance_charge, db, user)
