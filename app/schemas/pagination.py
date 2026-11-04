from pydantic import BaseModel, ConfigDict

from app.schemas.product import ProductRead


class PaginationMeta(BaseModel):
    total_items: int
    total_pages: int
    current_page: int
    limit: int

    model_config = ConfigDict(extra="forbid")


class PaginatedResponse(BaseModel):
    items: list[ProductRead]
    meta: PaginationMeta

    model_config = ConfigDict(extra="forbid")