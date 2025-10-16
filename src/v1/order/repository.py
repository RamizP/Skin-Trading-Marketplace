from order.schemas import OrderResponse, OrderCreate
from order.models import Base, Order
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from order.models import Base, Order

class OrderRepository:
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
    def get_order_by_id(db, id):
        order: Order = db.query(Order).with_for_update().filter(Order.id == id).order_by(Order.price.asc()).first()

        return order
