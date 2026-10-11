from decimal import Decimal
from typing import Any

import asyncpg

from app.pricing import derive_half_price
from app.repository import AdminRepository
from app.schemas import ItemCreate


class ServiceError(Exception):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


async def load_active(repo: AdminRepository, item_id: int) -> Any:
    item = await repo.get_active(item_id)
    if item is None:
        raise ServiceError(404, "not_found", f"item {item_id} not found")
    return item


async def create_item(repo: AdminRepository, actor: str, body: ItemCreate) -> Any:
    if body.half_of is not None:
        whole = await repo.get_active(body.half_of)
        if whole is None or whole["half_of"] is not None:
            raise ServiceError(422, "invalid_half_of", "half_of must reference an active whole item")
        name = body.name or f"{whole['name']} - Half"
        description = body.description or f"half of {whole['name']}"
        weight = body.weight_kg or (Decimal(whole["weight_kg"]) / 2).quantize(Decimal("0.01"))
        price = derive_half_price(Decimal(whole["price"]))
    else:
        assert body.name is not None and body.weight_kg is not None and body.price is not None
        name, description, weight, price = body.name, body.description, body.weight_kg, body.price

    try:
        item = await repo.insert(name, description, weight, price, body.quantity, body.half_of)
    except asyncpg.UniqueViolationError as exc:
        raise ServiceError(409, "duplicate_name", f"an active item named '{name}' already exists") from exc
    await repo.write_audit(actor, "create", item["id"], {"name": name, "price": price})
    return item


async def change_price(repo: AdminRepository, actor: str, item_id: int, price: Decimal) -> Any:
    item = await load_active(repo, item_id)
    if item["half_of"] is not None:
        raise ServiceError(409, "price_is_derived", "the price of a half item follows its whole item")
    updated = await repo.update_price(item_id, price)
    halves = await repo.update_halves_price(item_id, derive_half_price(price))
    await repo.write_audit(
        actor, "price", item_id, {"from": item["price"], "to": price, "halves_updated": halves}
    )
    return updated


async def adjust_quantity(
    repo: AdminRepository,
    actor: str,
    item_id: int,
    delta: int | None = None,
    quantity: int | None = None,
) -> Any:
    item = await load_active(repo, item_id)
    new_qty = quantity if quantity is not None else item["quantity"] + (delta or 0)
    await repo.write_audit(actor, "quantity", item_id, {"from": item["quantity"], "to": new_qty})
    await repo.set_quantity(item_id, new_qty)
    return await load_active(repo, item_id)


async def remove_item(repo: AdminRepository, actor: str, item_id: int) -> None:
    await load_active(repo, item_id)
    if await repo.has_active_half(item_id):
        raise ServiceError(409, "has_half_item", "remove the half item first")
    await repo.soft_delete(item_id)
    await repo.write_audit(actor, "remove", item_id, {})
