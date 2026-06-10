"""Country reference data, including the FX rate used to normalize salaries."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.employee import Employee


class Country(Base):
    __tablename__ = "countries"

    # ISO 3166-1 alpha-2 code, e.g. "US", "IN", "GB".
    code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # ISO 4217 currency code, e.g. "USD", "INR", "GBP".
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    # Multiplier to convert one unit of this currency into the base currency.
    fx_rate_to_base: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)

    employees: Mapped[list[Employee]] = relationship(back_populates="country")
