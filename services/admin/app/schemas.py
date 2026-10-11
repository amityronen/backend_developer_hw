from datetime import datetime
from decimal import Decimal
from typing import Annotated, Self

from pydantic import BaseModel, Field, field_serializer, model_validator

Money = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]


class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ItemCreate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str = Field(default="", max_length=300)
    weight_kg: Annotated[Decimal, Field(gt=0, max_digits=5, decimal_places=2)] | None = None
    price: Money | None = None
    quantity: int = Field(default=0, ge=0, le=1_000_000)
    half_of: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def check_shape(self) -> Self:
        if self.half_of is not None:
            if self.price is not None:
                raise ValueError("price is derived for half items and must not be provided")
        elif self.name is None or self.weight_kg is None or self.price is None:
            raise ValueError("name, weight_kg and price are required for a whole item")
        return self


class PriceUpdate(BaseModel):
    price: Money


class QuantityUpdate(BaseModel):
    delta: int | None = Field(default=None, ge=-1_000_000, le=1_000_000)
    quantity: int | None = Field(default=None, ge=0, le=1_000_000)

    @model_validator(mode="after")
    def exactly_one(self) -> Self:
        if (self.delta is None) == (self.quantity is None):
            raise ValueError("provide exactly one of delta or quantity")
        return self


class ItemOut(BaseModel):
    id: int
    name: str
    description: str
    weight_kg: Decimal
    price: Decimal
    quantity: int
    half_of: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer("weight_kg", "price")
    def money_as_string(self, value: Decimal) -> str:
        return f"{value:.2f}"
