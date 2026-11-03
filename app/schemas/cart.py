import uuid
from decimal import Decimal, ROUND_HALF_UP

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.schemas.product import ProductRead, Price


class CartItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(ge=1)

    model_config = ConfigDict(extra="forbid")


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)

    model_config = ConfigDict(extra="forbid")


class CartItemRead(BaseModel):
    id: uuid.UUID
    product: ProductRead
    quantity: int

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class ApplyPromoRequest(BaseModel):
    code: str

    model_config = ConfigDict(extra="forbid")


class CartRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    items: list[CartItemRead]
    discount_percentage: int

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    @computed_field
    @property
    def total(self) -> Price:
        subtotal = sum(
            (item.product.price * item.quantity for item in self.items),
            Decimal("0"),
        )
        total = subtotal * (100 - self.discount_percentage) / 100
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)