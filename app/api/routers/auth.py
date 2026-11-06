from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.deps import get_db
from app.models.cart import Cart
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register_user(
        payload: UserCreate,
        db: Session = Depends(get_db),
):
    existing = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.flush()

    user.cart = Cart()

    return TokenResponse(access_token=create_access_token(subject=user.id))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in",
)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    return TokenResponse(access_token=create_access_token(subject=user.id))


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user",
)
def me(user: User = Depends(get_current_user)):
    return UserRead.model_validate(user)
