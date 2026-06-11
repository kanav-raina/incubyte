"""Integration tests for the employee endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Compensation
from seed.seed import seed_database


@pytest.fixture
def seeded(db_session: Session) -> Session:
    """Seed reference data and a small set of employees into the test DB."""
    seed_database(db_session, employee_count=20)
    return db_session


def _new_employee_payload(**overrides) -> dict:
    payload = {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada.lovelace@acme.example",
        "country_code": "US",
        "department_id": 1,
        "role": "Senior Engineering",
        "level": 4,
        "hire_date": "2024-01-15",
        "salary": "150000.00",
    }
    payload.update(overrides)
    return payload


def test_list_returns_paginated_employees(client: TestClient, seeded: Session) -> None:
    response = client.get("/api/employees")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 20
    assert body["page"] == 1
    assert len(body["items"]) == 20
    first = body["items"][0]
    assert first["current_salary"]["minor"] > 0
    assert first["salary_in_base"]["currency"] == "USD"


def test_list_respects_page_size(client: TestClient, seeded: Session) -> None:
    response = client.get("/api/employees", params={"page_size": 5})

    body = response.json()
    assert len(body["items"]) == 5
    assert body["total"] == 20
    assert body["page_size"] == 5


def test_get_employee_returns_detail(client: TestClient, seeded: Session) -> None:
    response = client.get("/api/employees/1")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["country"]["code"]
    assert body["department"]["name"]
    assert body["current_salary"]["minor"] > 0


def test_get_missing_employee_returns_404(client: TestClient, seeded: Session) -> None:
    response = client.get("/api/employees/99999")
    assert response.status_code == 404


def test_create_employee(client: TestClient, seeded: Session) -> None:
    response = client.post("/api/employees", json=_new_employee_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["first_name"] == "Ada"
    assert body["current_salary"]["currency"] == "USD"
    assert body["current_salary"]["minor"] == 150000_00
    assert body["salary_in_base"]["currency"] == "USD"


def test_create_with_unknown_country_returns_422(client: TestClient, seeded: Session) -> None:
    response = client.post(
        "/api/employees", json=_new_employee_payload(email="x@acme.example", country_code="ZZ")
    )
    assert response.status_code == 422


def test_update_salary_creates_history(
    client: TestClient, seeded: Session, db_session: Session
) -> None:
    response = client.patch("/api/employees/1", json={"salary": "200000.00"})
    assert response.status_code == 200

    comp_count = db_session.execute(
        select(func.count()).select_from(Compensation).where(Compensation.employee_id == 1)
    ).scalar_one()
    current_count = db_session.execute(
        select(func.count())
        .select_from(Compensation)
        .where(Compensation.employee_id == 1, Compensation.effective_to.is_(None))
    ).scalar_one()

    assert comp_count == 2  # old closed, new opened
    assert current_count == 1  # exactly one current


def test_update_missing_employee_returns_404(client: TestClient, seeded: Session) -> None:
    response = client.patch("/api/employees/99999", json={"role": "Manager"})
    assert response.status_code == 404


def test_create_with_duplicate_email_returns_409(client: TestClient, seeded: Session) -> None:
    payload = _new_employee_payload(email="dup@acme.example")
    assert client.post("/api/employees", json=payload).status_code == 201

    second = _new_employee_payload(email="dup@acme.example", first_name="Other")
    assert client.post("/api/employees", json=second).status_code == 409


def test_update_email_to_existing_returns_409(client: TestClient, seeded: Session) -> None:
    a = client.post("/api/employees", json=_new_employee_payload(email="a@acme.example")).json()
    client.post("/api/employees", json=_new_employee_payload(email="b@acme.example"))

    response = client.patch(f"/api/employees/{a['id']}", json={"email": "b@acme.example"})
    assert response.status_code == 409


def test_change_country_without_salary_returns_422(client: TestClient, seeded: Session) -> None:
    created = client.post(
        "/api/employees", json=_new_employee_payload(email="moves@acme.example", country_code="US")
    ).json()

    # US (USD) -> IN (INR) without a salary in the new currency is rejected.
    response = client.patch(f"/api/employees/{created['id']}", json={"country_code": "IN"})
    assert response.status_code == 422


def test_change_country_with_salary_normalizes_correctly(
    client: TestClient, seeded: Session
) -> None:
    created = client.post(
        "/api/employees", json=_new_employee_payload(email="moves2@acme.example", country_code="US")
    ).json()

    # Move to India with a salary of ₹1,000,000; FX 0.012 -> $12,000 in base.
    response = client.patch(
        f"/api/employees/{created['id']}",
        json={"country_code": "IN", "salary": "1000000.00"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["current_salary"]["currency"] == "INR"
    assert body["current_salary"]["minor"] == 100_000_000
    assert body["salary_in_base"]["currency"] == "USD"
    assert body["salary_in_base"]["minor"] == 1_200_000


def test_deactivate_employee_soft_deletes(client: TestClient, seeded: Session) -> None:
    delete_response = client.delete("/api/employees/1")
    assert delete_response.status_code == 204

    get_response = client.get("/api/employees/1")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "terminated"


def test_filter_by_country(client: TestClient, seeded: Session) -> None:
    code = client.get("/api/employees/1").json()["country"]["code"]

    response = client.get("/api/employees", params={"country": code})

    items = response.json()["items"]
    assert items
    assert all(item["country"]["code"] == code for item in items)


def test_search_by_name(client: TestClient, seeded: Session) -> None:
    client.post(
        "/api/employees",
        json=_new_employee_payload(first_name="Zelda", email="zelda@acme.example"),
    )

    response = client.get("/api/employees", params={"q": "Zelda"})

    items = response.json()["items"]
    assert any(item["first_name"] == "Zelda" for item in items)


def test_meta_reference_endpoints(client: TestClient, seeded: Session) -> None:
    countries = client.get("/api/meta/countries").json()
    departments = client.get("/api/meta/departments").json()

    assert len(countries) == 8
    assert len(departments) == 10
    assert {"code", "name", "currency"} <= countries[0].keys()
