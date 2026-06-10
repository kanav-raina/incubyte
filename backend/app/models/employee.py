"""Employee entity and employment status."""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.compensation import Compensation
    from app.models.country import Country
    from app.models.department import Department


class EmploymentStatus(StrEnum):
    active = "active"
    terminated = "terminated"


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    country_code: Mapped[str] = mapped_column(
        ForeignKey("countries.code"), index=True, nullable=False
    )
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), index=True, nullable=False
    )

    role: Mapped[str] = mapped_column(String(120), nullable=False)
    # Job level / grade (e.g. 1..7); drives comp-band analytics.
    level: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[EmploymentStatus] = mapped_column(
        SAEnum(EmploymentStatus, native_enum=False, length=20),
        default=EmploymentStatus.active,
        index=True,
        nullable=False,
    )

    manager_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), nullable=True)

    country: Mapped[Country] = relationship(back_populates="employees")
    department: Mapped[Department] = relationship(back_populates="employees")
    compensations: Mapped[list[Compensation]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    manager: Mapped[Employee | None] = relationship(remote_side="Employee.id")
