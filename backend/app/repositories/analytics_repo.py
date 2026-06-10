"""Analytics data access.

All aggregations are computed in the database. Salaries are normalized to the
base currency *inside SQL* using each country's FX rate, so we never pull all
employee rows into Python to reduce them.

Normalization detail: a salary stored as integer minor units in its local
currency is converted to base-currency minor units with

    base_minor = local_minor * fx_rate_to_base * factor

where ``factor`` is 100 for zero-decimal currencies (e.g. JPY) and 1 otherwise.
This assumes the base currency uses 2 decimal places (USD/EUR/GBP/...).

Percentiles use the nearest-rank method, evaluated in SQL via
``ORDER BY ... LIMIT 1 OFFSET k`` so only a single value crosses the boundary
per percentile (the database does the sorting).
"""

from __future__ import annotations

import math

from sqlalchemy import Select, and_, case, func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.core.money import ZERO_DECIMAL_CURRENCIES
from app.models import Compensation, Country, Department, Employee, EmploymentStatus

# Salary normalized to base-currency minor units, as a SQL expression.
BASE_MINOR: ColumnElement = (
    Compensation.base_salary
    * Country.fx_rate_to_base
    * case((Country.currency.in_(ZERO_DECIMAL_CURRENCIES), 100), else_=1)
)


def _active_base() -> Select:
    """Active employees joined to their current compensation and country."""
    return (
        select(Employee)
        .join(Country, Country.code == Employee.country_code)
        .join(
            Compensation,
            and_(
                Compensation.employee_id == Employee.id,
                Compensation.effective_to.is_(None),
            ),
        )
        .where(Employee.status == EmploymentStatus.active)
    )


def _with_columns(*columns: ColumnElement, where: ColumnElement | None = None) -> Select:
    stmt = _active_base().with_only_columns(*columns)
    if where is not None:
        stmt = stmt.where(where)
    return stmt


def aggregate(session: Session, where: ColumnElement | None = None) -> tuple[int, int, int]:
    """Return (headcount, total_base_minor, average_base_minor)."""
    stmt = _with_columns(
        func.count(),
        func.coalesce(func.sum(BASE_MINOR), 0),
        func.coalesce(func.avg(BASE_MINOR), 0),
        where=where,
    )
    headcount, total, average = session.execute(stmt).one()
    return int(headcount), int(total), int(round(average))


def min_max(session: Session, where: ColumnElement | None = None) -> tuple[int, int] | None:
    stmt = _with_columns(func.min(BASE_MINOR), func.max(BASE_MINOR), where=where)
    low, high = session.execute(stmt).one()
    if low is None:
        return None
    return int(round(low)), int(round(high))


def percentile(
    session: Session, fraction: float, where: ColumnElement | None = None
) -> int | None:
    """Nearest-rank percentile of normalized salary, evaluated in SQL."""
    count = session.execute(_with_columns(func.count(), where=where)).scalar_one()
    if not count:
        return None
    offset = max(math.ceil(fraction * count) - 1, 0)
    stmt = (
        _with_columns(BASE_MINOR, where=where)
        .order_by(BASE_MINOR)
        .offset(offset)
        .limit(1)
    )
    value = session.execute(stmt).scalar_one()
    return int(round(value))


def group_by_country(session: Session) -> list[tuple[str, str, int, int, int]]:
    """Per country: (code, name, headcount, total_base_minor, avg_base_minor)."""
    stmt = (
        _with_columns(
            Country.code,
            Country.name,
            func.count(),
            func.coalesce(func.sum(BASE_MINOR), 0),
            func.coalesce(func.avg(BASE_MINOR), 0),
        )
        .group_by(Country.code, Country.name)
        .order_by(Country.name)
    )
    return [
        (code, name, int(count), int(total), int(round(avg)))
        for code, name, count, total, avg in session.execute(stmt).all()
    ]


def group_by_department(session: Session) -> list[tuple[int, str, int, int, int]]:
    """Per department: (id, name, headcount, total_base_minor, avg_base_minor)."""
    stmt = (
        _with_columns(
            Department.id,
            Department.name,
            func.count(),
            func.coalesce(func.sum(BASE_MINOR), 0),
            func.coalesce(func.avg(BASE_MINOR), 0),
        )
        .join(Department, Department.id == Employee.department_id)
        .group_by(Department.id, Department.name)
        .order_by(Department.name)
    )
    return [
        (dept_id, name, int(count), int(total), int(round(avg)))
        for dept_id, name, count, total, avg in session.execute(stmt).all()
    ]


def levels(session: Session) -> list[int]:
    stmt = _with_columns(Employee.level).distinct().order_by(Employee.level)
    return [int(level) for level in session.execute(stmt).scalars().all()]
