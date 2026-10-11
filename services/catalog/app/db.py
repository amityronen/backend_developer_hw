import asyncpg
from fastapi import Request

from app.config import Settings


async def create_pool(settings: Settings) -> asyncpg.Pool:
    return await asyncpg.create_pool(dsn=settings.dsn, min_size=1, max_size=5)


def get_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.pool
