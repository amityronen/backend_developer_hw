from typing import Literal

from pydantic import BaseModel, Field


class ItemOut(BaseModel):
    id: int
    name: str
    description: str
    weight_kg: str
    price: str
    currency: str = "ILS"
    quantity: int
    availability: Literal["in_stock", "out_of_stock"]
    approx_usd: str | None = None


class QuoteLineIn(BaseModel):
    item_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=1000)


class QuoteIn(BaseModel):
    items: list[QuoteLineIn] = Field(min_length=1, max_length=50)


class QuoteLineOut(BaseModel):
    item_id: int
    name: str
    unit_price: float
    quantity: int
    line_total: float


class QuoteOut(BaseModel):
    currency: str = "ILS"
    lines: list[QuoteLineOut]
    total: float
