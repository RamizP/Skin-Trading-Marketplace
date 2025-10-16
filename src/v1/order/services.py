from fastapi import HTTPException
from sqlalchemy.orm import Session

from sqlalchemy import text
from auth.models import User
from order.models import Order, Side
from inventory.models import UserInventory
from order.repository import OrderRepository
from order.schemas import OrderCreate, OrderDelete, OrderBuy, OrderResponse

from auth.schemas import UserResponse

from trading.engine import TradingEngine


class OrderService:

    def __init__(self):
        self.engine = TradingEngine(order_service=self)

    # ----------------------Public Methods----------------------------------
    def create_order(self, order: OrderCreate, db, user) -> OrderResponse:
        try:
            self._validate_order_input(order)
            db.execute(text("BEGIN IMMEDIATE;"))
            inventory = self._get_inventory_item_locked(
                db, order.entity_in_inventory_id, user.id
            )

            if order.side == Side.SELL and order.entity_in_inventory_id != 0 and inventory:
                db_post = self._create_sell_order(db, user, order, inventory)

            elif order.side == Side.BUY:
                self._ensure_no_existing_buy_order(user, order, db)
                db_post = self._create_buy_order(order, user)

            else:
                raise HTTPException(status_code=400, detail="Something went wrong.")

            db.add(db_post)

            if inventory:
                db.add(inventory)

            db.commit()
            buy_request = OrderBuy(order_id=db_post.id)
            self.engine.match_buy_request(buy_request, user, db)

        except Exception as e:
            db.rollback()
            raise

        return OrderResponse.model_validate(db.query(Order).filter(Order.id == db_post.id).first())

    def order_buy(self, order_buy: OrderBuy, db, user) -> OrderResponse:

        try:
            db.execute(text("BEGIN IMMEDIATE;"))

            order_to_buy: Order = self._get_order_to_buy(order_buy, user, db)

            if order_to_buy.side == Side.BUY:
                raise HTTPException(
                    status_code=404, detail="It seems you cant buy this order."
                )


            item_in_inventory = self._get_inventory_item_locked(
                db, order_to_buy.entity_in_inventory_id
            )

            self._execute_cash_transaction(order_to_buy, user, db)

            # Adding the Item to buyer inventory after a successful purchase
            new_inventory_item = UserInventory(
                user_id=user.id,
                entity_id=item_in_inventory.entity_id,
                entity_wear=item_in_inventory.entity_wear,
            )
            db.add(new_inventory_item)

            # Deleting the order from Marketplace, and sellers inventory
            db.delete(order_to_buy)
            db.delete(item_in_inventory)

            buy_request = (
                db.query(Order)
                .with_for_update()
                .filter(
                    Order.user_id == user.id,
                    Order.side == Side.BUY,
                    Order.entity_id == item_in_inventory.entity_id,
                )
                .first()
            )

            if buy_request:
                db.delete(buy_request)

            # Committing the whole transaction
            db.commit()

            return OrderResponse.model_validate(order_to_buy)
        except Exception as e:
            db.rollback()
            raise

        return OrderResponse.model_validate(order_to_buy)

    def order_delete(self, order_delete: OrderDelete, db, user) -> OrderResponse:

        try:
            db.execute(text("BEGIN IMMEDIATE;"))
            order_to_delete: Order = db.query(Order).with_for_update().filter(Order.id == order_delete.order_id).order_by(Order.price.asc()).first()


            if not order_to_delete or order_to_delete.user_id != user.id:
                raise HTTPException(
                    status_code=404, detail="It seems you cant delete this order."
                )

            item_in_inventory = (
                db.query(UserInventory)
                .with_for_update()
                .filter(
                    UserInventory.entity_id == order_to_delete.entity_id,
                    UserInventory.user_id == user.id,
                )
                .first()
            )

            if not item_in_inventory:
                raise HTTPException(status_code=404, detail="Inventory item not found.")

            db.delete(order_to_delete)

            item_in_inventory.in_sale = False
            db.add(item_in_inventory)
            db.commit()

        except Exception as e:
            db.rollback()
            raise

        return OrderResponse.model_validate(order_to_delete)

    # ----------------------Private Helpers----------------------------------
    def _get_inventory_item_locked(
        self, db: Session, inventory_id: int, user_id: int = None
    ):
        query = (
            db.query(UserInventory)
            .with_for_update()
            .filter(UserInventory.id == inventory_id)
        )
        if user_id:
            query = query.filter(UserInventory.user_id == user_id)
        return query.first()

    def _create_sell_order(
        self,
        db: Session,
        user: UserResponse,
        order: OrderCreate,
        inventory: UserInventory,
    ):

        # lock the inventory
        db.query(Order).with_for_update().filter(
            Order.entity_in_inventory_id == order.entity_in_inventory_id
        ).all()

        if inventory.in_sale:
            raise HTTPException(status_code=404, detail="Item not found in inventory.")

        inventory.in_sale = 1

        # Creating the new Order
        order = Order(
            user_id=user.id,
            entity_in_inventory_id=order.entity_in_inventory_id,
            entity_id=inventory.entity_id,
            price=order.price,
            side=order.side,
        )
        return order

    def _create_buy_order(self, order, user):
        return Order(
            user_id=user.id,
            entity_id=order.entity_id,
            price=order.price,
            side=order.side,
        )

    def _ensure_no_existing_buy_order(self, user, order, db):
        user_order = (
            db.query(Order)
            .with_for_update()
            .filter(
                Order.entity_id == order.entity_id,
                Order.user_id == user.id,
                Order.side == Side.BUY,
            )
            .all()
        )
        if user_order:
            raise HTTPException(
                status_code=400,
                detail="You already have an order for this item",
            )

    def _execute_cash_transaction(self, order_to_buy, user, db):
        # Getting both user from DB
        seller_user: User = (
            db.query(User)
            .with_for_update()
            .filter(User.id == order_to_buy.user_id)
            .first()
        )
        buyer_user: User = (
            db.query(User).with_for_update().filter(User.id == user.id).first()
        )
        if not seller_user or not buyer_user:
            raise HTTPException(status_code=404, detail="User not found.")
        total_cost = order_to_buy.price
        if total_cost > buyer_user.balance:
            raise HTTPException(status_code=400, detail="Not enough balance.")
        # Initiate balance transaction
        seller_user.balance += total_cost
        buyer_user.balance -= total_cost

        db.add(buyer_user)
        db.add(seller_user)

    def _get_order_to_buy(self, order_buy, user, db):
        order_to_buy: Order = OrderRepository.get_order_by_id(db, order_buy.order_id)

        if not order_to_buy:
            raise HTTPException(status_code=404, detail="Order not found.")
        if order_to_buy.user_id == user.id:
            raise HTTPException(
                status_code=403, detail="You cannot buy your own order."
            )

        return order_to_buy

    def _validate_inventory_for_sell(self, inventory):
        if not inventory:
            raise HTTPException(status_code=400, detail="Inventory item not found.")
        if inventory.in_sale:
            raise HTTPException(status_code=400, detail="Item is already in sale.")

    def _validate_order_input(self, order):
        if order.price <= 0:
            raise HTTPException(status_code=400, detail="Price must be greater than 0.")
        if order.side not in (Side.BUY, Side.SELL):
            raise HTTPException(status_code=400, detail="Invalid order side.")

    def _validate_buy_order(self, order_to_buy, buyer, db):
        if order_to_buy.user_id == buyer.id:
            raise HTTPException(status_code=403, detail="Cannot buy your own order.")
        buyer_user = db.query(User).filter(User.id == buyer.id).first()
        if order_to_buy.price > buyer_user.balance:
            raise HTTPException(status_code=400, detail="Insufficient balance.")
