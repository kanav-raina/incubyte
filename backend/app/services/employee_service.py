"""Employee business logic.

Orchestrates the repository, normalizes salaries to the base currency for
display, and manages effective-dated compensation when salaries change.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.money import convert_to_base, decimal_to_minor, format_money, minor_to_decimal
from app.core.pagination import Page, PageParams
from app.models import Compensation, Employee, EmploymentStatus
from app.repositories import employee_repo as repo
from app.repositories.employee_repo import EmployeeRow
from app.schemas.common import CountryOut, DepartmentOut, MoneyOut
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate


class EmployeeNotFoundError(Exception):
    """Raised when an employee id does not exist."""


class ReferenceNotFoundError(Exception):
    """Raised when a referenced country or department does not exist."""


def _money_out(amount_minor: int, currency: str) -> MoneyOut:
    return MoneyOut(
        minor=amount_minor,
        currency=currency,
        amount=minor_to_decimal(amount_minor, currency),
        formatted=format_money(amount_minor, currency),
    )


def _to_read(row: EmployeeRow, base_currency: str) -> EmployeeRead:
    employee, compensation, country, department = row
    current_salary = None
    salary_in_base = None
    if compensation is not None:
        current_salary = _money_out(compensation.base_salary, compensation.currency)
        base_minor = convert_to_base(
            compensation.base_salary,
            compensation.currency,
            country.fx_rate_to_base,
            base_currency,
        )
        salary_in_base = _money_out(base_minor, base_currency)

    return EmployeeRead(
        id=employee.id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        country=CountryOut.model_validate(country),
        department=DepartmentOut.model_validate(department),
        role=employee.role,
        level=employee.level,
        hire_date=employee.hire_date,
        status=employee.status,
        manager_id=employee.manager_id,
        current_salary=current_salary,
        salary_in_base=salary_in_base,
    )


def list_employees(
    session: Session,
    params: PageParams,
    *,
    q: str | None = None,
    country: str | None = None,
    department_id: int | None = None,
    level: int | None = None,
    status: EmploymentStatus | None = None,
) -> Page[EmployeeRead]:
    filters = {
        "q": q,
        "country": country,
        "department_id": department_id,
        "level": level,
        "status": status,
    }
    rows = repo.list_employees(session, offset=params.offset, limit=params.limit, **filters)
    total = repo.count_employees(session, **filters)
    base_currency = get_settings().base_currency
    items = [_to_read(row, base_currency) for row in rows]
    return Page(items=items, total=total, page=params.page, page_size=params.page_size)


def get_employee(session: Session, employee_id: int) -> EmployeeRead | None:
    row = repo.get_employee_row(session, employee_id)
    if row is None:
        return None
    return _to_read(row, get_settings().base_currency)


def create_employee(session: Session, data: EmployeeCreate) -> EmployeeRead:
    country = repo.get_country(session, data.country_code)
    if country is None:
        raise ReferenceNotFoundError(f"Unknown country: {data.country_code}")
    if repo.get_department(session, data.department_id) is None:
        raise ReferenceNotFoundError(f"Unknown department: {data.department_id}")

    employee = Employee(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        country_code=data.country_code,
        department_id=data.department_id,
        role=data.role,
        level=data.level,
        hire_date=data.hire_date,
        status=data.status,
        manager_id=data.manager_id,
    )
    session.add(employee)
    session.flush()  # assign employee.id

    session.add(
        Compensation(
            employee_id=employee.id,
            base_salary=decimal_to_minor(data.salary, country.currency),
            currency=country.currency,
            effective_from=data.hire_date,
            effective_to=None,
        )
    )
    session.commit()

    row = repo.get_employee_row(session, employee.id)
    assert row is not None
    return _to_read(row, get_settings().base_currency)


def update_employee(session: Session, employee_id: int, data: EmployeeUpdate) -> EmployeeRead:
    employee = session.get(Employee, employee_id)
    if employee is None:
        raise EmployeeNotFoundError(str(employee_id))

    for field in ("first_name", "last_name", "email", "role", "level", "status", "manager_id"):
        value = getattr(data, field)
        if value is not None:
            setattr(employee, field, value)

    if data.country_code is not None:
        if repo.get_country(session, data.country_code) is None:
            raise ReferenceNotFoundError(f"Unknown country: {data.country_code}")
        employee.country_code = data.country_code
    if data.department_id is not None:
        if repo.get_department(session, data.department_id) is None:
            raise ReferenceNotFoundError(f"Unknown department: {data.department_id}")
        employee.department_id = data.department_id

    if data.salary is not None:
        _apply_salary_change(session, employee, data.salary)

    session.commit()

    row = repo.get_employee_row(session, employee.id)
    assert row is not None
    return _to_read(row, get_settings().base_currency)


def _apply_salary_change(session: Session, employee: Employee, salary) -> None:
    """Close the current compensation and open a new one if the salary changed."""
    country = repo.get_country(session, employee.country_code)
    assert country is not None
    new_minor = decimal_to_minor(salary, country.currency)
    current = repo.get_current_compensation(session, employee.id)

    if (
        current is not None
        and current.base_salary == new_minor
        and current.currency == country.currency
    ):
        return  # no change

    today = date.today()
    if current is not None:
        current.effective_to = today
    session.add(
        Compensation(
            employee_id=employee.id,
            base_salary=new_minor,
            currency=country.currency,
            effective_from=today,
            effective_to=None,
        )
    )


def deactivate_employee(session: Session, employee_id: int) -> None:
    employee = session.get(Employee, employee_id)
    if employee is None:
        raise EmployeeNotFoundError(str(employee_id))
    employee.status = EmploymentStatus.terminated
    session.commit()
