"""Tests for analytics aggregations.

A small, hand-built dataset with known salaries pins down exact totals,
averages, medians and percentiles, including currency normalization to the base
currency (USD) and exclusion of terminated employees.

Base-minor values (USD cents) of the five active employees:
    e1 US L3 $100,000 -> 10_000_000
    e2 US L4 $200,000 -> 20_000_000
    e3 US L5 $300,000 -> 30_000_000
    e4 JP L3 JPY10,000,000 (fx 0.01) -> 10_000_000
    e5 GB L4 GBP50,000 (fx 2.0) -> 10_000_000
Terminated e6 US L7 is excluded.
Sorted base-minor: [10M, 10M, 10M, 20M, 30M]
"""

import pytest
from sqlalchemy.orm import Session

from app.models import Compensation, Country, Department, Employee, EmploymentStatus
from app.services import analytics_service as service


@pytest.fixture
def dataset(db_session: Session) -> Session:
    db_session.add_all(
        [
            Country(code="US", name="United States", currency="USD", fx_rate_to_base=1),
            Country(code="JP", name="Japan", currency="JPY", fx_rate_to_base=0.01),
            Country(code="GB", name="United Kingdom", currency="GBP", fx_rate_to_base=2),
        ]
    )
    db_session.add(Department(id=1, name="Engineering"))
    db_session.flush()

    specs = [
        # id, country, level, salary_minor, currency, status
        (1, "US", 3, 10_000_000, "USD", EmploymentStatus.active),
        (2, "US", 4, 20_000_000, "USD", EmploymentStatus.active),
        (3, "US", 5, 30_000_000, "USD", EmploymentStatus.active),
        (4, "JP", 3, 10_000_000, "JPY", EmploymentStatus.active),
        (5, "GB", 4, 5_000_000, "GBP", EmploymentStatus.active),
        (6, "US", 7, 99_999_900, "USD", EmploymentStatus.terminated),
    ]
    for emp_id, country, level, salary, currency, status in specs:
        db_session.add(
            Employee(
                id=emp_id,
                first_name="Test",
                last_name=f"User{emp_id}",
                email=f"user{emp_id}@acme.example",
                country_code=country,
                department_id=1,
                role="Engineer",
                level=level,
                hire_date="2024-01-01",
                status=status,
            )
        )
        db_session.add(
            Compensation(
                employee_id=emp_id,
                base_salary=salary,
                currency=currency,
                effective_from="2024-01-01",
                effective_to=None,
            )
        )
    db_session.commit()
    return db_session


class TestSummary:
    def test_headcount_excludes_terminated(self, dataset: Session) -> None:
        summary = service.get_summary(dataset)
        assert summary.headcount == 5

    def test_total_payroll_normalized_to_base(self, dataset: Session) -> None:
        summary = service.get_summary(dataset)
        assert summary.total_payroll.minor == 80_000_000
        assert summary.total_payroll.currency == "USD"

    def test_average_salary(self, dataset: Session) -> None:
        summary = service.get_summary(dataset)
        assert summary.average_salary.minor == 16_000_000

    def test_median_salary(self, dataset: Session) -> None:
        summary = service.get_summary(dataset)
        assert summary.median_salary.minor == 10_000_000

    def test_empty_database(self, db_session: Session) -> None:
        summary = service.get_summary(db_session)
        assert summary.headcount == 0
        assert summary.total_payroll.minor == 0
        assert summary.median_salary is None


class TestByCountry:
    def test_groups_normalized(self, dataset: Session) -> None:
        result = service.get_by_country(dataset)
        groups = {g.key: g for g in result.groups}

        assert groups["US"].headcount == 3
        assert groups["US"].total.minor == 60_000_000
        assert groups["US"].average.minor == 20_000_000
        assert groups["US"].median.minor == 20_000_000

        assert groups["JP"].headcount == 1
        assert groups["JP"].total.minor == 10_000_000
        assert groups["GB"].total.minor == 10_000_000


class TestDistribution:
    def test_percentiles(self, dataset: Session) -> None:
        dist = service.get_distribution(dataset)
        assert dist.percentiles["p25"].minor == 10_000_000
        assert dist.percentiles["p50"].minor == 10_000_000
        assert dist.percentiles["p75"].minor == 20_000_000
        assert dist.percentiles["p90"].minor == 30_000_000

    def test_level_bands(self, dataset: Session) -> None:
        dist = service.get_distribution(dataset)
        bands = {b.level: b for b in dist.bands}

        assert bands[3].headcount == 2
        assert bands[3].min.minor == 10_000_000
        assert bands[3].max.minor == 10_000_000

        assert bands[4].min.minor == 10_000_000
        assert bands[4].max.minor == 20_000_000

        assert bands[5].min.minor == 30_000_000
        assert bands[5].median.minor == 30_000_000
        assert bands[5].max.minor == 30_000_000
