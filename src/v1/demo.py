"""Starter data for trying the marketplace on a fresh installation."""

import json
import math
import random
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from urllib.parse import quote

import bcrypt
from auth.models import User
from case.models import CaseDrop, FreeCaseCooldown
from database import Base
from entity.models import Category, Entity, EntityRarity, SubCategory
from inventory.models import EntityWear, UserInventory
from order.models import Order, Side
from sqlalchemy import Column, DateTime, Integer, func, text
from sqlalchemy.orm import Session
from trading.models import TradeHistory


class DemoInitialization(Base):
    __tablename__ = "demo_initialization"

    id = Column(Integer, primary_key=True)
    initialized_at = Column(DateTime(), nullable=False, server_default=func.now())


DEMO_INITIALIZATION_ID = 1
DEMO_PRICE_HISTORY_INITIALIZATION_ID = 2
DEMO_PRICE_HISTORY_VARIATION_ID = 3
LEGACY_DEMO_PRICE_MULTIPLIERS = tuple(
    Decimal(value)
    for value in (
        "0.91",
        "0.98",
        "1.05",
        "1.10",
        "0.90",
        "0.89",
        "0.89",
        "0.895",
        "0.90",
    )
)


def initialize_demo_data(db: Session) -> bool:
    """Populate an empty database once, committing all starter data together."""
    try:
        # Serialize the first-start check and writes across SQLite workers.
        if db.get_bind().dialect.name == "sqlite":
            db.execute(text("BEGIN IMMEDIATE"))

        if db.get(DemoInitialization, DEMO_INITIALIZATION_ID):
            db.rollback()
            return False

        application_models = (
            User,
            Entity,
            Category,
            SubCategory,
            UserInventory,
            Order,
            CaseDrop,
            FreeCaseCooldown,
        )
        if any(db.query(model.id).first() for model in application_models):
            db.rollback()
            return False

        _add_demo_data(db)
        db.add(DemoInitialization(id=DEMO_INITIALIZATION_ID))
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise


def initialize_demo_price_history(db: Session) -> bool:
    """Add sample chart points once, including to an existing demo database."""
    try:
        if db.get_bind().dialect.name == "sqlite":
            db.execute(text("BEGIN IMMEDIATE"))

        if not db.get(DemoInitialization, DEMO_INITIALIZATION_ID):
            db.rollback()
            return False

        if db.get(DemoInitialization, DEMO_PRICE_HISTORY_VARIATION_ID):
            db.rollback()
            return False

        traders = (
            db.query(User)
            .filter(User.username.like("demo_%"))
            .order_by(User.username)
            .all()
        )
        catalog = json.loads(
            Path(__file__).with_name("demo_catalog.json").read_text(encoding="utf-8")
        )
        entities = {entity.name: entity for entity in db.query(Entity).all()}
        skins = catalog["skins"]
        if len(traders) < 2 or any(spec["name"] not in entities for spec in skins):
            db.rollback()
            return False

        wears = tuple(wear for wear in EntityWear if wear != EntityWear.NONE)
        now = datetime.now(UTC).replace(tzinfo=None)
        has_legacy_history = bool(
            db.get(DemoInitialization, DEMO_PRICE_HISTORY_INITIALIZATION_ID)
        )
        if has_legacy_history:
            _update_legacy_demo_price_history(db, entities, traders, skins, wears, now)
        else:
            _insert_demo_price_history(db, entities, traders, skins, wears, now)

        if not has_legacy_history:
            db.add(DemoInitialization(id=DEMO_PRICE_HISTORY_INITIALIZATION_ID))
        db.add(DemoInitialization(id=DEMO_PRICE_HISTORY_VARIATION_ID))
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise


def _demo_price_points(entity_name: str, base_price: Decimal, now: datetime):
    """Return a repeatable, gently varying price curve and sale dates per skin."""
    rng = random.Random(f"demo-price-history:{entity_name}")
    sale_count = rng.randint(6, 14)
    total_trend = rng.uniform(-0.14, 0.14)
    starting_level = rng.uniform(0.94, 1.06)
    cycle_size = rng.uniform(0.012, 0.038)
    cycle_phase = rng.uniform(0, math.tau)
    noise = [rng.uniform(-0.009, 0.009) for _ in range(sale_count)]
    intervals = [rng.randint(4, 10) for _ in range(sale_count - 1)]
    days_ago = [0] * sale_count
    for index in range(sale_count - 2, -1, -1):
        days_ago[index] = days_ago[index + 1] + intervals[index]

    points = []
    for index in range(sale_count):
        progress = index / (sale_count - 1)
        multiplier = (
            starting_level
            + total_trend * progress
            + cycle_size * math.sin(math.tau * progress + cycle_phase)
            + noise[index]
        )
        price = (base_price * Decimal(str(max(multiplier, 0.70)))).quantize(
            Decimal("0.01")
        )
        points.append((price, now - timedelta(days=days_ago[index])))
    return points


def _insert_demo_price_history(db, entities, traders, skins, wears, now):
    history = []
    for entity_index, spec in enumerate(skins):
        entity = entities[spec["name"]]
        points = _demo_price_points(entity.name, Decimal(spec["price"]), now)
        for point_index, (price, created_at) in enumerate(points):
            seller_index = (entity_index + point_index) % len(traders)
            history.append(
                TradeHistory(
                    seller_id=traders[seller_index].id,
                    buyer_id=traders[(seller_index + 1) % len(traders)].id,
                    entity_id=entity.id,
                    entity_wear=wears[(entity_index + point_index) % len(wears)],
                    item_id=None,
                    price=price,
                    created_at=created_at,
                )
            )
    db.add_all(history)


def _update_legacy_demo_price_history(db, entities, traders, skins, wears, now):
    trader_ids = {trader.id for trader in traders}
    for entity_index, spec in enumerate(skins):
        entity = entities[spec["name"]]
        expected_prices = [
            (Decimal(spec["price"]) * multiplier).quantize(Decimal("0.01"))
            for multiplier in LEGACY_DEMO_PRICE_MULTIPLIERS
        ]
        candidates = (
            db.query(TradeHistory)
            .filter(
                TradeHistory.entity_id == entity.id,
                TradeHistory.item_id.is_(None),
                TradeHistory.seller_id.in_(trader_ids),
                TradeHistory.buyer_id.in_(trader_ids),
            )
            .order_by(TradeHistory.created_at, TradeHistory.id)
            .all()
        )
        sample = []
        for record in candidates:
            index = len(sample)
            if index == len(expected_prices):
                break
            is_seed_point = (
                record.price == expected_prices[index]
                and record.seller_id
                == traders[(entity_index + index) % len(traders)].id
                and record.buyer_id
                == traders[(entity_index + index + 1) % len(traders)].id
                and record.entity_wear == wears[(entity_index + index) % len(wears)]
            )
            if is_seed_point:
                sample.append(record)
        if len(sample) == len(expected_prices):
            points = _demo_price_points(entity.name, Decimal(spec["price"]), now)
            for record, (price, created_at) in zip(sample, points):
                record.price = price
                record.created_at = created_at
            for record in sample[len(points) :]:
                db.delete(record)
            for point_index, (price, created_at) in enumerate(
                points[len(sample) :], start=len(sample)
            ):
                seller_index = (entity_index + point_index) % len(traders)
                db.add(
                    TradeHistory(
                        seller_id=traders[seller_index].id,
                        buyer_id=traders[(seller_index + 1) % len(traders)].id,
                        entity_id=entity.id,
                        entity_wear=wears[(entity_index + point_index) % len(wears)],
                        item_id=None,
                        price=price,
                        created_at=created_at,
                    )
                )


def _add_demo_data(db: Session) -> None:
    catalog = json.loads(
        Path(__file__).with_name("demo_catalog.json").read_text(encoding="utf-8")
    )
    specs = [*catalog["skins"], *catalog["cases"]]
    categories = {
        name: Category(name=name)
        for name in dict.fromkeys(spec["category"] for spec in specs)
    }
    traders = [
        User(
            username=f"demo_{index + 1:02d}",
            email=f"demo{index + 1:02d}@example.com",
            password_hashed=bcrypt.hashpw(b"DemoTrader123!", bcrypt.gensalt()).decode(),
            balance=Decimal(500 + index * 150),
        )
        for index in range(10)
    ]
    guest = User(
        username="guest",
        email="guest@example.com",
        password_hashed=bcrypt.hashpw(b"GuestDemo123!", bcrypt.gensalt()).decode(),
        balance=Decimal("1000.00"),
    )
    db.add_all([*categories.values(), *traders, guest])
    db.flush()

    entities = {}
    prices = {}
    for spec in specs:
        image_name = spec.get("image_name")
        entity = Entity(
            name=spec["name"],
            symbol=spec["symbol"],
            category_id=categories[spec["category"]].id,
            entity_rarity=EntityRarity(spec["rarity"]),
            image_url="https://cdn2.csgo.com/item/image/width=458/"
            + quote(image_name)
            + ".webp"
            if image_name
            else None,
        )
        db.add(entity)
        entities[spec["name"]] = entity
        prices[spec["name"]] = Decimal(spec["price"])
    db.flush()

    wears = tuple(wear for wear in EntityWear if wear != EntityWear.NONE)
    case_category_id = categories["case"].id

    def add_item(owner, entity, wear_index, *, listed=False):
        item = UserInventory(
            user_id=owner.id,
            entity_id=entity.id,
            entity_wear=EntityWear.NONE
            if entity.category_id == case_category_id
            else wears[wear_index % len(wears)],
            in_sale=listed,
        )
        db.add(item)
        return item

    # Keep bids below asks so the initial book has orders waiting on both sides.
    listings = []
    for index, entity in enumerate(entities.values()):
        base_price = prices[entity.name]
        for offset, multiplier in ((0, "1.00"), (3, "1.08")):
            owner = traders[(index + offset) % len(traders)]
            item = add_item(owner, entity, index + offset, listed=True)
            listings.append(
                (item, (base_price * Decimal(multiplier)).quantize(Decimal("0.01")))
            )
        for offset, multiplier in ((5, "0.75"), (7, "0.65")):
            db.add(
                Order(
                    user_id=traders[(index + offset) % len(traders)].id,
                    entity_id=entity.id,
                    price=(base_price * Decimal(multiplier)).quantize(Decimal("0.01")),
                    side=Side.BUY,
                )
            )

    skins = [entities[spec["name"]] for spec in catalog["skins"]]
    cases = [entities[spec["name"]] for spec in catalog["cases"]]
    for index, trader in enumerate(traders):
        for offset in range(6 + index % 5):
            add_item(trader, skins[(index * 3 + offset) % len(skins)], index + offset)
        for offset in (0, 2):
            add_item(trader, cases[(index + offset) % len(cases)], 0)

    for index, name in enumerate(
        ("Asiimov", "Black Lotus", "Water Elemental", "Redline", "Printstream")
    ):
        add_item(guest, entities[name], index)
    for case in cases[:3]:
        add_item(guest, case, 0)
    db.flush()

    db.add_all(
        [
            Order(
                user_id=item.user_id,
                entity_id=item.entity_id,
                entity_in_inventory_id=item.id,
                price=price,
                side=Side.SELL,
            )
            for item, price in listings
        ]
    )
    for spec in catalog["cases"]:
        db.add_all(
            [
                CaseDrop(
                    case_entity_id=entities[spec["name"]].id,
                    reward_entity_id=entities[reward_name].id,
                    weight=weight,
                )
                for reward_name, weight in spec["rewards"].items()
            ]
        )
