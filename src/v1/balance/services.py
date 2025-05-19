import os
from fastapi import HTTPException
from balance.schemas import BalanceResponse, BalanceCharge
from balance.repository import BalanceRepository
from auth.schemas import UserResponse
from balance.models import Base, UserBalance


class BalanceService:
    def charge(charge_balance: BalanceCharge, user: UserResponse, db):
        return BalanceRepository().charge_my_balance(charge_balance, user, db)