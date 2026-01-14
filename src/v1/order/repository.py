from order.models import Base, Order
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from sqlalchemy import func
from order.models import Base, Order
from entity.models import Base, Entity
from inventory.models import Base, UserInventory
from order.schemas import OrderCreate, OrderDelete, OrderBuy, OrderResponse

class OrderRepository:

    def __init__(self, db):
        self.db = db
    # def create_order(order: OrderCreate, db: Session):
    #     db_post = Order(
    #         name=order.name,
    #         symbol=order.symbol,
    #         image_url=order.image_url
    #     )

    #     db.add(db_post)
    #     db.commit()
    #     db.refresh(db_post)

    #     return db_post
    def get_order_by_id(self, id):
        order: Order = self.db.query(Order).with_for_update().filter(Order.id == id).first()
        return order

    def get_orders_by_id(self, id):
        order = self.db.query(Order, UserInventory, Entity).join(UserInventory, UserInventory.id == Order.entity_in_inventory_id).join(Entity, Entity.id == UserInventory.entity_id).filter(Order.entity_id == id).order_by(Order.price.asc()).all()
        return order

    def get_all_orders_by_lowest_price(self):
            lowest_price = func.min(Order.price)

            orders = (
                self.db.query(Entity, lowest_price)
                .join(Order, Order.entity_id == Entity.id)
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