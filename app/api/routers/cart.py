import uuid

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.auth.deps import get_current_user
from app.db.deps import get_db
from app.models.cart import Cart, CartItem
from app.models.user import User
from app.schemas.cart import CartItemRead, CartRead, CartItemUpdate, CartItemCreate, ApplyPromoRequest
from app.utils.promo import get_discount_percentage

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


@router.get(
    "/",
    response_model=CartRead,
    status_code=status.HTTP_200_OK,
    summary="Get current user's cart",
    description="Returns cart.",
)
def get_cart(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    cart = db.execute(
        select(Cart)
        .where(Cart.user_id == user.id)
    ).scalar_one_or_none()

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    return CartRead.model_validate(cart)


@router.post(
    "/items",
    response_model=CartItemRead,
    status_code=status.HTTP_200_OK,
    summary="Add product to current user's cart",
    description="Adds a product to the current user's cart or increases quantity if it already exists.",
)
def add_cart_item(
    payload: CartItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cart = db.execute(
        select(Cart).where(Cart.user_id == user.id)
    ).scalar_one_or_none()

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    found_cart_item = db.execute(
        select(CartItem)
        .where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == payload.product_id,
        )
    ).scalar_one_or_none()

    if found_cart_item is not None:
        found_cart_item.quantity += payload.quantity
        db.commit()
        db.refresh(found_cart_item)
        return CartItemRead.model_validate(found_cart_item)

    new_cart_item = CartItem(
        cart_id=cart.id,
        product_id=payload.product_id,
        quantity=payload.quantity,
    )
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)

    return CartItemRead.model_validate(new_cart_item)


@router.patch(
    "/items/{item_id}",
    response_model=CartItemRead,
    status_code=status.HTTP_200_OK,
    summary="Update cart item by id",
    description="Replaces cart item data by id with the provided payload.",
)
def update_product(
        item_id: uuid.UUID,
        payload: CartItemUpdate,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    found_cart_item = db.execute(
        select(CartItem)
        .join(Cart, CartItem.cart_id == Cart.id)
        .where(
            CartItem.id == item_id,
            Cart.user_id == user.id,
        )
    ).scalar_one_or_none()

    if found_cart_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    data = payload.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(found_cart_item, field, value)

    db.commit()
    db.refresh(found_cart_item)

    return found_cart_item


@router.post(
    "/apply-promo",
    response_model=CartRead,
    status_code=status.HTTP_200_OK,
    summary="Apply Promo",
    description="Apply SAVE10 promo code to the cart.",
)
def apply_promo(
        payload: ApplyPromoRequest,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    cart = db.execute(
        select(Cart)
        .where(Cart.user_id == user.id)
    ).scalar_one_or_none()

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    discount = get_discount_percentage(payload.code)

    if discount == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Promo code is invalid",
        )

    cart.discount_percentage = discount
    db.commit()
    db.refresh(cart)

    return CartRead.model_validate(cart)


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product from cart",
    description="Deletes a product from cart by id.",
)
def delete_product_from_cart(
        item_id: uuid.UUID,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
):
    found_cart_item = db.execute(
        select(CartItem)
        .join(Cart, CartItem.cart_id == Cart.id)
        .where(
            CartItem.id == item_id,
            Cart.user_id == user.id,
        )
    ).scalar_one_or_none()

    if found_cart_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    db.delete(found_cart_item)
    db.commit()
