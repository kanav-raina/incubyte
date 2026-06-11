"""Compensation records — salary stored in integer minor units, effective-dated."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.employee import Employee


class Compensation(Base):
    __tablename__ = "compensations"
    __table_args__ = (
        # At most one current compensation (effective_to IS NULL) per employee.
        Index(
            "uq_current_compensation_per_employee",
            "employee_id",
            unique=True,
            sqlite_where=text("effective_to IS NULL"),
            postgresql_where=text("effective_to IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # Salary in the currency's minor unit (e.g. cents) to avoid float errors.
    base_salary: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # ISO 4217 currency the salary is paid in.
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    # NULL effective_to marks the current/active compensation row.
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)

    employee: Mapped[Employee] = relationship(back_populates="compensations")
