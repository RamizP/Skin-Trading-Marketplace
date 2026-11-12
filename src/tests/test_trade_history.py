from decimal import Decimal
from types import SimpleNamespace

import pytest
from case.models import CaseDrop
from entity.models import Category
from fastapi import HTTPException
from inventory.models import EntityWear, UserInventory
from order.models import Order
from order.services import OrderService
from trading.models import TradeHistory
from trading.schemas import TradeHistoryResponse


@pytest.fixture
def history_market(user_factory, entity_factory, inventory_factory, auth_headers):
    seller = user_factory(balance="0.00")
    buyer = user_factory(balance="50.00")
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


def place_order(client, market, side):
    payload = {
        "entity_id": market.entity.id,
        "side": side,
        "price": "10.00" if side == "sell" else "12.00",
    }
    if side == "sell":
        payload["entity_in_inventory_id"] = market.item.id
    headers = market.seller_headers if side == "sell" else market.buyer_headers
    response = client.post("/orders", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["id"]


def assert_trade(db, market):
    history = db.query(TradeHistory).one()
    assert history.seller_id == market.seller.id
    assert history.buyer_id == market.buyer.id
    assert history.entity_id == market.entity.id
    assert history.item_id == market.item.id
    assert history.entity_wear == EntityWear.MINIMAL_WEAR
    assert history.price == Decimal("10.00")
    assert history.created_at is not None
    return history


def test_direct_purchase_records_history_once(client, db_session, history_market):
    order_id = place_order(client, history_market, "sell")
    response = client.post(
        "/order/buy", json={"order_id": order_id}, headers=history_market.buyer_headers
    )
    assert response.status_code == 200, response.text
    history = assert_trade(db_session, history_market)
    assert db_session.query(Order).count() == 0
    parsed = TradeHistoryResponse.model_validate(history)
    assert parsed.price == Decimal("10.00")

    response = client.post(
        "/order/buy", json={"order_id": order_id}, headers=history_market.buyer_headers
    )
    assert response.status_code == 404
    assert db_session.query(TradeHistory).count() == 1


@pytest.mark.parametrize("first_side", ["buy", "sell"])
def test_automatic_match_records_actual_price(
    client, db_session, history_market, first_side
):
    place_order(client, history_market, first_side)
    place_order(client, history_market, "sell" if first_side == "buy" else "buy")
    assert_trade(db_session, history_market)
    db_session.refresh(history_market.item)
    assert history_market.item.user_id == history_market.buyer.id
    assert db_session.query(Order).count() == 0


def test_skipped_unfunded_bid_does_not_create_history(
    client, db_session, history_market, user_factory, auth_headers
):
    poor_buyer = user_factory(balance="0.50")
    response = client.post(
        "/orders",
        json={"entity_id": history_market.entity.id, "side": "buy", "price": "100.00"},
        headers=auth_headers(poor_buyer),
    )
    assert response.status_code == 200
    place_order(client, history_market, "buy")
    place_order(client, history_market, "sell")
    assert_trade(db_session, history_market)
    assert db_session.query(Order).count() == 0
    db_session.refresh(poor_buyer)
    assert poor_buyer.balance == Decimal("0.50")


@pytest.mark.parametrize(
    "mode", ["direct", "incoming_buy", "incoming_sell", "skip_unfunded"]
)
def test_history_failure_rolls_back_the_whole_trade(
    client, db_session, history_market, monkeypatch, user_factory, auth_headers, mode
):
    first_side = "buy" if mode in {"incoming_sell", "skip_unfunded"} else "sell"
    initial_id = place_order(client, history_market, first_side)
    expected_ids = {initial_id}
    if mode == "skip_unfunded":
        poor = user_factory(balance="0.50")
        response = client.post(
            "/orders",
            json={
                "entity_id": history_market.entity.id,
                "side": "buy",
                "price": "100.00",
            },
            headers=auth_headers(poor),
        )
        assert response.status_code == 200
        expected_ids.add(response.json()["id"])

    original = OrderService.fill_history

    def record_then_fail(service, trade):
        original(service, trade)
        raise HTTPException(status_code=503, detail="History write failed")

    monkeypatch.setattr(OrderService, "fill_history", record_then_fail)
    if mode == "direct":
        response = client.post(
            "/order/buy",
            json={"order_id": initial_id},
            headers=history_market.buyer_headers,
        )
    else:
        side = "sell" if first_side == "buy" else "buy"
        payload = {
            "entity_id": history_market.entity.id,
            "side": side,
            "price": "10.00",
        }
        if side == "sell":
            payload["entity_in_inventory_id"] = history_market.item.id
        response = client.post(
            "/orders",
            json=payload,
            headers=history_market.seller_headers
            if side == "sell"
            else history_market.buyer_headers,
        )
    assert response.status_code == 503, response.text
    assert db_session.query(TradeHistory).count() == 0
    assert {order.id for order in db_session.query(Order)} == expected_ids
    db_session.refresh(history_market.seller)
    db_session.refresh(history_market.buyer)
    db_session.refresh(history_market.item)
    assert history_market.seller.balance == Decimal("0.00")
    assert history_market.buyer.balance == Decimal("50.00")
    assert history_market.item.user_id == history_market.seller.id
    assert history_market.item.in_sale is (first_side == "sell")
    assert db_session.query(UserInventory).count() == 1


def test_opening_a_traded_case_preserves_history(
    client, db_session, history_market, entity_factory
):
    category = Category(name="case")
    db_session.add(category)
    db_session.flush()
    history_market.entity.category_id = category.id
    history_market.item.entity_wear = EntityWear.NONE
    db_session.commit()
    reward = entity_factory()
    db_session.add(
        CaseDrop(
            case_entity_id=history_market.entity.id,
            reward_entity_id=reward.id,
            weight=1,
        )
    )
    db_session.commit()
    order_id = place_order(client, history_market, "sell")
    response = client.post(
        "/order/buy", json={"order_id": order_id}, headers=history_market.buyer_headers
    )
    assert response.status_code == 200
    history = db_session.query(TradeHistory).one()
    case_id = history.item_id
    response = client.post(
        f"/cases/{case_id}/open", headers=history_market.buyer_headers
    )
    assert response.status_code == 200, response.text
    assert response.json()["entity_id"] == reward.id
    db_session.refresh(history)
    assert history.item_id is None
    assert history.entity_id == history_market.entity.id
    assert history.entity_wear == EntityWear.NONE
    assert history.price == Decimal("10.00")
    assert history.seller_id == history_market.seller.id
    assert history.buyer_id == history_market.buyer.id
    assert TradeHistoryResponse.model_validate(history).item_id is None
    assert db_session.query(UserInventory).filter_by(id=case_id).count() == 0
    assert db_session.query(TradeHistory).count() == 1
