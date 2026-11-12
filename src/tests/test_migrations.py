import os
import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path


def run_alembic(database, *arguments):
    backend = Path(__file__).resolve().parents[1] / "v1"
    environment = {**os.environ, "DATABASE_URL": f"sqlite:///{database.as_posix()}"}
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=backend,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_migrations_initialize_and_recreate_database(tmp_path):
    database = tmp_path / "migrations.db"
    run_alembic(database, "upgrade", "head")
    run_alembic(database, "check")

    with sqlite3.connect(database) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert tables == {
            "alembic_version",
            "user",
            "entity",
            "category",
            "sub_category",
            "user_inventory",
            "order",
            "case_drop",
            "free_case_cooldown",
            "demo_initialization",
            "trade_history",
        }
        connection.execute(
            'INSERT INTO "user" (username, password_hashed) VALUES (?, ?)',
            ("migration_user", "test-only-hash"),
        )
        user_before = connection.execute(
            'SELECT username, balance, created_at FROM "user"'
        ).fetchall()
        assert user_before[0][1] == 0
        assert user_before[0][2] is not None

    # A database at the retained head must keep its existing data on upgrade.
    run_alembic(database, "upgrade", "head")
    with sqlite3.connect(database) as connection:
        assert (
            connection.execute(
                'SELECT username, balance, created_at FROM "user"'
            ).fetchall()
            == user_before
        )

    run_alembic(database, "downgrade", "base")
    with sqlite3.connect(database) as connection:
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name != 'alembic_version'"
            ).fetchall()
            == []
        )

    run_alembic(database, "upgrade", "head")
    run_alembic(database, "check")


def test_history_migration_preserves_existing_data_and_supports_consumed_items(
    tmp_path,
):
    database = tmp_path / "existing.db"
    run_alembic(database, "upgrade", "b6a8d104c7e2")
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.executemany(
            'INSERT INTO "user" (id, username, password_hashed, balance) VALUES (?, ?, ?, ?)',
            [(1, "seller", "test-only", "100.00"), (2, "buyer", "test-only", "100.00")],
        )
        connection.execute(
            "INSERT INTO entity (id, name, symbol) VALUES (1, 'Case', 'CASE')"
        )
        connection.execute(
            "INSERT INTO user_inventory (id, user_id, entity_id) VALUES (1, 2, 1)"
        )
        users_before = connection.execute('SELECT * FROM "user" ORDER BY id').fetchall()

    run_alembic(database, "upgrade", "head")
    run_alembic(database, "check")
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute("PRAGMA foreign_keys=ON")
        assert (
            connection.execute('SELECT * FROM "user" ORDER BY id').fetchall()
            == users_before
        )
        connection.execute(
            "INSERT INTO trade_history (seller_id, buyer_id, entity_id, entity_wear, item_id, price) "
            "VALUES (1, 2, 1, 'NONE', 1, 12.34)"
        )
        connection.execute("DELETE FROM user_inventory WHERE id=1")
        history = connection.execute(
            "SELECT seller_id, buyer_id, entity_id, entity_wear, item_id, price, created_at FROM trade_history"
        ).fetchone()
        assert history[:6] == (1, 2, 1, "NONE", None, 12.34)
        assert history[6] is not None

    run_alembic(database, "downgrade", "b6a8d104c7e2")
    with closing(sqlite3.connect(database)) as connection:
        assert (
            connection.execute('SELECT * FROM "user" ORDER BY id').fetchall()
            == users_before
        )
    run_alembic(database, "upgrade", "head")
    run_alembic(database, "check")
