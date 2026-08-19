from __future__ import annotations

import enum
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db import Base
from app.models.mixins import TimestampMixin, VersionMixin
from app.models.user import User


class ProductStatus(str, enum.Enum):
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    requires_health_notice: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    subcategories: Mapped[list["Subcategory"]] = relationship(back_populates="category")
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Subcategory(TimestampMixin, Base):
    __tablename__ = "subcategories"
    __table_args__ = (UniqueConstraint("category_id", "slug", name="uq_subcategory_category_slug"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    category_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    slug: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)

    category: Mapped[Category] = relationship(back_populates="subcategories")
    products: Mapped[list["Product"]] = relationship(back_populates="subcategory")


class Product(TimestampMixin, VersionMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("normalized_name", "brand_normalized", name="uq_product_brand_name"),
        CheckConstraint(
            "status IN ('published', 'archived', 'deleted')",
            name="ck_products_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    created_by_user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    category_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    subcategory_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("subcategories.id", ondelete="SET NULL"), index=True
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    normalized_name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    brand_name: Mapped[str] = mapped_column(String(120), nullable=False)
    brand_normalized: Mapped[str] = mapped_column(String(120), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(80))
    website_url: Mapped[str | None] = mapped_column(String(500))
    typical_price_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    typical_price_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="USD")
    release_year: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=ProductStatus.PUBLISHED.value)

    creator: Mapped[User] = relationship()
    category: Mapped[Category] = relationship(back_populates="products")
    subcategory: Mapped[Subcategory | None] = relationship(back_populates="products")
    reviews: Mapped[list["Review"]] = relationship(back_populates="product")
