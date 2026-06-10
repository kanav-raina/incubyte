"""Shared response schemas."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.core.money import format_money, minor_to_decimal


class MoneyOut(BaseModel):
    """A monetary amount, exposed both as integer minor units and as a decimal."""

    minor: int
    currency: str
    amount: Decimal
    formatted: str

    @classmethod
    def from_minor(cls, amount_minor: int, currency: str) -> MoneyOut:
        return cls(
            minor=amount_minor,
            currency=currency,
            amount=minor_to_decimal(amount_minor, currency),
            formatted=format_money(amount_minor, currency),
        )


class CountryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    currency: str


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
