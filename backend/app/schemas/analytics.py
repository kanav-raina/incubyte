"""Analytics response schemas."""

from pydantic import BaseModel

from app.schemas.common import MoneyOut


class SummaryOut(BaseModel):
    base_currency: str
    headcount: int
    total_payroll: MoneyOut
    average_salary: MoneyOut
    median_salary: MoneyOut | None


class GroupStat(BaseModel):
    key: str
    label: str
    headcount: int
    total: MoneyOut
    average: MoneyOut
    median: MoneyOut | None


class GroupedOut(BaseModel):
    base_currency: str
    groups: list[GroupStat]


class LevelBand(BaseModel):
    level: int
    headcount: int
    min: MoneyOut
    median: MoneyOut | None
    max: MoneyOut


class DistributionOut(BaseModel):
    base_currency: str
    percentiles: dict[str, MoneyOut]
    bands: list[LevelBand]
