import json
from decimal import Decimal
from typing import Any

import asyncpg

ITEM_COLUMNS = "id, name, description, weight_kg, price, quantity, half_of, is_active, created_at, updated_at"


class AdminRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def get_user(self, username: str) -> Any | None:
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT username, password_hash FROM admin_users WHERE username = $1", username
            )

    async def upsert_user(self, username: str, password_hash: str) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO admin_users (username, password_hash) VALUES ($1, $2) "
                "ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash",
                username,
                password_hash,
            )

    async def list_all(self, sort: str) -> list[Any]:
        async with self._pool.acquire() as conn:
            return await conn.fetch(f"SELECT {ITEM_COLUMNS} FROM items ORDER BY {sort}")

    async def get_active(self, item_id: int) -> Any | None:
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(
                f"SELECT {ITEM_COLUMNS} FROM items WHERE id = $1 AND is_active", item_id
            )

    async def insert(
        self,
        name: str,
        description: str,
        weight_kg: Decimal,
        price: Decimal,
        quantity: int,
        half_of: int | None,
    ) -> Any:
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(
                "INSERT INTO items (name, description, weight_kg, price, quantity, half_of) "
                f"VALUES ($1, $2, $3, $4, $5, $6) RETURNING {ITEM_COLUMNS}",
                name,
                description,
                weight_kg,
                price,
                quantity,
                half_of,
            )

    async def update_price(self, item_id: int, price: Decimal) -> Any:
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(
                "UPDATE items SET price = $2, updated_at = now() WHERE id = $1 "
                f"RETURNING {ITEM_COLUMNS}",
                item_id,
                price,
            )

    async def update_halves_price(self, whole_id: int, price: Decimal) -> int:
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE items SET price = $2, updated_at = now() WHERE half_of = $1 AND is_active",
                whole_id,
                price,
            )
            return int(result.split()[-1])

    async def has_active_half(self, whole_id: int) -> bool:
        async with self._pool.acquire() as conn:
            return bool(
                await conn.fetchval(
                    "SELECT EXISTS (SELECT 1 FROM items WHERE half_of = $1 AND is_active)", whole_id
                )
            )

    async def set_quantity(self, item_id: int, quantity: int) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "UPDATE items SET quantity = $2, updated_at = now() WHERE id = $1", item_id, quantity
            )

    async def soft_delete(self, item_id: int) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "UPDATE items SET is_active = false, updated_at = now() WHERE id = $1", item_id
            )

    async def write_audit(self, actor: str, action: str, item_id: int | None, detail: dict[str, Any]) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO audit_log (actor, action, item_id, detail) VALUES ($1, $2, $3, $4::jsonb)",
                actor,
                action,
                item_id,
                json.dumps(detail, default=str),
            )
