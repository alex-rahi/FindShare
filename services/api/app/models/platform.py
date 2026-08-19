from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON, Uuid

from app.db import Base
from app.models.mixins import TimestampMixin


class BetaConfiguration(TimestampMixin, Base):
    __tablename__ = "beta_configurations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    registration_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="invite_only")
    maximum_active_users: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    reviews_per_user: Mapped[int] = mapped_column(Integer, nullable=False, default=25)
    images_per_review: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    maximum_image_size_mb: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    registration_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    image_uploads_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    comments_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    price_submissions_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    public_collections_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    placeholder_ads_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    live_advertising_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    advertising_provider: Mapped[str] = mapped_column(String(32), nullable=False, default="mock")
    maintenance_mode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class AuditEvent(TimestampMixin, Base):
    __tablename__ = "audit_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    actor_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    action: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    resource_type: Mapped[str | None] = mapped_column(String(32))
    resource_id: Mapped[str | None] = mapped_column(String(64))
    extra: Mapped[dict | None] = mapped_column(JSON)
