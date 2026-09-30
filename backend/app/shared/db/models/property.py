import uuid
from datetime import datetime
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.db.config.base import Base
from app.shared.db.enums.verification import VerificationStatus


def generate_uuid() -> str:
    return str(uuid.uuid4())


# class SubscriptionPlan(Base):
#     __tablename__ = "subscription_plans"

#     id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
#     name: Mapped[str] = mapped_column(String(100), nullable=False)
#     max_spaces: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
#     max_workers: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
#     ai_analysis_frequency: Mapped[str | None] = mapped_column(String(100), nullable=True)
#     price_monthly: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("app_users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(100), default="UTC", nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, native_enum=False), default=VerificationStatus.PENDING, nullable=False
    )
    # subscription_plan_id: Mapped[str | None] = mapped_column(
    #     String(36), ForeignKey("subscription_plans.id"), nullable=True, index=True
    # )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)