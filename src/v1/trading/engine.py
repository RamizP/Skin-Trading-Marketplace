from order.schemas import OrderBuy
from order.models import Order, Side

from auth.models import User

class TradingEngine:

    def __init__(self, order_service):
        self.order_service = order_service

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

    def execute_match(self, db, order, user, in_transaction):
        # buy_request = OrderBuy(order_id=db_post.id)
        # self.engine.match_buy_request(buy_request, user, self.db)
        matching_order: Order = self.find_match(order, db)
        if not matching_order:
            return

        if matching_order.side == Side.SELL:
            order_buy = OrderBuy(order_id=matching_order.id)
            self.order_service.order_buy(order_buy, user, in_transaction, matched=True)
        elif matching_order.side == Side.BUY:
            order_buy = OrderBuy(order_id=order.id)
            buyer_user = (
                db.query(User)
                .filter(
                    User.id == matching_order.user_id
                )
                .first()
            )
            self.order_service.order_buy(order_buy, buyer_user, in_transaction, matched=True)