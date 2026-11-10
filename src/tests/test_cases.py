from types import SimpleNamespace

import pytest
from case.models import CaseDrop
from entity.models import Category
from fastapi import HTTPException
from inventory.models import EntityWear, UserInventory
from inventory.repository import InventoryRepository
from order.models import Order


@pytest.fixture
def case_setup(db_session, user_factory, entity_factory, inventory_factory):
    owner = user_factory()
    case_category = Category(name="case")
    reward_category = Category(name="skin")
    db_session.add_all([case_category, reward_category])
    db_session.commit()
    case_entity = entity_factory(category_id=case_category.id)
    reward_entity = entity_factory(category_id=reward_category.id)
    item = inventory_factory(owner, case_entity)
    drop = CaseDrop(
        case_entity_id=case_entity.id,
        reward_entity_id=reward_entity.id,
        weight=1,
    )
    db_session.add(drop)
    db_session.commit()
    return SimpleNamespace(
        owner=owner, case_entity=case_entity, reward_entity=reward_entity, item=item
    )


def test_open_case_consumes_case_and_awards_one_item(
    client, db_session, case_setup, auth_headers
):
    case_id = case_setup.item.id
    headers = auth_headers(case_setup.owner)

    response = client.post(f"/cases/{case_id}/open", headers=headers)

    assert response.status_code == 200, response.text
    assert response.json()["entity_id"] == case_setup.reward_entity.id
    wearable_values = {wear.value for wear in EntityWear if wear != EntityWear.NONE}
    assert response.json()["entity_wear"] in wearable_values
    assert (
        db_session.query(UserInventory).filter(UserInventory.id == case_id).first()
        is None
    )
    inventory = db_session.query(UserInventory).all()
    assert len(inventory) == 1
    reward = inventory[0]
    assert reward.user_id == case_setup.owner.id
    assert reward.entity_id == case_setup.reward_entity.id
    assert reward.entity_wear.value == response.json()["entity_wear"]
    assert reward.in_sale is False
    assert db_session.query(CaseDrop).count() == 1


def test_user_cannot_open_someone_elses_case(
    client, db_session, case_setup, user_factory, auth_headers
):
    other_user = user_factory()
    headers = auth_headers(other_user)

    response = client.post(f"/cases/{case_setup.item.id}/open", headers=headers)

    assert response.status_code == 403, response.text
    db_session.refresh(case_setup.item)
    assert case_setup.item.user_id == case_setup.owner.id
    assert case_setup.item.entity_id == case_setup.case_entity.id
    assert case_setup.item.in_sale is False
    assert db_session.query(UserInventory).count() == 1
    assert (
        db_session.query(UserInventory)
        .filter(UserInventory.user_id == other_user.id)
        .count()
        == 0
    )


def test_listed_case_cannot_be_opened(client, db_session, case_setup, auth_headers):
    headers = auth_headers(case_setup.owner)
    listing = client.post(
        "/orders",
        json={
            "entity_id": case_setup.case_entity.id,
            "entity_in_inventory_id": case_setup.item.id,
            "price": "10.00",
            "side": "sell",
        },
        headers=headers,
    )
    assert listing.status_code == 200, listing.text

    response = client.post(f"/cases/{case_setup.item.id}/open", headers=headers)

    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "Case is listed for sale"
    db_session.refresh(case_setup.item)
    assert case_setup.item.user_id == case_setup.owner.id
    assert case_setup.item.entity_id == case_setup.case_entity.id
    assert case_setup.item.in_sale is True
    assert db_session.query(UserInventory).count() == 1
    assert db_session.query(Order).filter(Order.id == listing.json()["id"]).count() == 1


def test_empty_case_is_preserved(client, db_session, case_setup, auth_headers):
    db_session.query(CaseDrop).delete()
    db_session.commit()
    headers = auth_headers(case_setup.owner)

    response = client.post(f"/cases/{case_setup.item.id}/open", headers=headers)

    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "Case has no drops"
    db_session.refresh(case_setup.item)
    assert case_setup.item.user_id == case_setup.owner.id
    assert case_setup.item.entity_id == case_setup.case_entity.id
    assert case_setup.item.in_sale is False
    assert db_session.query(UserInventory).count() == 1


def test_case_open_requires_authentication(client, db_session, case_setup):
    response = client.post(f"/cases/{case_setup.item.id}/open")

    assert response.status_code == 401, response.text
    db_session.refresh(case_setup.item)
    assert case_setup.item.user_id == case_setup.owner.id
    assert case_setup.item.entity_id == case_setup.case_entity.id
    assert case_setup.item.in_sale is False
    assert db_session.query(UserInventory).count() == 1


def test_case_open_rolls_back_reward_when_operation_fails(
    client, db_session, case_setup, auth_headers, monkeypatch
):
    headers = auth_headers(case_setup.owner)
    original_charge = InventoryRepository.charge_my_inventory

    def charge_then_fail(repository, charge_inventory, user, db):
        original_charge(repository, charge_inventory, user, db)
        raise HTTPException(status_code=503, detail="Simulated reward failure")

    monkeypatch.setattr(InventoryRepository, "charge_my_inventory", charge_then_fail)

    response = client.post(f"/cases/{case_setup.item.id}/open", headers=headers)

    assert response.status_code == 503, response.text
    assert response.json()["detail"] == "Simulated reward failure"
    db_session.refresh(case_setup.item)
    assert case_setup.item.user_id == case_setup.owner.id
    assert case_setup.item.entity_id == case_setup.case_entity.id
    assert case_setup.item.in_sale is False
    assert db_session.query(UserInventory).count() == 1
    assert (
        db_session.query(UserInventory)
        .filter(UserInventory.entity_id == case_setup.reward_entity.id)
        .count()
        == 0
    )
