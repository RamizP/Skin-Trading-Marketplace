import pytest
from pydantic import ValidationError

from order.models import Side
from order.schemas import OrderCreate


def test_sell_order_requires_inventory_item():
    with pytest.raises(
        ValidationError,
        match="Sell orders require an inventory item",
    ):
        OrderCreate(
            entity_id=1,
            price="10.00",
            side=Side.SELL,
        )

def test_buy_order_with_entity_in_inventory_id():
    with pytest.raises(
        ValidationError,
        match="Buy orders cannot reference an inventory item.",
    ):
        OrderCreate(
            entity_id=1,
            price="10.00",
            side=Side.BUY,
            entity_in_inventory_id=10,
        )

def test_with_zero_price():
    with pytest.raises(
        ValidationError,
        match="Input should be greater than 0",
    ):
        OrderCreate(
            entity_id=1,
            price="00.00",
            side=Side.BUY,
            entity_in_inventory_id=10,
        )

def test_with_negative_price():
    with pytest.raises(
        ValidationError,
        match="Input should be greater than 0",
    ):
        OrderCreate(
            entity_id=1,
            price="-1",
            side=Side.BUY,
            entity_in_inventory_id=10,
        )

def test_valid_buy_order():
    order = OrderCreate(
        entity_id=1,
        price="10.00",
        side=Side.BUY,
    )

    assert order.entity_id == 1
    assert order.entity_in_inventory_id is None
    assert order.price == 10
    assert order.side == Side.BUY

def test_valid_sell_order():
    order = OrderCreate(
        entity_id=1,
        entity_in_inventory_id=10,
        price="10.00",
        side=Side.SELL,
    )

    assert order.entity_id == 1
    assert order.entity_in_inventory_id == 10
    assert order.price == 10
    assert order.side == Side.SELL