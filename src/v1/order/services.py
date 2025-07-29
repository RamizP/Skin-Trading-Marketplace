from fastapi import HTTPException
from fastapi.responses import JSONResponse

# from order.schemas import OrderResponse, OrderCreate
from order.models import Base, Order
from inventory.models import UserInventory
from auth.models import User
from order.repository import OrderRepository
from inventory.repository import InventoryRepository


class OrderService:

    def create_order(order, db, user):
        try:
            inventory = (
                db.query(UserInventory)
                .with_for_update()
                .filter(
                    UserInventory.id == order.entity_in_inventory_id,
                    UserInventory.user_id == user.id,
                )
                .first()
            )
            if not inventory or inventory.in_sale != "False":
                db.rollback()
                raise HTTPException(status_code=400, detail="Not enough in inventory")

            inventory.in_sale="True"

            #Creating the new Order
            db_post = Order(
                user_id=user.id,
                entity_in_inventory_id=order.entity_in_inventory_id,
                entity_id=inventory.entity_id,
                price=order.price
            )

            db.add(db_post)
            db.add(inventory)
            db.commit()
        except:
            db.rollback()
            raise

        response = JSONResponse(content="success")
        return response

    def order_buy(order_buy, db, user):

        try:
            order_to_buy: Order = OrderRepository.get_order_by_id(db, order_buy.order_id)

            if not order_to_buy or order_to_buy.user_id == user.id:
                raise HTTPException(status_code=404, detail="It seems you cant buy this order.")

            item_in_inventory = (
                db.query(UserInventory)
                .with_for_update()
                .filter(
                    UserInventory.id == order_to_buy.entity_in_inventory_id,
                )
                .first()
            )

            #Getting both user from DB
            seller_user: User = db.query(User).with_for_update().filter(User.id == order_to_buy.user_id).first()
            buyer_user: User = db.query(User).with_for_update().filter(User.id == user.id).first()


            total_cost = order_to_buy.price
            if total_cost > buyer_user.balance:
                raise HTTPException(status_code=400, detail="Not enough balance.")

            if not seller_user or not buyer_user:
                raise HTTPException(status_code=404, detail="Users not found.")

            #Initiate balance transaction
            seller_user.balance += total_cost
            buyer_user.balance -= total_cost

    	    #Adding the Item to buyer inventory after a successful purchase
            db_post = UserInventory(
                user_id=buyer_user.id,
                entity_id=item_in_inventory.entity_id,
                entity_wear=item_in_inventory.entity_wear
            )
            db.add(db_post)

            #Updating balances of users
            db.add(buyer_user)
            db.add(seller_user)

            #Deleting the order from Marketplace, and sellers inventory
            db.delete(order_to_buy)
            db.delete(item_in_inventory)

            #Committing the whole transaction
            db.commit()
        except:
            db.rollback()
            raise

        response = JSONResponse(content="success")
        return response

    def order_delete(order_delete, db, user):

        try:
            order_to_delete: Order = OrderRepository.get_order_by_id(db, order_delete.order_id)

            if not order_to_delete or order_to_delete.user_id != user.id:
                raise HTTPException(status_code=404, detail="It seems you cant delete this order.")

            item_in_inventory = db.query(UserInventory).filter(UserInventory.entity_id == order_to_delete.entity_id, UserInventory.user_id == user.id).first()

            db.delete(order_to_delete)

            item_in_inventory.in_sale="False"
            db.add(item_in_inventory)
            db.commit()

        except:
            db.rollback()
            raise

        response = JSONResponse(content="success")
        return response
