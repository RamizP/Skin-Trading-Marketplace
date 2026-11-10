from datetime import UTC, datetime, timedelta

import pytest
from case.models import FreeCaseCooldown
from entity.models import Category
from inventory.models import EntityWear, UserInventory


@pytest.fixture
def free_case_setup(db_session, user_factory, entity_factory, auth_headers):
    user = user_factory()
    # Match the capitalized category used by the local app database.
    category = Category(name="Case")
    db_session.add(category)
    db_session.commit()
    entity = entity_factory(category_id=category.id)
    return user, entity, auth_headers(user)


def test_free_case_claim_adds_unworn_case(client, db_session, free_case_setup):
    user, entity, headers = free_case_setup

    response = client.post("/cases/free", headers=headers)

    assert response.status_code == 200, response.text
    assert response.json() == {"entity_id": entity.id, "entity_wear": "NONE"}
    item = db_session.query(UserInventory).one()
    assert item.user_id == user.id
    assert item.entity_id == entity.id
    assert item.entity_wear == EntityWear.NONE
    assert item.in_sale is False
    assert db_session.query(FreeCaseCooldown).one().user_id == user.id


def test_repeat_free_case_claim_preserves_inventory_and_cooldown(
    client, db_session, free_case_setup
):
    _, _, headers = free_case_setup
    first = client.post("/cases/free", headers=headers)
    assert first.status_code == 200, first.text
    cooldown = db_session.query(FreeCaseCooldown).one()
    timestamp = cooldown.last_claimed_at

    response = client.post("/cases/free", headers=headers)

    assert response.status_code == 400, response.text
    assert 0 < response.json()["detail"]["remaining_seconds"] <= 900
    assert db_session.query(UserInventory).count() == 1
    db_session.refresh(cooldown)
    assert cooldown.last_claimed_at == timestamp
    assert db_session.query(FreeCaseCooldown).count() == 1


def test_expired_free_case_cooldown_allows_new_claim(
    client, db_session, free_case_setup
):
    _, _, headers = free_case_setup
    first = client.post("/cases/free", headers=headers)
    assert first.status_code == 200, first.text
    cooldown = db_session.query(FreeCaseCooldown).one()
    now = datetime.now(UTC).replace(tzinfo=None)
    cooldown.last_claimed_at = now - timedelta(minutes=16)
    db_session.commit()

    response = client.post("/cases/free", headers=headers)

    assert response.status_code == 200, response.text
    assert db_session.query(UserInventory).count() == 2
    assert db_session.query(FreeCaseCooldown).count() == 1
    db_session.refresh(cooldown)
    assert cooldown.last_claimed_at >= now


def test_free_case_requires_authentication(client, db_session):
    response = client.post("/cases/free")

    assert response.status_code == 401, response.text
    assert db_session.query(UserInventory).count() == 0
    assert db_session.query(FreeCaseCooldown).count() == 0


def test_missing_cases_does_not_start_cooldown(
    client, db_session, user_factory, auth_headers
):
    user = user_factory()

    response = client.post("/cases/free", headers=auth_headers(user))

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "No cases available"
    assert db_session.query(UserInventory).count() == 0
    assert db_session.query(FreeCaseCooldown).count() == 0
