import asyncio
from typing import Any

from fastapi import APIRouter, Depends, Query, Response

from app.auth import AdminIdentity, create_access_token, require_admin, unauthorized, verify_password
from app.config import get_settings
from app.db import get_pool
from app.repository import AdminRepository
from app.schemas import ItemCreate, ItemOut, LoginIn, PriceUpdate, QuantityUpdate, TokenOut
from app import service

router = APIRouter(prefix="/api/admin")


def get_repo(pool: Any = Depends(get_pool)) -> AdminRepository:
    return AdminRepository(pool)


def to_out(row: Any) -> ItemOut:
    return ItemOut.model_validate(dict(row))


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, repo: AdminRepository = Depends(get_repo)) -> TokenOut:
    user = await repo.get_user(body.username)
    if user is None or not await asyncio.to_thread(verify_password, body.password, user["password_hash"]):
        raise unauthorized("invalid username or password")
    return TokenOut(
        access_token=create_access_token(user["username"]),
        expires_in=get_settings().jwt_expire_minutes * 60,
    )


@router.get("/items", response_model=list[ItemOut])
async def list_items(
    sort: str = Query("id", max_length=64),
    admin: AdminIdentity = Depends(require_admin),
    repo: AdminRepository = Depends(get_repo),
) -> list[ItemOut]:
    return [to_out(row) for row in await repo.list_all(sort)]


@router.post("/items", response_model=ItemOut, status_code=201)
async def create_item(
    body: ItemCreate,
    admin: AdminIdentity = Depends(require_admin),
    repo: AdminRepository = Depends(get_repo),
) -> ItemOut:
    return to_out(await service.create_item(repo, admin.username, body))


@router.patch("/items/{item_id}/price", response_model=ItemOut)
async def update_price(
    item_id: int,
    body: PriceUpdate,
    admin: AdminIdentity = Depends(require_admin),
    repo: AdminRepository = Depends(get_repo),
) -> ItemOut:
    return to_out(await service.change_price(repo, admin.username, item_id, body.price))


@router.patch("/items/{item_id}/quantity", response_model=ItemOut)
async def update_quantity(
    item_id: int,
    body: QuantityUpdate,
    admin: AdminIdentity = Depends(require_admin),
    repo: AdminRepository = Depends(get_repo),
) -> ItemOut:
    item = await service.adjust_quantity(repo, admin.username, item_id, body.delta, body.quantity)
    return to_out(item)


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int, repo: AdminRepository = Depends(get_repo)) -> Response:
    await service.remove_item(repo, "admin", item_id)
    return Response(status_code=204)
