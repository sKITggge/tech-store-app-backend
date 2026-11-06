from app.db.base import Base
from app.db.session import engine

from app.models.image import Image  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.cart import Cart  # noqa: F401
from app.models.user import User  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
