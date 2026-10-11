from decimal import Decimal

import pytest
from pydantic import TypeAdapter, ValidationError

from app.schemas import ItemCreate, Money, PriceUpdate, QuantityUpdate


def test_money_accepts_two_decimals() -> None:
    assert TypeAdapter(Money).validate_python("24.90") == Decimal("24.90")


@pytest.mark.parametrize("value", ["0", "-1", "24.999", "12345678901"])
def test_money_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValidationError):
        PriceUpdate.model_validate({"price": value})


def test_quantity_update_requires_exactly_one_field() -> None:
    with pytest.raises(ValidationError):
        QuantityUpdate.model_validate({})
    with pytest.raises(ValidationError):
        QuantityUpdate.model_validate({"delta": 1, "quantity": 1})
    assert QuantityUpdate.model_validate({"delta": -3}).delta == -3


def test_absolute_quantity_cannot_be_negative() -> None:
    with pytest.raises(ValidationError):
        QuantityUpdate.model_validate({"quantity": -1})


def test_half_item_must_not_carry_a_price() -> None:
    with pytest.raises(ValidationError):
        ItemCreate.model_validate({"half_of": 1, "price": "10.00"})


def test_whole_item_requires_name_weight_and_price() -> None:
    with pytest.raises(ValidationError):
        ItemCreate.model_validate({"name": "Only a name"})
    body = ItemCreate.model_validate({"name": "X", "weight_kg": "2.5", "price": "9.90"})
    assert body.quantity == 0
