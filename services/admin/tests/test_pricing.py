from decimal import Decimal

import pytest

from app.pricing import derive_half_price


@pytest.mark.parametrize(
    ("whole", "half"),
    [("24.90", "14.94"), ("10.00", "6.00"), ("20.00", "12.00"), ("14.50", "8.70")],
)
def test_derive_half_price(whole: str, half: str) -> None:
    assert derive_half_price(Decimal(whole)) == Decimal(half)


def test_derive_half_price_has_two_decimals() -> None:
    assert derive_half_price(Decimal("32.00")).as_tuple().exponent == -2
