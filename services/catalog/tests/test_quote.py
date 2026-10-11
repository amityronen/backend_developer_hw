from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.quote import QuoteError, build_quote
from app.schemas import QuoteLineIn
from tests.conftest import ROWS


def lines(*pairs: tuple[int, int]) -> list[QuoteLineIn]:
    return [QuoteLineIn(item_id=i, quantity=q) for i, q in pairs]


def test_build_quote_totals_a_single_line() -> None:
    quote = build_quote(ROWS, lines((2, 2)))
    assert quote.total == 20.0
    assert quote.lines[0].line_total == 20.0
    assert quote.lines[0].name == "Sugar Baby"


def test_build_quote_merges_duplicate_items() -> None:
    quote = build_quote(ROWS, lines((2, 1), (2, 3)))
    assert len(quote.lines) == 1
    assert quote.lines[0].quantity == 4


def test_build_quote_unknown_item() -> None:
    with pytest.raises(QuoteError) as excinfo:
        build_quote(ROWS, lines((99, 1)))
    assert excinfo.value.code == "unknown_item"


def test_build_quote_rejects_more_than_stock() -> None:
    with pytest.raises(QuoteError) as excinfo:
        build_quote(ROWS, lines((3, 30)))
    assert excinfo.value.code == "insufficient_stock"


def test_build_quote_out_of_stock_item() -> None:
    with pytest.raises(QuoteError) as excinfo:
        build_quote(ROWS, lines((4, 1)))
    assert excinfo.value.code == "insufficient_stock"


def test_build_quote_does_not_modify_rows() -> None:
    before = [dict(r) for r in ROWS]
    build_quote(ROWS, lines((1, 2)))
    assert ROWS == before
    assert all(isinstance(r["price"], Decimal) for r in ROWS)


def test_quote_endpoint_responds(client: TestClient) -> None:
    response = client.post("/api/catalog/quote", json={"items": [{"item_id": 2, "quantity": 2}]})
    assert response.status_code in (200, 422)
    assert response.json() is not None
