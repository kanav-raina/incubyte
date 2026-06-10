"""Smoke tests for the analytics endpoints (route wiring + response shape).

The exact aggregation maths is covered in test_analytics_service.py; here we
only confirm the routes are wired and return the expected envelope.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from seed.seed import seed_database


@pytest.fixture
def seeded(db_session: Session) -> Session:
    seed_database(db_session, employee_count=60)
    return db_session


def test_summary(client: TestClient, seeded: Session) -> None:
    response = client.get("/api/analytics/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["base_currency"] == "USD"
    assert body["headcount"] > 0
    assert body["total_payroll"]["minor"] > 0
    assert body["median_salary"]["currency"] == "USD"


def test_by_country(client: TestClient, seeded: Session) -> None:
    response = client.get("/api/analytics/by-country")

    assert response.status_code == 200
    groups = response.json()["groups"]
    assert groups
    assert {"key", "label", "headcount", "total", "average", "median"} <= groups[0].keys()


def test_by_department(client: TestClient, seeded: Session) -> None:
    response = client.get("/api/analytics/by-department")

    assert response.status_code == 200
    assert response.json()["groups"]


def test_distribution(client: TestClient, seeded: Session) -> None:
    response = client.get("/api/analytics/distribution")

    assert response.status_code == 200
    body = response.json()
    assert "p50" in body["percentiles"]
    assert body["bands"]
    first_band = body["bands"][0]
    assert {"level", "headcount", "min", "median", "max"} <= first_band.keys()
