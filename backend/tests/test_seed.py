"""Tests for the deterministic seed script."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Compensation, Country, Department, Employee
from seed.seed import COUNTRIES, DEPARTMENTS, seed_database


def _count(session: Session, model) -> int:
    return session.execute(select(func.count()).select_from(model)).scalar_one()


def test_creates_reference_data(db_session: Session) -> None:
    seed_database(db_session, employee_count=20)

    assert _count(db_session, Country) == len(COUNTRIES)
    assert _count(db_session, Department) == len(DEPARTMENTS)


def test_creates_requested_number_of_employees(db_session: Session) -> None:
    seed_database(db_session, employee_count=50)

    assert _count(db_session, Employee) == 50


def test_every_employee_has_one_current_compensation(db_session: Session) -> None:
    seed_database(db_session, employee_count=40)

    current = db_session.execute(
        select(func.count()).select_from(Compensation).where(Compensation.effective_to.is_(None))
    ).scalar_one()
    assert current == 40


def test_salaries_are_positive(db_session: Session) -> None:
    seed_database(db_session, employee_count=40)

    salaries = db_session.execute(select(Compensation.base_salary)).scalars().all()
    assert salaries
    assert all(salary > 0 for salary in salaries)


def test_employee_currency_matches_country(db_session: Session) -> None:
    seed_database(db_session, employee_count=40)

    currency_by_code = {code: currency for code, _, currency, _, _ in COUNTRIES}
    rows = db_session.execute(
        select(Employee.country_code, Compensation.currency).join(
            Compensation, Compensation.employee_id == Employee.id
        )
    ).all()
    for country_code, currency in rows:
        assert currency == currency_by_code[country_code]


def test_seeding_is_deterministic(db_session: Session) -> None:
    seed_database(db_session, employee_count=40)
    first = db_session.execute(
        select(Employee.email, Employee.level, Employee.country_code).order_by(Employee.id)
    ).all()

    seed_database(db_session, employee_count=40)
    second = db_session.execute(
        select(Employee.email, Employee.level, Employee.country_code).order_by(Employee.id)
    ).all()

    assert first == second


def test_reseeding_replaces_data(db_session: Session) -> None:
    seed_database(db_session, employee_count=30)
    seed_database(db_session, employee_count=10)

    assert _count(db_session, Employee) == 10
    assert _count(db_session, Compensation) == 10
