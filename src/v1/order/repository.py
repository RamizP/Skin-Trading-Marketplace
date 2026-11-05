from entity.models import Entity
from inventory.models import UserInventory
from order.models import Order, Side
from sqlalchemy import func


class OrderRepository:
    def __init__(self, db):
        self.db = db

    def get_order_by_id(self, order_id):
        order: Order = (
            self.db.query(Order).with_for_update().filter(Order.id == order_id).first()
        )
        return order

    def get_orders_by_id(self, order_id):
        order = (
            self.db.query(Order, UserInventory, Entity)
            .join(UserInventory, UserInventory.id == Order.entity_in_inventory_id)
            .join(Entity, Entity.id == UserInventory.entity_id)
            .filter(Order.entity_id == order_id, Order.side == Side.SELL)
            .order_by(Order.price.asc())
            .all()
        )
        return order

    def get_user_buy_orders_by_entity(self, entity_id, user_id):
        return (
            self.db.query(Order)
            .filter(
                Order.entity_id == entity_id,
                Order.user_id == user_id,
                Order.side == Side.BUY,
            )
            .order_by(Order.price.desc())
            .all()
        )

    def get_highest_buy_orders_by_entity(self, entity_id):
        return (
            self.db.query(Order)
            .filter(
                Order.entity_id == entity_id,
                Order.side == Side.BUY,
            )
            .order_by(Order.price.desc())
            .first()
        )

    def get_all_orders_by_lowest_price(self):
        lowest_price = func.min(Order.price)

        orders = (
            self.db.query(Entity, lowest_price)
            .join(Order, Order.entity_id == Entity.id)
            .filter(Order.side == Side.SELL)
            .group_by(Entity.id)
            .all()
        )

        return orders

    def get_suitable_buy_order(self, user_id, side, entity_id):
        buy_order = (
            self.db.query(Order)
            .with_for_update()
            .filter(
                Order.user_id == user_id,
                Order.side == side,
                Order.entity_id == entity_id,
            )
            .first()
        )
        return buy_order

    def get_user_order(self, entity_id, user_id, side):
        return (
            self.db.query(Order)
            .with_for_update()
            .filter(
                Order.entity_id == entity_id,
                Order.user_id == user_id,
                Order.side == side,
            )
            .all()
        )

    def add(self, Order):
        self.db.add(Order)

    def delete(self, Order):
        self.db.delete(Order)
