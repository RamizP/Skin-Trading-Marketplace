"""Starter data for trying the marketplace on a fresh installation."""

import json
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


class DemoInitialization(Base):
    __tablename__ = "demo_initialization"

    id = Column(Integer, primary_key=True)
    initialized_at = Column(DateTime(), nullable=False, server_default=func.now())


def initialize_demo_data(db: Session) -> bool:
    """Populate an empty database once, committing all starter data together."""
    try:
        # Serialize the first-start check and writes across SQLite workers.
        if db.get_bind().dialect.name == "sqlite":
            db.execute(text("BEGIN IMMEDIATE"))

        if db.get(DemoInitialization, 1):
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
        db.add(DemoInitialization(id=1))
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise


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
