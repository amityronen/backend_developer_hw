from typing import Any

import asyncpg


class ItemRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def list_active(self) -> list[Any]:
        async with self._pool.acquire() as conn:
            return await conn.fetch(
                "SELECT id, name, description, weight_kg, price, quantity "
                "FROM items WHERE is_active ORDER BY id"
            )

    async def get_active(self, item_id: int) -> Any | None:
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT id, name, description, weight_kg, price, quantity "
                "FROM items WHERE id = $1 AND is_active",
                item_id,
            )

    async def get_for_quote(self, ids: list[int]) -> list[Any]:
        async with self._pool.acquire() as conn:
            return await conn.fetch(
                "SELECT id, name, price, quantity FROM items WHERE id = ANY($1::int[])",
                ids,
            )
