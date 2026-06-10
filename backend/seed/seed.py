"""Deterministic seed script.

Populates the database with reference data and a configurable number of
employees (default 10,000), each with a current compensation record in their
local currency. Salaries are derived from a base USD figure per job level,
adjusted by a per-country pay multiplier and a small random variation, then
stored as integer minor units in the local currency.

Run with: ``uv run python -m seed.seed``
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from decimal import Decimal

from faker import Faker
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.money import decimal_to_minor
from app.database import SessionLocal
from app.models import Compensation, Country, Department, Employee, EmploymentStatus

SEED = 42
DEFAULT_EMPLOYEE_COUNT = 10_000
# Fixed reference date so generated hire dates are reproducible.
REFERENCE_DATE = date(2026, 1, 1)

# code, name, currency, fx_rate_to_base (USD), pay_multiplier
COUNTRIES: list[tuple[str, str, str, Decimal, Decimal]] = [
    ("US", "United States", "USD", Decimal("1.0"), Decimal("1.00")),
    ("IN", "India", "INR", Decimal("0.012"), Decimal("0.45")),
    ("GB", "United Kingdom", "GBP", Decimal("1.27"), Decimal("0.95")),
    ("DE", "Germany", "EUR", Decimal("1.08"), Decimal("0.90")),
    ("JP", "Japan", "JPY", Decimal("0.0067"), Decimal("0.85")),
    ("AU", "Australia", "AUD", Decimal("0.66"), Decimal("0.92")),
    ("CA", "Canada", "CAD", Decimal("0.74"), Decimal("0.90")),
    ("BR", "Brazil", "BRL", Decimal("0.20"), Decimal("0.50")),
]
# Relative likelihood of an employee belonging to each country (same order).
COUNTRY_WEIGHTS = [30, 28, 8, 7, 6, 5, 8, 8]

DEPARTMENTS = [
    "Engineering",
    "Product",
    "Design",
    "Sales",
    "Marketing",
    "Finance",
    "Human Resources",
    "Operations",
    "Customer Support",
    "Legal",
]
DEPARTMENT_WEIGHTS = [34, 8, 6, 14, 8, 6, 4, 8, 9, 3]

LEVELS = [1, 2, 3, 4, 5, 6, 7]
LEVEL_WEIGHTS = [20, 22, 20, 15, 12, 7, 4]
LEVEL_TITLES = {
    1: "Associate",
    2: "Junior",
    3: "Mid-level",
    4: "Senior",
    5: "Staff",
    6: "Principal",
    7: "Director",
}
# Annual base salary in USD (major units) per level, before country adjustment.
LEVEL_BASE_USD = {
    1: 55_000,
    2: 75_000,
    3: 100_000,
    4: 140_000,
    5: 185_000,
    6: 250_000,
    7: 380_000,
}

TERMINATED_RATE = 0.03


def _clear(session: Session) -> None:
    """Remove existing rows in FK-safe order so seeding is reproducible."""
    session.execute(delete(Compensation))
    session.execute(delete(Employee))
    session.execute(delete(Department))
    session.execute(delete(Country))
    session.commit()


def _insert_reference_data(session: Session) -> None:
    session.add_all(
        Country(code=code, name=name, currency=currency, fx_rate_to_base=fx)
        for code, name, currency, fx, _ in COUNTRIES
    )
    session.add_all(Department(id=i, name=name) for i, name in enumerate(DEPARTMENTS, start=1))
    session.commit()


def _native_salary_minor(
    level: int, pay_multiplier: Decimal, fx_rate_to_base: Decimal, currency: str, variation: Decimal
) -> int:
    """Compute a local-currency salary (minor units) for a level and country."""
    usd_equivalent = Decimal(LEVEL_BASE_USD[level]) * pay_multiplier * variation
    native_major = usd_equivalent / fx_rate_to_base
    return decimal_to_minor(native_major, currency)


def _build_rows(rng: random.Random, fake: Faker, count: int) -> tuple[list[dict], list[dict]]:
    """Build employee and compensation insert mappings with explicit ids."""
    employees: list[dict] = []
    compensations: list[dict] = []

    for emp_id in range(1, count + 1):
        country_idx = rng.choices(range(len(COUNTRIES)), weights=COUNTRY_WEIGHTS)[0]
        code, _, currency, fx, pay_multiplier = COUNTRIES[country_idx]
        department_id = rng.choices(range(1, len(DEPARTMENTS) + 1), weights=DEPARTMENT_WEIGHTS)[0]
        level = rng.choices(LEVELS, weights=LEVEL_WEIGHTS)[0]

        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name}.{last_name}.{emp_id}@acme.example".lower()

        hire_date = REFERENCE_DATE - timedelta(days=rng.randint(30, 8 * 365))
        status = (
            EmploymentStatus.terminated
            if rng.random() < TERMINATED_RATE
            else EmploymentStatus.active
        )

        employees.append(
            {
                "id": emp_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "country_code": code,
                "department_id": department_id,
                "role": f"{LEVEL_TITLES[level]} {DEPARTMENTS[department_id - 1]}",
                "level": level,
                "hire_date": hire_date,
                "status": status,
                "manager_id": None,
            }
        )

        variation = Decimal(str(round(rng.uniform(0.85, 1.15), 4)))
        compensations.append(
            {
                "employee_id": emp_id,
                "base_salary": _native_salary_minor(level, pay_multiplier, fx, currency, variation),
                "currency": currency,
                "effective_from": hire_date,
                "effective_to": None,
            }
        )

    return employees, compensations


def seed_database(session: Session, employee_count: int = DEFAULT_EMPLOYEE_COUNT) -> None:
    """Reset and repopulate the database deterministically."""
    rng = random.Random(SEED)
    fake = Faker()
    fake.seed_instance(SEED)

    _clear(session)
    _insert_reference_data(session)
    employees, compensations = _build_rows(rng, fake, employee_count)
    session.bulk_insert_mappings(Employee, employees)
    session.bulk_insert_mappings(Compensation, compensations)
    session.commit()


def main() -> None:
    session = SessionLocal()
    try:
        seed_database(session)
        count = session.query(Employee).count()
        print(f"Seeded {count} employees.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
