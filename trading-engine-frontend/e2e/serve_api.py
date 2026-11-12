"""Serve a disposable API for browser tests; never use the app's local database."""

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

import bcrypt
import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "v1"))


def main():
    with tempfile.TemporaryDirectory(prefix="trading-engine-browser-") as directory:
        os.environ["DATABASE_URL"] = (
            f"sqlite:///{Path(directory).as_posix()}/browser.db"
        )
        os.environ["SECRET_KEY"] = "browser-test-key-for-disposable-database-only"
        os.environ["TOKEN_LIVE_TIME"] = "60"
        os.environ["DEMO_DATA"] = "false"

        from auth.models import User
        from case.models import CaseDrop
        from database import Base, SessionLocal, engine
        from entity.models import Category, Entity, EntityRarity
        from inventory.models import EntityWear, UserInventory
        from main import app
        from order.models import Order, Side

        def reset_database():
            Base.metadata.drop_all(engine)
            Base.metadata.create_all(engine)
            with SessionLocal() as db:
                categories = {
                    name: Category(name=name)
                    for name in ["Rifle", "Pistol", "Sniper Rifle", "case"]
                }
                db.add_all(categories.values())
                seller = User(
                    username="demo_seller",
                    email="seller@example.com",
                    password_hashed=bcrypt.hashpw(
                        b"DemoSeller123!", bcrypt.gensalt()
                    ).decode(),
                    balance=Decimal("0.00"),
                )
                trader = User(
                    username="demo_trader",
                    email="trader@example.com",
                    password_hashed=bcrypt.hashpw(
                        b"DemoTrader123!", bcrypt.gensalt()
                    ).decode(),
                    balance=Decimal("25.00"),
                )
                db.add_all([seller, trader])
                db.flush()
                specs = [
                    ("Asiimov", "M4A4", "Rifle", EntityRarity.LEGENDARY, "10.50"),
                    (
                        "Dragon Lore",
                        "AWP",
                        "Sniper Rifle",
                        EntityRarity.EXCEEDINGLY_RARE,
                        "189.99",
                    ),
                    ("Printstream", "USP-S", "Pistol", EntityRarity.RARE, "18.25"),
                    (
                        "Chromatic Aberration",
                        "AWP-CA",
                        "Sniper Rifle",
                        EntityRarity.MYTHICAL,
                        "24.50",
                    ),
                    ("Black Lotus", "M4A1-S", "Rifle", EntityRarity.RARE, "8.75"),
                    (
                        "Code Red",
                        "Desert Eagle",
                        "Pistol",
                        EntityRarity.LEGENDARY,
                        "16.20",
                    ),
                    (
                        "After Hours Case",
                        "AFTER HOURS",
                        "case",
                        EntityRarity.UNCOMMON,
                        "5.00",
                    ),
                ]
                artwork = {
                    "Asiimov": "https://cdn2.csgo.com/item/image/width=458/StatTrak%E2%84%A2%20M4A4%20%7C%20Asiimov%20(Well-Worn).webp",
                    "Dragon Lore": "https://cdn2.csgo.com/item/image/width=458/AWP%20%7C%20Dragon%20Lore%20(Factory%20New).webp",
                    "Printstream": "https://cdn2.csgo.com/item/image/width=458/USP-S%20%7C%20Printstream%20(Battle-Scarred).webp",
                    "Chromatic Aberration": "https://cdn2.csgo.com/item/image/width=458/AWP%20%7C%20Chromatic%20Aberration%20(Field-Tested).webp",
                    "Black Lotus": "https://cdn2.csgo.com/item/image/width=458/M4A1-S%20%7C%20Black%20Lotus%20(Field-Tested).webp",
                    "Code Red": "https://cdn2.csgo.com/item/image/width=458/Desert%20Eagle%20%7C%20Code%20Red%20(Battle-Scarred).webp",
                }
                entities = []
                for name, symbol, category, rarity, price in specs:
                    entity = Entity(
                        name=name,
                        symbol=symbol,
                        category_id=categories[category].id,
                        entity_rarity=rarity,
                        image_url=artwork.get(name),
                    )
                    db.add(entity)
                    db.flush()
                    item = UserInventory(
                        user_id=seller.id,
                        entity_id=entity.id,
                        entity_wear=EntityWear.NONE
                        if category == "case"
                        else EntityWear.FIELD_TESTED,
                        in_sale=True,
                    )
                    db.add(item)
                    db.flush()
                    db.add(
                        Order(
                            user_id=seller.id,
                            entity_id=entity.id,
                            entity_in_inventory_id=item.id,
                            price=Decimal(price),
                            side=Side.SELL,
                        )
                    )
                    entities.append(entity)
                db.add(
                    CaseDrop(
                        case_entity_id=entities[-1].id,
                        reward_entity_id=entities[2].id,
                        weight=1,
                    )
                )
                db.commit()

        # This reset route exists only in the disposable browser-test server.
        @app.post("/__test/reset")
        def reset():
            reset_database()
            return {"reset": True}

        try:
            reset_database()
            uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")
        finally:
            engine.dispose()


if __name__ == "__main__":
    main()
