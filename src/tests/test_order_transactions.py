from decimal import Decimal
from types import SimpleNamespace

import pytest
from inventory.models import EntityWear, UserInventory
from order.models import Order


@pytest.fixture
def market(user_factory, entity_factory, inventory_factory, auth_headers):
    seller = user_factory(balance="0.00")
    buyer = user_factory(balance="20.00")
    entity = entity_factory()
    item = inventory_factory(seller, entity, wear=EntityWear.MINIMAL_WEAR)
    return SimpleNamespace(
        seller=seller,
        buyer=buyer,
        entity=entity,
        item=item,
        seller_headers=auth_headers(seller),
        buyer_headers=auth_headers(buyer),
    )


def create_order(client, market, side):
    payload = {
        "entity_id": market.entity.id,
        "price": "10.00" if side == "sell" else "12.00",
        "side": side,
    }
    if side == "sell":
        payload["entity_in_inventory_id"] = market.item.id
    headers = market.seller_headers if side == "sell" else market.buyer_headers
    response = client.post("/orders", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_insufficient_balance_preserves_listing_and_balances(
    client, db_session, market
):
    market.buyer.balance = Decimal("5.00")
    db_session.commit()
    order_id = create_order(client, market, "sell")

    response = client.post(
        "/order/buy", json={"order_id": order_id}, headers=market.buyer_headers
    )

    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "Not enough balance."
    db_session.refresh(market.seller)
    db_session.refresh(market.buyer)
    db_session.refresh(market.item)
    assert market.seller.balance == Decimal("0.00")
    assert market.buyer.balance == Decimal("5.00")
    assert market.item.user_id == market.seller.id
    assert market.item.in_sale is True
    order = db_session.query(Order).filter(Order.id == order_id).one()
    assert order.user_id == market.seller.id
    assert order.entity_in_inventory_id == market.item.id
    assert order.price == Decimal("10.00")
    assert db_session.query(Order).count() == 1
    assert db_session.query(UserInventory).count() == 1


def test_user_cannot_buy_their_own_listing(client, db_session, market):
    # Enough balance ensures rejection is about ownership, not lack of funds.
    market.seller.balance = Decimal("20.00")
    db_session.commit()
    order_id = create_order(client, market, "sell")

    response = client.post(
        "/order/buy", json={"order_id": order_id}, headers=market.seller_headers
    )

    assert response.status_code == 403, response.text
    assert response.json()["detail"] == "You cannot buy your own order."
    db_session.refresh(market.seller)
    db_session.refresh(market.item)
    assert market.seller.balance == Decimal("20.00")
    assert market.item.user_id == market.seller.id
    assert market.item.in_sale is True
    assert db_session.query(Order).filter(Order.id == order_id).count() == 1
    assert db_session.query(Order).count() == 1


def test_buying_completed_order_again_does_not_charge_twice(client, db_session, market):
    order_id = create_order(client, market, "sell")
    payload = {"order_id": order_id}
    purchase = client.post("/order/buy", json=payload, headers=market.buyer_headers)
    assert purchase.status_code == 200, purchase.text

    response = client.post("/order/buy", json=payload, headers=market.buyer_headers)

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Order not found."
    db_session.refresh(market.seller)
    db_session.refresh(market.buyer)
    db_session.refresh(market.item)
    assert market.seller.balance == Decimal("10.00")
    assert market.buyer.balance == Decimal("10.00")
    assert market.item.user_id == market.buyer.id
    assert market.item.in_sale is False
    assert db_session.query(Order).count() == 0
    assert db_session.query(UserInventory).count() == 1


@pytest.mark.parametrize("first_side", ["sell", "buy"])
def test_matching_orders_trade_automatically(client, db_session, market, first_side):
    # A 12.00 buy offer crosses a 10.00 sell listing
    first_order_id = create_order(client, market, first_side)
    assert db_session.query(Order).filter(Order.id == first_order_id).count() == 1

    second_side = "buy" if first_side == "sell" else "sell"
    create_order(client, market, second_side)

    db_session.refresh(market.seller)
    db_session.refresh(market.buyer)
    db_session.refresh(market.item)
    assert market.seller.balance == Decimal("10.00")
    assert market.buyer.balance == Decimal("10.00")
    assert market.item.user_id == market.buyer.id
    assert market.item.in_sale is False
    assert market.item.entity_wear == EntityWear.MINIMAL_WEAR
    assert db_session.query(Order).count() == 0
    assert db_session.query(UserInventory).count() == 1


@pytest.mark.parametrize("first_side", ["sell", "buy"])
def test_unfunded_automatic_match_leaves_a_sell_listing(
    client, db_session, market, first_side
):
    market.buyer.balance = Decimal("5.00")
    db_session.commit()
    first_order_id = create_order(client, market, first_side)

    second_side = "buy" if first_side == "sell" else "sell"
    payload = {
        "entity_id": market.entity.id,
        "price": "10.00" if second_side == "sell" else "12.00",
        "side": second_side,
    }
    if second_side == "sell":
        payload["entity_in_inventory_id"] = market.item.id
    headers = market.seller_headers if second_side == "sell" else market.buyer_headers

    response = client.post("/orders", json=payload, headers=headers)

    if first_side == "sell":
        assert response.status_code == 400, response.text
        assert response.json()["detail"] == "Not enough balance."
        listing_id = first_order_id
    else:
        assert response.status_code == 200, response.text
        listing_id = response.json()["id"]
        assert db_session.get(Order, first_order_id) is None
    db_session.refresh(market.seller)
    db_session.refresh(market.buyer)
    db_session.refresh(market.item)
    assert market.seller.balance == Decimal("0.00")
    assert market.buyer.balance == Decimal("5.00")
    assert market.item.user_id == market.seller.id
    assert market.item.in_sale is True
    orders = db_session.query(Order).all()
    assert len(orders) == 1
    assert orders[0].id == listing_id
    assert orders[0].side.value == "sell"
    assert db_session.query(UserInventory).count() == 1


@pytest.mark.parametrize("action", ["create", "buy", "cancel"])
def test_order_mutations_require_authentication(client, db_session, market, action):
    order_id = create_order(client, market, "sell")
    client.cookies.clear()

    if action == "create":
        response = client.post(
            "/orders",
            json={"entity_id": market.entity.id, "price": "10.00", "side": "buy"},
        )
    elif action == "buy":
        response = client.post("/order/buy", json={"order_id": order_id})
    else:
        response = client.request("DELETE", "/order", json={"order_id": order_id})

    assert response.status_code == 401, response.text
    db_session.refresh(market.seller)
    db_session.refresh(market.buyer)
    db_session.refresh(market.item)
    assert market.seller.balance == Decimal("0.00")
    assert market.buyer.balance == Decimal("20.00")
    assert market.item.user_id == market.seller.id
    assert market.item.in_sale is True
    assert db_session.query(Order).filter(Order.id == order_id).count() == 1
    assert db_session.query(Order).count() == 1
