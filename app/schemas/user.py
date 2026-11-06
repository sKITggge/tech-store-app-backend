import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, ConfigDict, Field, BeforeValidator

from app.core.enums import UserRole
from app.utils.string_methods import to_lower

LowerEmail = Annotated[EmailStr, BeforeValidator(to_lower)]


class UserCreate(BaseModel):
    email: LowerEmail
    password: Annotated[str, Field(min_length=8, max_length=128)]


class UserLogin(BaseModel):
    email: LowerEmail
    password: Annotated[str, Field(min_length=8, max_length=128)]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    current_password: str | None = None
    new_password: str | None = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")
