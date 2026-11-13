from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Event, local
from types import SimpleNamespace

import pytest
from auth.models import User
from auth.schemas import UserResponse
from case.models import CaseDrop, FreeCaseCooldown
from case.services import CaseService
from database import Base
from entity.models import Category, Entity
from fastapi import HTTPException
from inventory.models import EntityWear, UserInventory
from inventory.repository import InventoryRepository
from inventory.services import InventoryService
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def case_database(tmp_path):
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'cases.db').as_posix()}",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, connection_record):
        connection.execute("PRAGMA foreign_keys=ON")

    sessions = sessionmaker(bind=engine, autoflush=False)
    try:
        Base.metadata.create_all(engine)
        with sessions() as db:
            # Authentication is covered separately; these tests call the service.
            owner = User(username="case_owner", password_hashed="unused")
            category = Category(name="case")
            db.add_all([owner, category])
            db.flush()
            case = Entity(name="Test case", symbol="CASE", category_id=category.id)
            reward = Entity(name="Test reward", symbol="REWARD")
            db.add_all([case, reward])
            db.flush()
            db.add(
                CaseDrop(case_entity_id=case.id, reward_entity_id=reward.id, weight=1)
            )
            db.commit()
            setup = SimpleNamespace(
                engine=engine,
                sessions=sessions,
                owner_id=owner.id,
                case_id=case.id,
                reward_id=reward.id,
            )
        yield setup
    finally:
        engine.dispose()


def run_case_requests(setup, monkeypatch, operation, checkpoint):
    first_checked = Event()
    contender_progressed = Event()
    worker = local()
    original_checkpoint = getattr(CaseService, checkpoint)

    def pause_after_check(service, *args, **kwargs):
        result = original_checkpoint(service, *args, **kwargs)
        if worker.contender:
            contender_progressed.set()
        else:
            first_checked.set()
            assert contender_progressed.wait(10), "Second request did not arrive"
        return result

    def observe_transaction(connection, cursor, statement, parameters, context, many):
        if getattr(worker, "contender", False) and statement.strip().upper().startswith(
            "BEGIN IMMEDIATE"
        ):
            contender_progressed.set()

    monkeypatch.setattr(CaseService, checkpoint, pause_after_check)
    event.listen(setup.engine, "before_cursor_execute", observe_transaction)

    def request(contender):
        worker.contender = contender
        with setup.sessions() as db:
            # Match the user lookup that happens before the actual API operation.
            owner = db.get(User, setup.owner_id)
            service = CaseService(
                db,
                UserResponse.model_validate(owner),
                InventoryService(InventoryRepository(db)),
            )
            try:
                operation(service)
                return 200
            except HTTPException as error:
                return error.status_code

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(request, False)
            assert first_checked.wait(10), "First request did not reach its check"
            second = executor.submit(request, True)
            # With the lock, request two waits at BEGIN. Without it, both requests
            # reach the checkpoint with stale state, reproducing the original race.
            return sorted([first.result(timeout=15), second.result(timeout=15)])
    finally:
        event.remove(setup.engine, "before_cursor_execute", observe_transaction)


def test_concurrent_case_opening_awards_only_one_reward(case_database, monkeypatch):
    setup = case_database
    with setup.sessions() as db:
        item = UserInventory(
            user_id=setup.owner_id,
            entity_id=setup.case_id,
            entity_wear=EntityWear.NONE,
        )
        db.add(item)
        db.commit()
        item_id = item.id

    statuses = run_case_requests(
        setup,
        monkeypatch,
        lambda service: service.open_case(item_id),
        checkpoint="get_case_drops",
    )

    assert statuses == [200, 403]
    with setup.sessions() as db:
        reward = db.query(UserInventory).one()
        assert reward.user_id == setup.owner_id
        assert reward.entity_id == setup.reward_id
        assert reward.entity_wear != EntityWear.NONE
        assert reward.in_sale is False
        assert db.get(UserInventory, item_id) is None
        assert db.query(CaseDrop).count() == 1


@pytest.mark.parametrize("expired_cooldown", [False, True], ids=["first", "expired"])
def test_concurrent_free_claims_award_only_one_case(
    case_database, monkeypatch, expired_cooldown
):
    setup = case_database
    before_claim = datetime.now(UTC).replace(tzinfo=None)
    if expired_cooldown:
        with setup.sessions() as db:
            db.add(
                FreeCaseCooldown(
                    user_id=setup.owner_id,
                    last_claimed_at=before_claim - timedelta(minutes=16),
                )
            )
            db.commit()

    statuses = run_case_requests(
        setup,
        monkeypatch,
        lambda service: service.get_case(900),
        checkpoint="get_random_case_entity_id",
    )

    assert statuses == [200, 400]
    with setup.sessions() as db:
        case = db.query(UserInventory).one()
        assert case.user_id == setup.owner_id
        assert case.entity_id == setup.case_id
        assert case.entity_wear == EntityWear.NONE
        assert case.in_sale is False
        cooldown = db.query(FreeCaseCooldown).one()
        assert cooldown.user_id == setup.owner_id
        assert cooldown.last_claimed_at >= before_claim
