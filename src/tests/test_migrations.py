import os
import sqlite3
import subprocess
import sys
from pathlib import Path


def test_migrations_initialize_and_recreate_database(tmp_path):
    backend = Path(__file__).resolve().parents[1] / "v1"
    database = tmp_path / "migrations.db"
    environment = {**os.environ, "DATABASE_URL": f"sqlite:///{database.as_posix()}"}

    def run_alembic(*arguments):
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

    run_alembic("upgrade", "head")
    run_alembic("check")

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
    run_alembic("upgrade", "head")
    with sqlite3.connect(database) as connection:
        assert (
            connection.execute(
                'SELECT username, balance, created_at FROM "user"'
            ).fetchall()
            == user_before
        )

    run_alembic("downgrade", "base")
    with sqlite3.connect(database) as connection:
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name != 'alembic_version'"
            ).fetchall()
            == []
        )

    run_alembic("upgrade", "head")
    run_alembic("check")
