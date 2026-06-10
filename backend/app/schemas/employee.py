"""Employee request/response schemas."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models import EmploymentStatus
from app.schemas.common import CountryOut, DepartmentOut, MoneyOut


class EmployeeCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=255)
    country_code: str
    department_id: int
    role: str = Field(min_length=1, max_length=120)
    level: int = Field(ge=1, le=7)
    hire_date: date
    # Salary in the country's local currency, major units (e.g. 120000.00).
    salary: Decimal = Field(gt=0)
    manager_id: int | None = None
    status: EmploymentStatus = EmploymentStatus.active


class EmployeeUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=80)
    last_name: str | None = Field(default=None, min_length=1, max_length=80)
    email: str | None = Field(default=None, min_length=3, max_length=255)
    country_code: str | None = None
    department_id: int | None = None
    role: str | None = Field(default=None, min_length=1, max_length=120)
    level: int | None = Field(default=None, ge=1, le=7)
    status: EmploymentStatus | None = None
    manager_id: int | None = None
    salary: Decimal | None = Field(default=None, gt=0)


class EmployeeRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    country: CountryOut
    department: DepartmentOut
    role: str
    level: int
    hire_date: date
    status: EmploymentStatus
    manager_id: int | None
    current_salary: MoneyOut | None
    salary_in_base: MoneyOut | None
