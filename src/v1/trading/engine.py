from order.schemas import OrderBuy
from order.models import Order, Side

from auth.schemas import UserResponse

from auth.models import User
from pydantic import BaseModel

class TradingEngine:

    def __init__(self, order_service):
        self.order_service = order_service

    def match_buy_request(self, buy_request: OrderBuy, user, db):
        order = (
                    db.query(Order)
                    .with_for_update()
                    .filter(
                        Order.id == buy_request.order_id
                    )
                    .first()
                )

        if order.side == Side.BUY:
            matching_order = (
                        db.query(Order)
                        .with_for_update()
                        .filter(
                            Order.side == Side.SELL,
                            Order.price <= order.price,
                            Order.entity_id == order.entity_id,
                            Order.user_id != user.id,
                        )
                        .first()
                    )
            if matching_order:
                order_buy = OrderBuy(order_id=matching_order.id)
                self.order_service.order_buy(order_buy, db, user)

        if order.side == Side.SELL:
            matching_order = (
                      db.query(Order)
                      .with_for_update()
                      .filter(
                          Order.side == Side.BUY,
                          Order.price >= order.price,
                          Order.entity_id == order.entity_id,
                          Order.user_id != user.id,
                      )
                      .first()
                  )

            if matching_order:
                buyer_user = (
                          db.query(User)
                          .filter(
                              User.id == matching_order.user_id
                          )
                          .first()
                        )
            else:
                return None

            if buyer_user:
                buyer_serialized = UserResponse.model_validate(buyer_user)
                order_buy = OrderBuy(order_id=order.id)
                self.order_service.order_buy(order_buy, db, buyer_serialized)