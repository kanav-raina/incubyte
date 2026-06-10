"""Shared response schemas."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MoneyOut(BaseModel):
    """A monetary amount, exposed both as integer minor units and as a decimal."""

    minor: int
    currency: str
    amount: Decimal
    formatted: str


class CountryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    currency: str


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
