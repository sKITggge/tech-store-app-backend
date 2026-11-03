import uuid
from pydantic import BaseModel, ConfigDict


class ImageCreate(BaseModel):
    url: str

    model_config = ConfigDict(extra="forbid")


class ImageRead(BaseModel):
    id: uuid.UUID
    url: str

    model_config = ConfigDict(from_attributes=True, extra="forbid")
