import math
import uuid
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, or_

from app.auth.deps import require_admin
from app.core.enums import SortBy, Order
from app.db.deps import get_db
from app.models.image import Image
from app.models.product import Product
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.schemas.product import ProductRead, ProductCreate, ProductUpdate
from app.utils.sql import escape_like

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.get(
    "",
    response_model=PaginatedResponse,
    status_code=status.HTTP_200_OK,
    summary="Get products",
    description="Returns paginated list of products with search, filters and sorting.",
)
def get_products(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        search: str | None = None,
        min_price: Decimal = Query(0, ge=0),
        max_price: Decimal = Query(99999999, ge=0),
        min_rating: float = Query(0, ge=0, le=5),
        sort_by: SortBy = SortBy.title,
        order: Order = Order.asc,
        db: Session = Depends(get_db),
):
    query = select(Product).where(
        Product.price.between(min_price, max_price),
        Product.rating >= min_rating,
    )

    if search:
        pattern = f"%{escape_like(search)}%"
        query = query.where(
            or_(
                Product.title.ilike(pattern, escape="\\"),
                Product.description.ilike(pattern, escape="\\"),
            )
        )

    sort_column = {
        SortBy.title: Product.title,
        SortBy.price: Product.price,
    }[sort_by]

    if order == Order.asc:
        query = query.order_by(sort_column.asc(), Product.id.asc())
    else:
        query = query.order_by(sort_column.desc(), Product.id.asc())

    count_query = select(func.count()).select_from(query.order_by(None).subquery())
    total_items = db.execute(count_query).scalar_one()

    products = db.execute(
        query.options(selectinload(Product.images))
        .limit(limit)
        .offset((page - 1) * limit)
    ).scalars().all()

    total_pages = math.ceil(total_items / limit) if total_items > 0 else 1

    return PaginatedResponse(
        items=[ProductRead.model_validate(product) for product in products],
        meta=PaginationMeta(
            total_items=total_items,
            total_pages=total_pages,
            current_page=page,
            limit=limit,
        ),
    )


@router.get(
    "/{product_id}",
    response_model=ProductRead,
    status_code=status.HTTP_200_OK,
    summary="Get product by id",
)
def get_product(
        product_id: uuid.UUID,
        db: Session = Depends(get_db),
):
    product = db.execute(
        select(Product).where(Product.id == product_id)
    ).scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return ProductRead.model_validate(product)


@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add product",
    dependencies=[Depends(require_admin)]
)
def add_product(
        item: ProductCreate,
        db: Session = Depends(get_db)
):
    product = Product(
        title=item.title,
        description=item.description,
        price=item.price,
        rating=item.rating,
        stock_quantity=item.stock_quantity,
        images=[Image(url=image.url) for image in item.images],
    )
    db.add(product)
    db.flush()
    db.refresh(product)

    return ProductRead.model_validate(product)


@router.patch(
    "/{product_id}",
    response_model=ProductRead,
    status_code=status.HTTP_200_OK,
    summary="Update product",
    description="Patches product data by id with the provided payload.",
    dependencies=[Depends(require_admin)]
)
def update_product(
        product_id: uuid.UUID,
        payload: ProductUpdate,
        db: Session = Depends(get_db)
):
    found_product = db.execute(
        select(Product).where(Product.id == product_id)
    ).scalar_one_or_none()

    if found_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    data = payload.model_dump(exclude_unset=True)
    images = data.pop("images", None)

    for field, value in data.items():
        if value is not None:
            setattr(found_product, field, value)

    if images is not None:
        found_product.images = [Image(url=image["url"]) for image in images]

    db.flush()
    db.refresh(found_product)

    return ProductRead.model_validate(found_product)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product",
    description="Hard delete a product by id.",
    dependencies=[Depends(require_admin)]
)
def delete_product(
        product_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    found_product = db.execute(
        select(Product).where(Product.id == product_id)
    ).scalar_one_or_none()

    if found_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.delete(found_product)
