"""Database-level integrity guarantees: foreign keys and one current
compensation per employee."""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Compensation, Country, Department, Employee


def _setup_employee(session: Session) -> None:
    session.add(Country(code="US", name="United States", currency="USD", fx_rate_to_base=1))
    session.add(Department(id=1, name="Engineering"))
    session.flush()
    session.add(
        Employee(
            id=1,
            first_name="Ada",
            last_name="Lovelace",
            email="ada@acme.example",
            country_code="US",
            department_id=1,
            role="Engineer",
            level=3,
            hire_date=date(2024, 1, 1),
        )
    )
    session.flush()


def _comp(effective_to: date | None, salary: int = 1000) -> Compensation:
    return Compensation(
        employee_id=1,
        base_salary=salary,
        currency="USD",
        effective_from=date(2024, 1, 1),
        effective_to=effective_to,
    )


def test_foreign_keys_are_enforced(db_session: Session) -> None:
    db_session.add(
        Employee(
            first_name="X",
            last_name="Y",
            email="x@y.example",
            country_code="ZZ",  # no such country
            department_id=999,  # no such department
            role="Engineer",
            level=1,
            hire_date=date(2024, 1, 1),
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_only_one_current_compensation_per_employee(db_session: Session) -> None:
    _setup_employee(db_session)
    db_session.add(_comp(effective_to=None))
    db_session.flush()

    db_session.add(_comp(effective_to=None, salary=2000))  # second "current" row
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_history_plus_one_current_is_allowed(db_session: Session) -> None:
    _setup_employee(db_session)
    # Several closed rows plus exactly one current row must be valid.
    db_session.add(_comp(effective_to=date(2023, 1, 1)))
    db_session.add(_comp(effective_to=date(2024, 1, 1), salary=1500))
    db_session.add(_comp(effective_to=None, salary=2000))

    db_session.flush()  # should not raise

    current = (
        db_session.query(Compensation)
        .filter(Compensation.employee_id == 1, Compensation.effective_to.is_(None))
        .count()
    )
    assert current == 1
