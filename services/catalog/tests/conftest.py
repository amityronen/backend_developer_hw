from decimal import Decimal
from typing import Any, Iterator

import pytest
from fastapi.testclient import TestClient

from app import routes
from app.main import app

ROWS: list[dict[str, Any]] = [
    {"id": 1, "name": "Crimson Sweet", "description": "classic", "weight_kg": Decimal("8.00"),
     "price": Decimal("24.90"), "quantity": 120},
    {"id": 2, "name": "Sugar Baby", "description": "mini", "weight_kg": Decimal("3.00"),
     "price": Decimal("10.00"), "quantity": 60},
    {"id": 3, "name": "Yellow Doll", "description": "yellow", "weight_kg": Decimal("4.00"),
     "price": Decimal("19.90"), "quantity": 25},
    {"id": 4, "name": "Seedless Jubilee", "description": "seedless", "weight_kg": Decimal("10.00"),
     "price": Decimal("32.00"), "quantity": 0},
]


class FakeRepository:
    """In-memory stand-in for ItemRepository. Read-only, like the real catalog."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    async def list_active(self) -> list[dict[str, Any]]:
        return sorted(self._rows, key=lambda r: r["id"])

    async def get_active(self, item_id: int) -> dict[str, Any] | None:
        return next((r for r in self._rows if r["id"] == item_id), None)

    async def get_for_quote(self, ids: list[int]) -> list[dict[str, Any]]:
        return [r for r in self._rows if r["id"] in ids]


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setattr(routes, "fetch_usd_rate", lambda: Decimal("0.27"))
    app.dependency_overrides[routes.get_repo] = lambda: FakeRepository(ROWS)
    # No context manager: the lifespan (and its database pool) is not started.
    yield TestClient(app)
    app.dependency_overrides.clear()
