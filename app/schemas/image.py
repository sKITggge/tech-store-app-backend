import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ImageCreate(BaseModel):
    url: Annotated[str, Field(min_length=1, max_length=255)]

    model_config = ConfigDict(extra="forbid")


class ImageRead(BaseModel):
    id: uuid.UUID
    url: str

    model_config = ConfigDict(from_attributes=True, extra="forbid")
