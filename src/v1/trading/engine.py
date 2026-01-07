from order.schemas import OrderBuy
from order.models import Order, Side

from auth.schemas import UserResponse

from auth.models import User
from pydantic import BaseModel

class TradingEngine:

    def find_match(self, order: Order, db):
        if order.side == Side.BUY:
            return (
                db.query(Order)
                .with_for_update()
                .filter(
                    Order.side == Side.SELL,
                    Order.price <= order.price,
                    Order.entity_id == order.entity_id,
                    Order.user_id != order.user_id,
                )
                .first()
            )
        elif order.side == Side.SELL:
            return (
                      db.query(Order)
                      .with_for_update()
                      .filter(
                          Order.side == Side.BUY,
                          Order.price >= order.price,
                          Order.entity_id == order.entity_id,
                          Order.user_id != order.user_id,
                      )
                      .first()
                  )
        return None