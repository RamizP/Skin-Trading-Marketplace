from fastapi import HTTPException
from order.models import Side

# def _validate_inventory_for_sell(inventory):
#     if not inventory:
#         raise HTTPException(status_code=400, detail="Inventory item not found.")
#     if inventory.in_sale:
#         raise HTTPException(status_code=400, detail="Item is already in sale.")


def _validate_order_input(order):
    if order.price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than 0.")
    if order.side not in (Side.BUY, Side.SELL):
        raise HTTPException(status_code=400, detail="Invalid order side.")


# def _validate_buy_order(order_to_buy, buyer):
#         if order_to_buy.user_id == buyer.id:
#             raise HTTPException(status_code=403, detail="Cannot buy your own order.")
#         buyer_user = self.db.query(User).filter(User.id == buyer.id).first()
#         if order_to_buy.price > buyer_user.balance:
#             raise HTTPException(status_code=400, detail="Insufficient balance.")
