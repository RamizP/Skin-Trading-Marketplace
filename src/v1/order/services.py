import os
from fastapi import HTTPException
from fastapi.responses import JSONResponse
# from order.schemas import OrderResponse, OrderCreate
from order.models import Base, Order
from inventory.models import UserInventory


class OrderService:
    def create_order(order, db, user):
        inventory = db.query(UserInventory).filter(UserInventory.entity_id == order.entity_id, UserInventory.user_id == user.id).first()

        try:
            if not inventory or inventory.amount < order.amount or order.amount <= 0:
                db.rollback()
                raise HTTPException(status_code=400, detail="Not enough inventory")

            inventory.amount -= order.amount

            if inventory.amount <= 0:
                db.delete(inventory)

            db_post = Order(
                 orderer_id=user.id,
                 entity_id=order.entity_id,
                 price=order.price,
                 amount=order.amount
             )

            db.add(db_post)
            db.commit()
        except:
            db.rollback()
            raise

        response = JSONResponse(content="true")
        return response