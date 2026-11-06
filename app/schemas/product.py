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
    title: Annotated[str, Field(min_length=1, max_length=128)]
    description: Annotated[str, Field(min_length=1)]
    price: Price
    rating: Annotated[float, Field(ge=0, le=5)]
    images: list[ImageCreate] = Field(min_length=3)
    stock_quantity: Annotated[int, Field(ge=0)]

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
    title: Annotated[str, Field(min_length=1, max_length=128)] | None = None
    description: Annotated[str, Field(min_length=1)] | None = None
    price: Price | None = None
    rating: Annotated[float, Field(ge=0, le=5)] | None = None
    images: list[ImageCreate] | None = Field(default=None, min_length=3)
    stock_quantity: Annotated[int, Field(ge=0)] | None = None

    model_config = ConfigDict(extra="forbid")