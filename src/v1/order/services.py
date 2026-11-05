from auth.models import User
from auth.repository import AuthRepository
from auth.schemas import UserResponse
from entity.repository import EntityRepository
from fastapi import HTTPException
from inventory.models import UserInventory
from inventory.services import InventoryService
from order.models import Order, Side
from order.repository import OrderRepository
from order.schemas import OrderBuy, OrderCreate, OrderDelete, OrderResponse
from order.validation import _validate_order_input
from sqlalchemy import update
from trading.engine import TradingEngine
from uow import SQLiteUnitOfWork, UnitOfWork


class OrderService:
    def __init__(
        self,
        db,
        order_repository,
        user_repository,
        entity_repository,
        inventory_service,
    ):
        self.order_repository: OrderRepository = order_repository
        self.user_repository: AuthRepository = user_repository
        self.entity_repository: EntityRepository = entity_repository
        self.inventory_service: InventoryService = inventory_service
        self.db = db
        self.uow: UnitOfWork = SQLiteUnitOfWork(self.db)
        self.engine = TradingEngine(self)

    # ----------------------Public Methods----------------------------------
    def create_order(self, order: OrderCreate, user) -> OrderResponse:
        try:
            _validate_order_input(order)
            self.uow.begin()
            inventory = None

            if order.side == Side.SELL and order.entity_in_inventory_id != 0:
                inventory = self.inventory_service.get_inventory_item_locked(
                    order.entity_in_inventory_id, user.id
                )
                self.match_entity_to_item(order, inventory)
                db_post = self._create_sell_order(user, order, inventory)

            elif order.side == Side.BUY:
                self._ensure_no_existing_buy_order(user, order)
                self.entity_repository.get_entity_by_id(order.entity_id)
                db_post = self._create_buy_order(order, user)

            else:
                raise HTTPException(status_code=400, detail="Order not valid.")

            self.db.add(db_post)

            self.db.flush()
            self.engine.execute_match(self.db, db_post, user, in_transaction=True)

            self.uow.commit()
        except Exception:
            self.uow.rollback()
            raise

        return OrderResponse.model_validate(db_post)

    def order_buy(
        self, order_buy: OrderBuy, user, in_transaction, matched=False
    ) -> OrderResponse:

        try:
            if in_transaction == False:
                self.uow.begin()

            order_to_buy: Order = self._get_order_to_buy(order_buy, user)

            if order_to_buy.side == Side.BUY:
                raise HTTPException(status_code=404, detail="Can't buy this Order.")

            item_in_inventory = self.inventory_service.get_inventory_item_locked(
                order_to_buy.entity_in_inventory_id
            )

            self._execute_cash_transaction(order_to_buy, user)

            # Adding the Item to buyer inventory after a successful purchase
            # new_inventory_item = self.inventory_service.create_inventory_item(item_in_inventory, user)
            self.db.execute(
                update(UserInventory)
                .where(UserInventory.id == item_in_inventory.id)
                .values(user_id=user.id, in_sale=False)
            )
            self.db.flush()

            # Deleting the order from Marketplace, and sellers inventory
            self.order_repository.delete(order_to_buy)
            # self.order_repository.delete(item_in_inventory)

            # IF two orders matched, means there is also BUY order in Orders Table. So we should delete it.
            # So if user BUYS manually, we dont delete his BUY order too
            if matched:
                buy_request = self.order_repository.get_suitable_buy_order(
                    user.id, Side.BUY, item_in_inventory.entity_id
                )

                if buy_request:
                    self.db.delete(buy_request)

            # Committing the whole transaction
            if in_transaction == False:
                self.uow.commit()

            return OrderResponse.model_validate(order_to_buy)
        except Exception:
            if in_transaction == False:
                self.uow.rollback()
            raise

    def order_delete(self, order_delete: OrderDelete, user) -> OrderResponse:

        try:
            self.uow.begin()
            order_to_delete: Order = self.order_repository.get_order_by_id(
                order_delete.order_id
            )

            if not order_to_delete or order_to_delete.user_id != user.id:
                raise HTTPException(
                    status_code=404, detail="It seems you cant delete this order."
                )

            if order_to_delete.side == Side.SELL:
                item_in_inventory = self.inventory_service.get_inventory_item_locked(
                    order_to_delete.entity_in_inventory_id, user.id
                )
            elif order_to_delete.side == Side.BUY:
                item_in_inventory = None
            else:
                raise HTTPException(status_code=400, detail="Order not valid.")

            self.db.delete(order_to_delete)

            if item_in_inventory:
                item_in_inventory.in_sale = False
            self.uow.commit()

        except Exception:
            self.uow.rollback()
            raise

        return OrderResponse.model_validate(order_to_delete)

    # ----------------------Private Helpers----------------------------------

    def _create_sell_order(
        self,
        user: UserResponse,
        order: OrderCreate,
        inventory: UserInventory,
    ):

        if inventory.in_sale:
            raise HTTPException(status_code=404, detail="Item not found in inventory.")

        inventory.in_sale = True

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

    def _ensure_no_existing_buy_order(self, user, order):
        user_order = self.order_repository.get_user_order(
            order.entity_id, user.id, Side.BUY
        )
        if user_order:
            raise HTTPException(
                status_code=400,
                detail="You already have an order for this item",
            )

    def _execute_cash_transaction(self, order_to_buy, user):
        # Getting both user from SELF.DB
        seller_user: User = self.user_repository.get_user_by_id(order_to_buy.user_id)
        buyer_user: User = self.user_repository.get_user_by_id(user.id)
        if not seller_user or not buyer_user:
            raise HTTPException(status_code=404, detail="User not found.")
        total_cost = order_to_buy.price
        if total_cost > buyer_user.balance:
            raise HTTPException(status_code=400, detail="Not enough balance.")
        # Initiate balance transaction
        seller_user.balance += total_cost
        buyer_user.balance -= total_cost

        self.db.add(buyer_user)
        self.db.add(seller_user)

    def _get_order_to_buy(self, order_buy, user):
        order_to_buy: Order = self.order_repository.get_order_by_id(order_buy.order_id)

        if not order_to_buy:
            raise HTTPException(status_code=404, detail="Order not found.")
        if order_to_buy.user_id == user.id:
            raise HTTPException(
                status_code=403, detail="You cannot buy your own order."
            )

        return order_to_buy

    def match_entity_to_item(self, order: OrderCreate, inventory: UserInventory):

        if inventory.entity_id != order.entity_id:
            raise HTTPException(
                status_code=404, detail="Item from inventory and entity did not match."
            )
        return True
