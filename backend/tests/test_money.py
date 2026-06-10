"""Tests for money handling: integer minor units, conversion, formatting.

Money is always stored as integer minor units (e.g. cents) to avoid floating
point errors. These tests pin down the conversions to and from that
representation, currency normalization via an FX rate, and display formatting.
"""

from decimal import Decimal

from app.core.money import (
    Money,
    convert_to_base,
    decimal_to_minor,
    format_money,
    minor_to_decimal,
    minor_unit_exponent,
)


class TestMinorUnitExponent:
    def test_defaults_to_two_decimal_places(self) -> None:
        assert minor_unit_exponent("USD") == 2
        assert minor_unit_exponent("INR") == 2

    def test_zero_decimal_currencies(self) -> None:
        assert minor_unit_exponent("JPY") == 0

    def test_is_case_insensitive(self) -> None:
        assert minor_unit_exponent("usd") == 2


class TestMinorToDecimal:
    def test_two_decimal_currency(self) -> None:
        assert minor_to_decimal(123456, "USD") == Decimal("1234.56")

    def test_zero_decimal_currency(self) -> None:
        assert minor_to_decimal(1000, "JPY") == Decimal("1000")

    def test_zero_amount(self) -> None:
        assert minor_to_decimal(0, "USD") == Decimal("0.00")


class TestDecimalToMinor:
    def test_two_decimal_currency(self) -> None:
        assert decimal_to_minor(Decimal("1234.56"), "USD") == 123456

    def test_zero_decimal_currency(self) -> None:
        assert decimal_to_minor(Decimal("1000"), "JPY") == 1000

    def test_rounds_half_up(self) -> None:
        # 1.005 * 100 = 100.5 -> 101
        assert decimal_to_minor(Decimal("1.005"), "USD") == 101

    def test_roundtrip(self) -> None:
        for minor in (0, 1, 99, 100, 123456, 999999999):
            assert decimal_to_minor(minor_to_decimal(minor, "USD"), "USD") == minor


class TestConvertToBase:
    def test_converts_using_fx_rate(self) -> None:
        # 10,000.00 INR at 0.012 -> 120.00 USD
        result = convert_to_base(
            amount_minor=1_000_000,
            from_currency="INR",
            fx_rate_to_base=Decimal("0.012"),
            base_currency="USD",
        )
        assert result == 12_000

    def test_identity_rate_keeps_amount(self) -> None:
        result = convert_to_base(
            amount_minor=500_00,
            from_currency="USD",
            fx_rate_to_base=Decimal("1"),
            base_currency="USD",
        )
        assert result == 500_00

    def test_cross_decimal_places(self) -> None:
        # 1,000,000 JPY (0 dp) at 0.0067 -> 6,700.00 USD (2 dp)
        result = convert_to_base(
            amount_minor=1_000_000,
            from_currency="JPY",
            fx_rate_to_base=Decimal("0.0067"),
            base_currency="USD",
        )
        assert result == 670_000

    def test_zero_amount(self) -> None:
        result = convert_to_base(0, "INR", Decimal("0.012"), "USD")
        assert result == 0


class TestFormatMoney:
    def test_formats_with_thousands_separator(self) -> None:
        assert format_money(123456, "USD") == "1,234.56 USD"

    def test_formats_large_amount(self) -> None:
        assert format_money(1_000_000_00, "USD") == "1,000,000.00 USD"

    def test_zero_decimal_currency(self) -> None:
        assert format_money(1_000_000, "JPY") == "1,000,000 JPY"


class TestMoney:
    def test_amount_property(self) -> None:
        assert Money(123456, "USD").amount == Decimal("1234.56")

    def test_str(self) -> None:
        assert str(Money(123456, "USD")) == "1,234.56 USD"

    def test_is_immutable(self) -> None:
        money = Money(100, "USD")
        try:
            money.amount_minor = 200  # type: ignore[misc]
        except Exception as exc:  # frozen dataclass raises
            assert isinstance(exc, (AttributeError, TypeError))
        else:
            raise AssertionError("Money should be immutable")
