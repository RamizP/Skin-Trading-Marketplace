from trading.models import TradeHistory
from trading.schemas import TradePricePoint


class TradingService:
    def get_entity_history(self, entity_id, db):
        entity_history: list[TradeHistory] = (
            db.query(TradeHistory)
            .filter(TradeHistory.entity_id == entity_id)
            .order_by(TradeHistory.created_at.asc(), TradeHistory.id)
            .all()
        )

        if not entity_history:
            return []
        return [TradePricePoint.model_validate(history) for history in entity_history]
