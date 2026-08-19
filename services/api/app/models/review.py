import enum
from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from app.db import Base
from app.models.catalog import Product
from app.models.mixins import TimestampMixin, VersionMixin
from app.models.user import User


class ReviewState(str, enum.Enum):
    DRAFT = "draft"
    PENDING_MODERATION = "pending_moderation"
    NEEDS_REVIEW = "needs_review"
    PUBLISHED = "published"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ReviewKind(str, enum.Enum):
    PERSONAL = "personal"
    RECOMMENDATION = "recommendation"
    FIRST_IMPRESSION = "first_impression"
    LONG_TERM = "long_term"
    COMPARISON = "comparison"
    QUESTION = "question"


class Review(TimestampMixin, VersionMixin, Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("overall_rating >= 1 AND overall_rating <= 5", name="ck_reviews_rating"),
        CheckConstraint(
            "state IN ('draft', 'pending_moderation', 'needs_review', 'published', "
            "'rejected', 'archived', 'deleted')",
            name="ck_reviews_state",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    author_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    overall_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    pros: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    cons: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    recommended: Mapped[bool | None] = mapped_column(Boolean)
    review_kind: Mapped[str] = mapped_column(String(32), nullable=False, default=ReviewKind.PERSONAL.value)
    length_of_ownership: Mapped[str | None] = mapped_column(String(32))
    usage_context: Mapped[str | None] = mapped_column(String(200))
    purchase_date: Mapped[date | None] = mapped_column(Date)
    state: Mapped[str] = mapped_column(String(32), nullable=False, default=ReviewState.DRAFT.value, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    product: Mapped[Product] = relationship(back_populates="reviews")
    author: Mapped[User] = relationship()
