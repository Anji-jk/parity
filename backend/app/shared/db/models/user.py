from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.db.config.base import Base
from src.shared.db.enums.role import Role


class AppUser(Base):
    __tablename__ = "app_users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    passwordHash: Mapped[str | None] = mapped_column("password_hash", String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    isPhoneVerified: Mapped[bool] = mapped_column(
        "is_phone_verified", Boolean, default=False, nullable=False
    )
    firstName: Mapped[str | None] = mapped_column("first_name", String, nullable=True)
    lastName: Mapped[str | None] = mapped_column("last_name", String, nullable=True)
    userRole: Mapped[Role] = mapped_column("user_role", Enum(Role), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=datetime.utcnow, nullable=False
    )
    updatedAt: Mapped[datetime] = mapped_column(
        "updated_at",
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )