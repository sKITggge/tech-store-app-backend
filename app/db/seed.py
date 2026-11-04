from sqlalchemy import select

from app.core.config import settings
from app.core.enums import UserRole
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.cart import Cart
from app.models.user import User


def seed_admin() -> None:
    if not settings.admin_email or not settings.admin_password:
        return

    email = settings.admin_email.lower()

    with SessionLocal() as db:
        existing = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if existing is not None:
            return

        admin = User(
            email=email,
            password_hash=hash_password(settings.admin_password),
            role=UserRole.ADMIN,
        )
        admin.cart = Cart()
        db.add(admin)
        db.commit()
