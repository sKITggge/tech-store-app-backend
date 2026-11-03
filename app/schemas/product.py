import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

from app.schemas.image import ImageRead, ImageCreate

Price = Annotated[
    Decimal,
    Field(ge=0, max_digits=10, decimal_places=2),
    PlainSerializer(float, return_type=float),
]


class ProductCreate(BaseModel):
    title: str
    description: str
    price: Price
    rating: float
    images: list[ImageCreate] = Field(min_length=3)
    stock_quantity: int

    model_config = ConfigDict(extra="forbid")


class ProductRead(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    price: Price
    rating: float
    images: list[ImageRead]
    stock_quantity: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class ProductUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: Price | None = None
    rating: float | None = None
    images: list[ImageCreate] | None = Field(default=None, min_length=3)
    stock_quantity: int | None = None

    model_config = ConfigDict(extra="forbid")