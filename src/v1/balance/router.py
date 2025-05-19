from sqlalchemy.orm import Session
from balance.models import Base, UserBalance
from balance.repository import BalanceRepository
from balance.services import BalanceService
from balance.utils import BalanceUtils
from auth.services import AuthService
import Exceptions
from Dependencies import is_admin, get_current_user
from balance.schemas import BalanceResponse, BalanceCharge
from database import SessionLocal, engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Request
)
from fastapi.responses import JSONResponse
from typing import List

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My API",
    description="This is a custom API using OpenAPI with FastAPI",
    version="1.0.0",
    openapi_url="/custom_openapi.json",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/balance-charge", response_model=BalanceResponse)
def charge_my_balance(charge_balance: BalanceCharge, request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):

    balance = BalanceService.charge(charge_balance, user, db)

    if balance is None:
        raise HTTPException(status_code=404, detail="Balance not found for user")

    return balance

@app.get("/mybalance", response_model=List[BalanceResponse])
def get_my_balance(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    
    balances = db.query(UserBalance).filter(UserBalance.user_id == user.id).all()
    if balances is None:
        raise HTTPException(status_code=404, detail="Balance not found for user")

    return balances
