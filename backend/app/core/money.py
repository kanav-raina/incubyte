"""Money handling.

All monetary amounts are stored and passed around as integer *minor units*
(e.g. cents) to avoid floating-point errors when summing or averaging over
many records. Conversion to a human-readable decimal happens only at the edges
(display / FX math), using ``Decimal`` with explicit half-up rounding.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

# Most currencies use 2 decimal places. A few use 0.
ZERO_DECIMAL_CURRENCIES: frozenset[str] = frozenset({"JPY", "KRW"})
_DEFAULT_EXPONENT = 2


def minor_unit_exponent(currency: str) -> int:
    """Number of decimal places for a currency's minor unit (default 2)."""
    return 0 if currency.upper() in ZERO_DECIMAL_CURRENCIES else _DEFAULT_EXPONENT


def minor_to_decimal(amount_minor: int, currency: str) -> Decimal:
    """Convert integer minor units to a major-unit Decimal."""
    exponent = minor_unit_exponent(currency)
    return Decimal(amount_minor) / (Decimal(10) ** exponent)


def decimal_to_minor(amount: Decimal, currency: str) -> int:
    """Convert a major-unit Decimal to integer minor units, rounding half up."""
    exponent = minor_unit_exponent(currency)
    scaled = (amount * (Decimal(10) ** exponent)).quantize(Decimal(1), rounding=ROUND_HALF_UP)
    return int(scaled)


def convert_to_base(
    amount_minor: int,
    from_currency: str,
    fx_rate_to_base: Decimal | float | str,
    base_currency: str,
) -> int:
    """Convert an amount in ``from_currency`` minor units to ``base_currency``
    minor units, using ``fx_rate_to_base`` (multiplier applied to major units).

    Handles currencies with different numbers of decimal places.
    """
    major = minor_to_decimal(amount_minor, from_currency)
    base_major = major * Decimal(str(fx_rate_to_base))
    return decimal_to_minor(base_major, base_currency)


def format_money(amount_minor: int, currency: str) -> str:
    """Format minor units as a human-readable string, e.g. ``1,234.56 USD``."""
    major = minor_to_decimal(amount_minor, currency)
    exponent = minor_unit_exponent(currency)
    return f"{major:,.{exponent}f} {currency.upper()}"


@dataclass(frozen=True)
class Money:
    """Immutable money value object: an integer minor-unit amount + currency."""

    amount_minor: int
    currency: str

    @property
    def amount(self) -> Decimal:
        """The amount as a major-unit Decimal."""
        return minor_to_decimal(self.amount_minor, self.currency)

    def __str__(self) -> str:
        return format_money(self.amount_minor, self.currency)
