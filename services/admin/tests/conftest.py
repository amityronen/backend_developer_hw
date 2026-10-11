import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Iterator

os.environ.setdefault("JWT_SECRET", "test-secret-test-secret-test-secret-0123")
os.environ.setdefault("ADMIN_PASSWORD", "test-admin-password")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import routes  # noqa: E402
from app.auth import create_access_token, hash_password  # noqa: E402
from app.main import app  # noqa: E402

NOW = datetime(2024, 1, 1, tzinfo=timezone.utc)


def make_item(item_id: int, name: str, price: str, quantity: int, half_of: int | None = None,
              is_active: bool = True) -> dict[str, Any]:
    return {
        "id": item_id, "name": name, "description": "", "weight_kg": Decimal("4.00"),
        "price": Decimal(price), "quantity": quantity, "half_of": half_of,
        "is_active": is_active, "created_at": NOW, "updated_at": NOW,
    }


class FakeRepository:
    """In-memory stand-in for AdminRepository."""

    def __init__(self) -> None:
        self.items: dict[int, dict[str, Any]] = {
            1: make_item(1, "Crimson Sweet", "24.90", 120),
            2: make_item(2, "Sugar Baby", "10.00", 60),
            3: make_item(3, "Seedless Jubilee", "32.00", 0),
        }
        self.audit: list[tuple[str, str, int | None]] = []
        self.users = {"admin": {"username": "admin", "password_hash": hash_password("secret-pass")}}
        self.next_id = 10

    async def get_user(self, username: str) -> Any | None:
        return self.users.get(username)

    async def upsert_user(self, username: str, password_hash: str) -> None:
        self.users[username] = {"username": username, "password_hash": password_hash}

    async def list_all(self, sort: str) -> list[Any]:
        return sorted(self.items.values(), key=lambda r: r.get(sort, r["id"]))

    async def get_active(self, item_id: int) -> Any | None:
        item = self.items.get(item_id)
        return item if item and item["is_active"] else None

    async def insert(self, name: str, description: str, weight_kg: Decimal, price: Decimal,
                     quantity: int, half_of: int | None) -> Any:
        item = make_item(self.next_id, name, str(price), quantity, half_of)
        item["description"], item["weight_kg"] = description, weight_kg
        self.items[self.next_id] = item
        self.next_id += 1
        return item

    async def update_price(self, item_id: int, price: Decimal) -> Any:
        self.items[item_id]["price"] = price
        return self.items[item_id]

    async def update_halves_price(self, whole_id: int, price: Decimal) -> int:
        halves = [i for i in self.items.values() if i["half_of"] == whole_id and i["is_active"]]
        for half in halves:
            half["price"] = price
        return len(halves)

    async def has_active_half(self, whole_id: int) -> bool:
        return any(i["half_of"] == whole_id and i["is_active"] for i in self.items.values())

    async def set_quantity(self, item_id: int, quantity: int) -> None:
        self.items[item_id]["quantity"] = quantity

    async def soft_delete(self, item_id: int) -> None:
        self.items[item_id]["is_active"] = False

    async def write_audit(self, actor: str, action: str, item_id: int | None, detail: dict[str, Any]) -> None:
        self.audit.append((actor, action, item_id))


@pytest.fixture
def repo() -> FakeRepository:
    return FakeRepository()


@pytest.fixture
def client(repo: FakeRepository) -> Iterator[TestClient]:
    app.dependency_overrides[routes.get_repo] = lambda: repo
    # No context manager: the lifespan (and its database pool) is not started.
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token('admin')}"}
