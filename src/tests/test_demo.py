from collections import Counter, defaultdict
from decimal import Decimal

import bcrypt
import demo
import pytest
from auth.models import User, UserRole
from case.models import CaseDrop
from demo import DemoInitialization, initialize_demo_data
from entity.models import Category, Entity
from fastapi.testclient import TestClient
from inventory.models import EntityWear, UserInventory
from order.models import Order, Side
from sqlalchemy.orm import sessionmaker

from src.v1 import main


def test_demo_initialization_populates_a_fresh_database(db_session):
    assert initialize_demo_data(db_session)
    assert db_session.query(User).count() == 11
    assert db_session.query(Entity).count() == 35
    assert db_session.query(UserInventory).count() == 178
    assert db_session.query(Order).filter(Order.side == Side.SELL).count() == 70
    assert db_session.query(Order).filter(Order.side == Side.BUY).count() == 70
    assert db_session.query(CaseDrop).count() == 24
    assert db_session.query(DemoInitialization).count() == 1

    guest = db_session.query(User).filter_by(username="guest").one()
    assert guest.balance == Decimal("1000.00")
    assert guest.role == UserRole.user
    assert bcrypt.checkpw(b"GuestDemo123!", guest.password_hashed.encode())
    case_category = db_session.query(Category).filter_by(name="case").one()
    cases = db_session.query(Entity).filter_by(category_id=case_category.id).all()
    assert len(cases) == 5
    case_ids = {case.id for case in cases}
    assert all(
        item.entity_wear == EntityWear.NONE
        for item in db_session.query(UserInventory).filter(
            UserInventory.entity_id.in_(case_ids)
        )
    )
    guest_items = db_session.query(UserInventory).filter_by(user_id=guest.id).all()
    assert len(guest_items) == 8
    assert sum(item.entity_id in case_ids for item in guest_items) == 3
    assert all(not item.in_sale for item in guest_items)
    assert db_session.query(Order).filter_by(user_id=guest.id).count() == 0

    collections = Counter(
        item.user_id
        for item in db_session.query(UserInventory)
        if not item.in_sale and item.entity_id not in case_ids
    )
    traders = db_session.query(User).filter(User.username.like("demo_%")).all()
    assert len(traders) == 10
    assert {collections[trader.id] for trader in traders} == {6, 7, 8, 9, 10}

    drops_by_case = defaultdict(list)
    for drop in db_session.query(CaseDrop):
        drops_by_case[drop.case_entity_id].append(drop)
        assert drop.reward_entity_id not in case_ids
        assert drop.weight > 0
    assert set(drops_by_case) == case_ids
    assert all(
        sum(drop.weight for drop in drops) == 100 for drops in drops_by_case.values()
    )


def test_demo_order_book_has_distinct_owners_and_no_crossed_orders(db_session):
    initialize_demo_data(db_session)
    orders_by_entity = defaultdict(list)
    bids_by_user = defaultdict(lambda: Decimal("0.00"))
    inventory = {item.id: item for item in db_session.query(UserInventory)}
    listed_items = []
    sellers = set()
    buyers = set()
    for order in db_session.query(Order):
        orders_by_entity[order.entity_id].append(order)
        if order.side == Side.SELL:
            item = inventory[order.entity_in_inventory_id]
            assert item.in_sale
            assert item.user_id == order.user_id
            assert item.entity_id == order.entity_id
            listed_items.append(item.id)
            sellers.add(order.user_id)
        else:
            assert order.entity_in_inventory_id is None
            bids_by_user[order.user_id] += order.price
            buyers.add(order.user_id)

    assert len(orders_by_entity) == 35
    assert len(sellers) == len(buyers) == 10
    assert len(listed_items) == len(set(listed_items))
    assert set(listed_items) == {item.id for item in inventory.values() if item.in_sale}
    for orders in orders_by_entity.values():
        asks = [order for order in orders if order.side == Side.SELL]
        bids = [order for order in orders if order.side == Side.BUY]
        assert len(asks) == len(bids) == 2
        assert len({order.user_id for order in asks}) == 2
        assert len({order.user_id for order in bids}) == 2
        assert max(order.price for order in bids) < min(order.price for order in asks)
    for user in db_session.query(User):
        assert bids_by_user[user.id] <= user.balance


def test_demo_initialization_does_not_restore_orders_or_balances(db_session):
    initialize_demo_data(db_session)
    db_session.query(Order).delete()
    db_session.query(User).filter_by(username="guest").update(
        {"balance": Decimal("1.00")}
    )
    db_session.commit()

    assert not initialize_demo_data(db_session)
    assert db_session.query(Order).count() == 0
    assert db_session.query(User).filter_by(username="guest").one().balance == Decimal(
        "1.00"
    )
    assert db_session.query(UserInventory).count() == 178


def test_demo_marker_prevents_reseeding_even_after_data_is_removed(db_session):
    initialize_demo_data(db_session)
    for model in (Order, UserInventory, CaseDrop, Entity, Category, User):
        db_session.query(model).delete()
    db_session.commit()

    assert not initialize_demo_data(db_session)
    assert db_session.query(User).count() == 0
    assert db_session.query(Entity).count() == 0
    assert db_session.query(DemoInitialization).count() == 1


def test_demo_initialization_preserves_an_existing_database(db_session):
    db_session.add(Category(name="My category"))
    db_session.commit()

    assert not initialize_demo_data(db_session)
    assert [category.name for category in db_session.query(Category)] == ["My category"]
    assert db_session.query(User).count() == 0
    assert db_session.query(Entity).count() == 0
    assert db_session.query(DemoInitialization).count() == 0


def test_failed_demo_initialization_rolls_back_and_can_retry(db_session, monkeypatch):
    original = demo._add_demo_data

    def fail_after_inserts(db):
        original(db)
        db.flush()
        raise RuntimeError("Initialization failed")

    monkeypatch.setattr(demo, "_add_demo_data", fail_after_inserts)
    with pytest.raises(RuntimeError, match="Initialization failed"):
        initialize_demo_data(db_session)
    for model in (User, Entity, Order, UserInventory, CaseDrop, DemoInitialization):
        assert db_session.query(model).count() == 0

    db_session.rollback()
    monkeypatch.setattr(demo, "_add_demo_data", original)
    assert initialize_demo_data(db_session)


def test_first_startup_provides_a_working_demo_and_preserves_trades(
    db_session, monkeypatch
):
    # Remove the test opt-out: automatic demo data must be the default.
    monkeypatch.delenv("DEMO_DATA")
    monkeypatch.setattr(main, "SessionLocal", sessionmaker(bind=db_session.get_bind()))

    with TestClient(main.app) as client:
        assert len(client.get("/entities", params={"limit": 100}).json()) == 35
        assert len(client.get("/orders").json()) == 35
        response = client.post(
            "/login", json={"username": "guest", "password": "GuestDemo123!"}
        )
        assert response.status_code == 200
        headers = {"Authentication": response.json()["token"]}
        items = client.get("/inventory/me", headers=headers).json()
        assert len(items) == 8
        case = next(
            item for item in items if item["entity"]["name"] == "After Hours Case"
        )
        assert (
            client.post(f"/cases/{case['id']}/open", headers=headers).status_code == 200
        )

        asiimov = next(
            item for item in client.get("/entities").json() if item["name"] == "Asiimov"
        )
        listing = client.get(f"/orders/{asiimov['id']}").json()[0]
        assert (
            client.post(
                "/order/buy", json={"order_id": listing["id"]}, headers=headers
            ).status_code
            == 200
        )
        assert client.get("/user/me", headers=headers).json()["balance"] == "989.50"
        assert len(client.get(f"/orders/{asiimov['id']}").json()) == 1

        black_lotus = next(
            item for item in items if item["entity"]["name"] == "Black Lotus"
        )
        bid = client.get(f"/buy-orders/{black_lotus['entity_id']}/highest").json()
        response = client.post(
            "/orders",
            json={
                "entity_id": black_lotus["entity_id"],
                "entity_in_inventory_id": black_lotus["id"],
                "price": bid["price"],
                "side": "sell",
            },
            headers=headers,
        )
        assert response.status_code == 200
        balance = Decimal("989.50") + Decimal(bid["price"])
        assert (
            Decimal(client.get("/user/me", headers=headers).json()["balance"])
            == balance
        )
        assert client.post("/cases/free", headers=headers).status_code == 200

    with TestClient(main.app) as client:
        assert (
            Decimal(client.get("/user/me", headers=headers).json()["balance"])
            == balance
        )
        assert len(client.get("/inventory/me", headers=headers).json()) == 9
        assert len(client.get(f"/orders/{asiimov['id']}").json()) == 1


def test_automatic_demo_data_can_be_disabled(db_session, monkeypatch):
    monkeypatch.setenv("DEMO_DATA", "false")

    def unexpected_initialization(db):
        raise AssertionError("Demo initialization should not run")

    monkeypatch.setattr(main, "initialize_demo_data", unexpected_initialization)
    with TestClient(main.app) as client:
        assert client.get("/entities").json() == []
    assert db_session.query(DemoInitialization).count() == 0
