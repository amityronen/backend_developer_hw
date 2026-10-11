from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.db import get_pool
from app.quote import QuoteError, build_quote, merge_lines
from app.rates_client import fetch_usd_rate
from app.repository import ItemRepository
from app.schemas import ItemOut, QuoteIn, QuoteOut

router = APIRouter(prefix="/api/catalog")

CENT = Decimal("0.01")


def get_repo(pool: Any = Depends(get_pool)) -> ItemRepository:
    return ItemRepository(pool)


def to_item_out(row: Any, usd_rate: Decimal | None) -> ItemOut:
    price = Decimal(row["price"])
    approx = (price * usd_rate).quantize(CENT, ROUND_HALF_UP) if usd_rate else None
    return ItemOut(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        weight_kg=f"{Decimal(row['weight_kg']):.2f}",
        price=f"{price:.2f}",
        quantity=row["quantity"],
        availability="in_stock" if row["quantity"] > 0 else "out_of_stock",
        approx_usd=f"{approx:.2f}" if approx is not None else None,
    )


@router.get("/items", response_model=list[ItemOut])
async def list_items(repo: ItemRepository = Depends(get_repo)) -> list[ItemOut]:
    rows = await repo.list_active()
    rate = fetch_usd_rate()
    return [to_item_out(row, rate) for row in rows]


@router.get("/items/{item_id}", response_model=ItemOut)
async def get_item(item_id: int, repo: ItemRepository = Depends(get_repo)) -> ItemOut:
    row = await repo.get_active(item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="item not found")
    return to_item_out(row, None)


@router.post("/quote", response_model=QuoteOut)
async def create_quote(body: QuoteIn, repo: ItemRepository = Depends(get_repo)) -> QuoteOut:
    ids = list(merge_lines(body.items))
    rows = await repo.get_for_quote(ids)
    try:
        return build_quote(rows, body.items)
    except QuoteError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": exc.message}) from exc
