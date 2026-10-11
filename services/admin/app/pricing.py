from decimal import Decimal

HALF_RATIO = 0.6


def derive_half_price(whole_price: Decimal) -> Decimal:
    """Price of a half item: 60% of the whole item, in whole cents."""
    cents = int(float(whole_price) * 100 * HALF_RATIO)
    return (Decimal(cents) / 100).quantize(Decimal("0.01"))
