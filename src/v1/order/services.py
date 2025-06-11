from fastapi import HTTPException
from fastapi.responses import JSONResponse

# from order.schemas import OrderResponse, OrderCreate
from order.models import Base, Order
from inventory.models import UserInventory
from auth.models import User


class OrderService:
    def create_order(order, db, user):
        inventory = (
            db.query(UserInventory)
            .filter(
                UserInventory.id == order.entity_in_inventory_id,
                UserInventory.user_id == user.id,
            )
            .first()
        )

        try:
            if not inventory or inventory.in_sale != "False":
                db.rollback()
                raise HTTPException(status_code=400, detail="Not enough in inventory")

            inventory.in_sale="True"

            db_post = Order(
                user_id=user.id,
                entity_in_inventory_id=order.entity_in_inventory_id,
                entity_id=inventory.entity_id,
                price=order.price
            )

            db.add(db_post)
            db.commit()
        except:
            db.rollback()
            raise

        response = JSONResponse(content="true")
        return response

    def order_buy(order_buy, db, user):

        order_to_buy: Order = (
            db.query(Order)
            .filter(Order.id == order_buy.order_id, Order.user_id != user.id)
            .order_by(Order.price.asc())
            .first()
        )
        if not order_to_buy:
            raise HTTPException(status_code=404, detail="No roots for this action.")

        total_cost = order_to_buy.price
        if total_cost > user.balance:
            raise HTTPException(status_code=400, detail="Not enough balance.")

        item_in_inventory = (
            db.query(UserInventory)
            .filter(
                UserInventory.id == order_to_buy.entity_in_inventory_id,
            )
            .first()
        )

        try:
            seller_user: User = db.query(User).filter(User.id == order_to_buy.user_id).first()
            buyer_user: User = db.query(User).filter(User.id == user.id).first()

            if not seller_user or not buyer_user:
                raise HTTPException(status_code=404, detail="User not found.")

            seller_user.balance += total_cost
            buyer_user.balance -= total_cost


            db_post = UserInventory(
                user_id=buyer_user.id,
                entity_id=item_in_inventory.entity_id,
                entity_wear=item_in_inventory.entity_wear
            )
            db.add(db_post)

            db.add(buyer_user)
            db.add(seller_user)
            db.delete(order_to_buy)
            db.delete(item_in_inventory)

            db.commit()
        except:
            db.rollback()
            raise

        response = JSONResponse(content="true")
        return response

    def order_delete(order_delete, db, user):
        order_to_delete: Order = (
            db.query(Order)
            .filter(Order.id == order_delete.order_id, Order.user_id == user.id)
            .first()
        )


        if not order_to_delete:
            raise HTTPException(status_code=404, detail="No roots for this action.")

        item_in_buyer_inventory = (
            db.query(UserInventory)
            .filter(
                UserInventory.entity_id == order_to_delete.entity_id,
                UserInventory.user_id == user.id,
            )
            .first()
        )

        try:
            db.delete(order_to_delete)


            db_post = UserInventory(
                user_id=user.id,
                entity_id=order_to_delete.entity_id
            )
            db.add(db_post)

            db.commit()
        except:
            db.rollback()
            raise

        response = JSONResponse(content="true")
        return response