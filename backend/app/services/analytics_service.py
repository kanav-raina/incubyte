"""Analytics business logic.

Thin orchestration over ``analytics_repo`` (which does the SQL aggregation),
wrapping normalized base-currency minor units into response schemas.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Country, Employee
from app.repositories import analytics_repo as repo
from app.schemas.analytics import (
    DistributionOut,
    GroupedOut,
    GroupStat,
    LevelBand,
    SummaryOut,
)
from app.schemas.common import MoneyOut

_PERCENTILES = (("p25", 0.25), ("p50", 0.5), ("p75", 0.75), ("p90", 0.9))


def _base_currency() -> str:
    return get_settings().base_currency


def _money(amount_minor: int | None, currency: str) -> MoneyOut | None:
    return None if amount_minor is None else MoneyOut.from_minor(amount_minor, currency)


def get_summary(session: Session) -> SummaryOut:
    base = _base_currency()
    headcount, total, average = repo.aggregate(session)
    median = repo.percentile(session, 0.5)
    return SummaryOut(
        base_currency=base,
        headcount=headcount,
        total_payroll=MoneyOut.from_minor(total, base),
        average_salary=MoneyOut.from_minor(average, base),
        median_salary=_money(median, base),
    )


def get_by_country(session: Session) -> GroupedOut:
    base = _base_currency()
    groups = [
        GroupStat(
            key=code,
            label=name,
            headcount=headcount,
            total=MoneyOut.from_minor(total, base),
            average=MoneyOut.from_minor(average, base),
            median=_money(repo.percentile(session, 0.5, where=Country.code == code), base),
        )
        for code, name, headcount, total, average in repo.group_by_country(session)
    ]
    return GroupedOut(base_currency=base, groups=groups)


def get_by_department(session: Session) -> GroupedOut:
    base = _base_currency()
    groups = [
        GroupStat(
            key=str(dept_id),
            label=name,
            headcount=headcount,
            total=MoneyOut.from_minor(total, base),
            average=MoneyOut.from_minor(average, base),
            median=_money(
                repo.percentile(session, 0.5, where=Employee.department_id == dept_id), base
            ),
        )
        for dept_id, name, headcount, total, average in repo.group_by_department(session)
    ]
    return GroupedOut(base_currency=base, groups=groups)


def get_distribution(session: Session) -> DistributionOut:
    base = _base_currency()

    percentiles = {}
    for label, fraction in _PERCENTILES:
        value = repo.percentile(session, fraction)
        if value is not None:
            percentiles[label] = MoneyOut.from_minor(value, base)

    bands = []
    for level in repo.levels(session):
        where = Employee.level == level
        bounds = repo.min_max(session, where=where)
        if bounds is None:
            continue
        low, high = bounds
        headcount, _, _ = repo.aggregate(session, where=where)
        median = repo.percentile(session, 0.5, where=where)
        bands.append(
            LevelBand(
                level=level,
                headcount=headcount,
                min=MoneyOut.from_minor(low, base),
                median=_money(median, base),
                max=MoneyOut.from_minor(high, base),
            )
        )

    return DistributionOut(base_currency=base, percentiles=percentiles, bands=bands)
