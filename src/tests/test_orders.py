from uuid import uuid4

import bcrypt
from auth.models import User
from entity.models import Entity, EntityRarity
from order.models import Order, Side
from decimal import Decimal

from inventory.models import EntityWear, UserInventory


def test_user_can_create_buy_order(client, db_session):
    unique_id = uuid4().hex
    password = "Password123!"

    user = User(
        username=f"buyer_{unique_id}",
        email=f"{unique_id}@example.com",
        password_hashed=bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8"),
    )
    entity = Entity(
        name=f"Test item {unique_id}",
        symbol=f"ITEM_{unique_id[:8]}",
        entity_rarity=EntityRarity.COMMON,
    )

    db_session.add_all([user, entity])
    db_session.commit()
    db_session.refresh(entity)

    login_response = client.post(
        "/login",
        json={
            "username": user.username,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["token"]

    response = client.post(
        "/orders",
        json={
            "entity_id": entity.id,
            "price": "10.00",
            "side": "buy",
        },
        headers={"Authentication": token},
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == user.id
    assert response.json()["entity_id"] == entity.id
    assert response.json()["price"] == "10.00"
    assert response.json()["side"] == "buy"

    saved_order = db_session.get(Order, response.json()["id"])
    assert saved_order is not None
    assert saved_order.user_id == user.id
    assert saved_order.entity_id == entity.id
    assert saved_order.price == Decimal("10.00")
    assert saved_order.side == Side.BUY
    assert saved_order.entity_in_inventory_id is None


def test_user_can_create_sell_order(client, db_session):
    unique_id = uuid4().hex
    password = "Password123!"

    user = User(
        username=f"buyer_{unique_id}",
        email=f"{unique_id}@example.com",
        password_hashed=bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8"),
    )
    entity = Entity(
        name=f"Test item {unique_id}",
        symbol=f"ITEM_{unique_id[:8]}",
        entity_rarity=EntityRarity.COMMON,
    )

    db_session.add_all([user, entity])
    db_session.commit()
    db_session.refresh(entity)

    inventory_item = UserInventory(
        user_id=user.id,
        entity_id=entity.id,
        entity_wear=EntityWear.NONE,
    )

    db_session.add(inventory_item)
    db_session.commit()
    db_session.refresh(inventory_item)

    login_response = client.post(
        "/login",
        json={
            "username": user.username,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["token"]

    response = client.post(
        "/orders",
        json={
            "entity_id": entity.id,
            "entity_in_inventory_id": inventory_item.id,
            "price": "10.00",
            "side": "sell",
        },
        headers={"Authentication": token},
    )
    db_session.refresh(inventory_item)

    assert response.status_code == 200, response.text
    assert inventory_item.in_sale is True
    assert inventory_item.user_id == user.id

    saved_order = db_session.get(Order, response.json()["id"])

    assert saved_order is not None
    assert saved_order.user_id == user.id
    assert saved_order.entity_id == entity.id
    assert saved_order.price == Decimal("10.00")
    assert saved_order.side == Side.SELL
    assert saved_order.entity_in_inventory_id == inventory_item.id

def test_user_cant_create_same_sell_order(client, db_session):
    unique_id = uuid4().hex
    password = "Password123!"

    user = User(
        username=f"buyer_{unique_id}",
        email=f"{unique_id}@example.com",
        password_hashed=bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8"),
    )
    entity = Entity(
        name=f"Test item {unique_id}",
        symbol=f"ITEM_{unique_id[:8]}",
        entity_rarity=EntityRarity.COMMON,
    )

    db_session.add_all([user, entity])
    db_session.commit()
    db_session.refresh(entity)

    inventory_item = UserInventory(
        user_id=user.id,
        entity_id=entity.id,
        entity_wear=EntityWear.NONE,
    )

    db_session.add(inventory_item)
    db_session.commit()
    db_session.refresh(inventory_item)

    login_response = client.post(
        "/login",
        json={
            "username": user.username,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["token"]

    response = client.post(
        "/orders",
        json={
            "entity_id": entity.id,
            "entity_in_inventory_id": inventory_item.id,
            "price": "10.00",
            "side": "sell",
        },
        headers={"Authentication": token},
    )

    response_second = client.post(
        "/orders",
        json={
            "entity_id": entity.id,
            "entity_in_inventory_id": inventory_item.id,
            "price": "10.00",
            "side": "sell",
        },
        headers={"Authentication": token},
    )
    db_session.refresh(inventory_item)

    assert response.status_code == 200, response.text
    assert response_second.status_code == 404
    assert inventory_item.in_sale is True
    assert inventory_item.user_id == user.id

    assert db_session.query(Order).count() == 1

    saved_order = db_session.get(Order, response.json()["id"])

    assert saved_order is not None
    assert saved_order.user_id == user.id
    assert saved_order.entity_id == entity.id
    assert saved_order.price == Decimal("10.00")
    assert saved_order.side == Side.SELL
    assert saved_order.entity_in_inventory_id == inventory_item.id

def test_user_can_cancel_sell_order(client, db_session):
    unique_id = uuid4().hex
    password = "Password123!"

    user = User(
        username=f"buyer_{unique_id}",
        email=f"{unique_id}@example.com",
        password_hashed=bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8"),
    )
    entity = Entity(
        name=f"Test item {unique_id}",
        symbol=f"ITEM_{unique_id[:8]}",
        entity_rarity=EntityRarity.COMMON,
    )

    db_session.add_all([user, entity])
    db_session.commit()
    db_session.refresh(entity)

    inventory_item = UserInventory(
        user_id=user.id,
        entity_id=entity.id,
        entity_wear=EntityWear.NONE,
    )

    db_session.add(inventory_item)
    db_session.commit()
    db_session.refresh(inventory_item)

    login_response = client.post(
        "/login",
        json={
            "username": user.username,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["token"]

    order_response = client.post(
        "/orders",
        json={
            "entity_id": entity.id,
            "entity_in_inventory_id": inventory_item.id,
            "price": "10.00",
            "side": "sell",
        },
        headers={"Authentication": token},
    )
    db_session.refresh(inventory_item)

    assert order_response.status_code == 200, order_response.text
    assert inventory_item.in_sale is True
    assert inventory_item.user_id == user.id

    saved_order = db_session.get(Order, order_response.json()["id"])

    assert saved_order is not None
    assert saved_order.user_id == user.id
    assert saved_order.entity_id == entity.id
    assert saved_order.price == Decimal("10.00")
    assert saved_order.side == Side.SELL
    assert saved_order.entity_in_inventory_id == inventory_item.id

    response = client.request(
        "DELETE",
        "/order",
        json={"order_id": saved_order.id},
        headers={"Authentication": token},
    )
    assert response.status_code == 200

    db_session.refresh(inventory_item)
    deleted_order = db_session.query(Order).filter(Order.id == saved_order.id).first()

    assert deleted_order is None
    assert inventory_item.in_sale is False
    assert inventory_item.user_id == user.id

def test_user_cant_cancel_someone_else_sell_order(client, db_session):
    unique_id = uuid4().hex
    password = "Password123!"

    user = User(
        username=f"buyer_{unique_id}",
        email=f"{unique_id}@example.com",
        password_hashed=bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8"),
    )

    second_user = User(
        username=f"second_buyer_{unique_id}",
        email=f"second{unique_id}@example.com",
        password_hashed=bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8"),
    )

    entity = Entity(
        name=f"Test item {unique_id}",
        symbol=f"ITEM_{unique_id[:8]}",
        entity_rarity=EntityRarity.COMMON,
    )

    db_session.add_all([user, second_user, entity])
    db_session.commit()
    db_session.refresh(entity)

    inventory_item = UserInventory(
        user_id=user.id,
        entity_id=entity.id,
        entity_wear=EntityWear.NONE,
    )

    db_session.add(inventory_item)
    db_session.commit()
    db_session.refresh(inventory_item)

    login_response = client.post(
        "/login",
        json={
            "username": user.username,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["token"]

    order_response = client.post(
        "/orders",
        json={
            "entity_id": entity.id,
            "entity_in_inventory_id": inventory_item.id,
            "price": "10.00",
            "side": "sell",
        },
        headers={"Authentication": token},
    )
    db_session.refresh(inventory_item)

    assert order_response.status_code == 200, order_response.text
    assert inventory_item.in_sale is True
    assert inventory_item.user_id == user.id

    saved_order = db_session.get(Order, order_response.json()["id"])

    assert saved_order is not None
    assert saved_order.user_id == user.id
    assert saved_order.entity_id == entity.id
    assert saved_order.price == Decimal("10.00")
    assert saved_order.side == Side.SELL
    assert saved_order.entity_in_inventory_id == inventory_item.id

    login_response = client.post(
        "/login",
        json={
            "username": second_user.username,
            "password": password,
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["token"]

    response = client.request(
        "DELETE",
        "/order",
        json={"order_id": saved_order.id},
        headers={"Authentication": token},
    )
    assert response.status_code == 403

    db_session.refresh(inventory_item)
    remaining_order = db_session.query(Order).filter(Order.id == saved_order.id).first()

    assert remaining_order is not None
    assert inventory_item.in_sale is True
    assert inventory_item.user_id == user.id

def test_user_cannot_sell_someone_elses_item(client, db_session):
    unique_id = uuid4().hex
    password = "Password123!"

    user = User(
        username=f"buyer_{unique_id}",
        email=f"{unique_id}@example.com",
        password_hashed=bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8"),
    )

    second_user = User(
        username=f"second_buyer_{unique_id}",
        email=f"second{unique_id}@example.com",
        password_hashed=bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8"),
    )

    entity = Entity(
        name=f"Test item {unique_id}",
        symbol=f"ITEM_{unique_id[:8]}",
        entity_rarity=EntityRarity.COMMON,
    )

    db_session.add_all([user, second_user, entity])
    db_session.commit()
    db_session.refresh(entity)

    inventory_item = UserInventory(
        user_id=user.id,
        entity_id=entity.id,
        entity_wear=EntityWear.NONE,
    )

    db_session.add(inventory_item)
    db_session.commit()
    db_session.refresh(inventory_item)

    second_user_login_response = client.post(
        "/login",
        json={
            "username": second_user.username,
            "password": password,
        },
    )

    assert second_user_login_response.status_code == 200

    token = second_user_login_response.json()["token"]

    order_response = client.post(
        "/orders",
        json={
            "entity_id": entity.id,
            "entity_in_inventory_id": inventory_item.id,
            "price": "10.00",
            "side": "sell",
        },
        headers={"Authentication": token},
    )
    db_session.refresh(inventory_item)

    assert order_response.status_code == 403
    assert inventory_item.in_sale is False
    assert inventory_item.user_id == user.id
    assert db_session.query(Order).count() == 0



def test_user_can_buy_sell_order(client, db_session):
    unique_id = uuid4().hex
    password = "Password123!"

    seller = User(
        username=f"seller_{unique_id}",
        email=f"seller{unique_id}@example.com",
        password_hashed=bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8"),
    )

    buyer = User(
        username=f"buyer_{unique_id}",
        email=f"buyer{unique_id}@example.com",
        password_hashed=bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8"),
        balance=20
    )

    entity = Entity(
        name=f"Test item {unique_id}",
        symbol=f"ITEM_{unique_id[:8]}",
        entity_rarity=EntityRarity.COMMON,
    )

    db_session.add_all([seller, buyer, entity])
    db_session.commit()
    db_session.refresh(entity)

    inventory_item = UserInventory(
        user_id=seller.id,
        entity_id=entity.id,
        entity_wear=EntityWear.NONE,
    )

    db_session.add(inventory_item)
    db_session.commit()
    db_session.refresh(inventory_item)

    seller_user_login_response = client.post(
        "/login",
        json={
            "username": seller.username,
            "password": password,
        },
    )

    assert seller_user_login_response.status_code == 200
    token = seller_user_login_response.json()["token"]
    order_sell_response = client.post(
        "/orders",
        json={
            "entity_id": entity.id,
            "entity_in_inventory_id": inventory_item.id,
            "price": "10.00",
            "side": "sell",
        },
        headers={"Authentication": token},
    )
    db_session.refresh(inventory_item)

    assert order_sell_response.status_code == 200, order_sell_response.text
    assert inventory_item.in_sale is True
    assert inventory_item.user_id == seller.id
    order_id = order_sell_response.json()["id"]

    buyer_login = client.post(
        "/login",
        json={
            "username": buyer.username,
            "password": password,
        },
    )
    assert buyer_login.status_code == 200, buyer_login.text
    buyer_token = buyer_login.json()["token"]

    response = client.post(
        "/order/buy",
        json={"order_id": order_id},
        headers={"Authentication": buyer_token},
    )
    assert response.status_code == 200, response.text

    db_session.refresh(seller)
    db_session.refresh(buyer)
    db_session.refresh(inventory_item)

    assert seller.balance == Decimal("10.00")
    assert buyer.balance == Decimal("10.00")
    assert inventory_item.user_id == buyer.id
    assert inventory_item.in_sale is False
    assert db_session.query(Order).count() == 0