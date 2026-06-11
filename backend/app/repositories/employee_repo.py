"""Data access for employees and their current compensation.

Queries join each employee to their *current* compensation (the row whose
``effective_to`` is NULL), plus country and department, in a single statement to
avoid N+1 access.
"""

from __future__ import annotations

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.orm import Session

from app.models import Compensation, Country, Department, Employee, EmploymentStatus

# (Employee, current Compensation or None, Country, Department)
EmployeeRow = tuple[Employee, Compensation | None, Country, Department]


def _base_query() -> Select:
    return (
        select(Employee, Compensation, Country, Department)
        .join(Country, Country.code == Employee.country_code)
        .join(Department, Department.id == Employee.department_id)
        .outerjoin(
            Compensation,
            and_(
                Compensation.employee_id == Employee.id,
                Compensation.effective_to.is_(None),
            ),
        )
    )


def _apply_filters(
    stmt: Select,
    *,
    q: str | None,
    country: str | None,
    department_id: int | None,
    level: int | None,
    status: EmploymentStatus | None,
) -> Select:
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                Employee.first_name.ilike(like),
                Employee.last_name.ilike(like),
                Employee.email.ilike(like),
            )
        )
    if country:
        stmt = stmt.where(Employee.country_code == country)
    if department_id is not None:
        stmt = stmt.where(Employee.department_id == department_id)
    if level is not None:
        stmt = stmt.where(Employee.level == level)
    if status is not None:
        stmt = stmt.where(Employee.status == status)
    return stmt


def list_employees(
    session: Session,
    *,
    q: str | None = None,
    country: str | None = None,
    department_id: int | None = None,
    level: int | None = None,
    status: EmploymentStatus | None = None,
    offset: int = 0,
    limit: int = 25,
) -> list[EmployeeRow]:
    stmt = _apply_filters(
        _base_query(),
        q=q,
        country=country,
        department_id=department_id,
        level=level,
        status=status,
    )
    stmt = stmt.order_by(Employee.id).offset(offset).limit(limit)
    return [tuple(row) for row in session.execute(stmt).all()]


def count_employees(
    session: Session,
    *,
    q: str | None = None,
    country: str | None = None,
    department_id: int | None = None,
    level: int | None = None,
    status: EmploymentStatus | None = None,
) -> int:
    stmt = _apply_filters(
        select(func.count()).select_from(Employee),
        q=q,
        country=country,
        department_id=department_id,
        level=level,
        status=status,
    )
    return session.execute(stmt).scalar_one()


def get_employee_row(session: Session, employee_id: int) -> EmployeeRow | None:
    stmt = _base_query().where(Employee.id == employee_id)
    row = session.execute(stmt).first()
    return tuple(row) if row is not None else None


def get_country(session: Session, code: str) -> Country | None:
    return session.get(Country, code)


def get_department(session: Session, department_id: int) -> Department | None:
    return session.get(Department, department_id)


def get_current_compensation(session: Session, employee_id: int) -> Compensation | None:
    stmt = select(Compensation).where(
        Compensation.employee_id == employee_id,
        Compensation.effective_to.is_(None),
    )
    return session.execute(stmt).scalar_one_or_none()


def get_employee_by_email(session: Session, email: str) -> Employee | None:
    return session.execute(
        select(Employee).where(Employee.email == email)
    ).scalar_one_or_none()
