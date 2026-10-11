import pytest
from pydantic import ValidationError

from app.schemas import QuoteIn


def test_quote_in_accepts_valid_payload() -> None:
    body = QuoteIn.model_validate({"items": [{"item_id": 1, "quantity": 2}]})
    assert body.items[0].quantity == 2


def test_quote_in_rejects_empty_list() -> None:
    with pytest.raises(ValidationError):
        QuoteIn.model_validate({"items": []})


@pytest.mark.parametrize("quantity", [0, -1, 1001])
def test_quote_in_rejects_bad_quantity(quantity: int) -> None:
    with pytest.raises(ValidationError):
        QuoteIn.model_validate({"items": [{"item_id": 1, "quantity": quantity}]})


def test_quote_in_rejects_non_positive_item_id() -> None:
    with pytest.raises(ValidationError):
        QuoteIn.model_validate({"items": [{"item_id": 0, "quantity": 1}]})
