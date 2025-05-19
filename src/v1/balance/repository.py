from balance.schemas import BalanceResponse, BalanceCharge
from balance.models import Base, UserBalance
from entity.models import Entity
from auth.schemas import UserResponse
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi import HTTPException

class BalanceRepository:

    def get_my_balance(self, user_id, db: Session):
        return db.query(UserBalance).filter(UserBalance.user_id == user_id).all()

    def charge_my_balance(self, charge_balance: BalanceCharge, user: UserResponse, db):
        balance = (
            db.query(UserBalance)
            .filter(UserBalance.user_id == user.id, UserBalance.entity_id == charge_balance.entity_id)
            .first()
        )
        entity = (
            db.query(Entity)
            .filter(Entity.id == charge_balance.entity_id)
            .first()
            )
        if not entity:
            raise HTTPException(status_code=400, detail="Not existing entity")
        
        if not balance:
            balance = self.create_balance(charge_balance, user, db)
        else:
            balance.amount += charge_balance.amount
            db.commit()
            db.refresh(balance)
            return balance
        return balance

    def create_balance(self, charge_balance: BalanceCharge, user: UserResponse, db):
        db_post = UserBalance(
            user_id=user.id,
            entity_id=charge_balance.entity_id,
            amount=charge_balance.amount
        )

        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post