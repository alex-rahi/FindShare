"""Phase 1 initial schema.

Revision ID: 001_initial
Revises:
Create Date: 2026-08-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSONType = sa.JSON


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("username", sa.String(32), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending_verification"),
        sa.Column("email_verified_at", sa.DateTime(timezone=True)),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('user', 'moderator', 'admin')", name="ck_users_role"),
        sa.CheckConstraint(
            "status IN ('pending_verification', 'active', 'suspended', 'deleted')",
            name="ck_users_status",
        ),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "profiles",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("display_name", sa.String(80)),
        sa.Column("biography", sa.String(500)),
        sa.Column("interests", JSONType, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "invitation_codes",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("max_uses", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("use_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("code"),
        sa.CheckConstraint("max_uses > 0", name="ck_invitation_max_uses"),
        sa.CheckConstraint("use_count >= 0", name="ck_invitation_use_count"),
    )
    op.create_index("ix_invitation_codes_code", "invitation_codes", ["code"])

    op.create_table(
        "beta_configurations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("registration_mode", sa.String(32), nullable=False, server_default="invite_only"),
        sa.Column("maximum_active_users", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("reviews_per_user", sa.Integer(), nullable=False, server_default="25"),
        sa.Column("images_per_review", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("maximum_image_size_mb", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("registration_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("image_uploads_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("comments_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("price_submissions_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("public_collections_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("placeholder_ads_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("live_advertising_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("advertising_provider", sa.String(32), nullable=False, server_default="mock"),
        sa.Column("maintenance_mode", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("requires_health_notice", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"])

    op.create_table(
        "subcategories",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "category_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("categories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("category_id", "slug", name="uq_subcategory_category_slug"),
    )
    op.create_index("ix_subcategories_category_id", "subcategories", ["category_id"])
    op.create_index("ix_subcategories_slug", "subcategories", ["slug"])

    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "created_by_user_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "category_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("categories.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("subcategory_id", sa.Uuid(as_uuid=True), sa.ForeignKey("subcategories.id", ondelete="SET NULL")),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("normalized_name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("brand_name", sa.String(120), nullable=False),
        sa.Column("brand_normalized", sa.String(120), nullable=False),
        sa.Column("model_version", sa.String(80)),
        sa.Column("website_url", sa.String(500)),
        sa.Column("typical_price_min", sa.Numeric(12, 2)),
        sa.Column("typical_price_max", sa.Numeric(12, 2)),
        sa.Column("currency", sa.String(8), nullable=False, server_default="USD"),
        sa.Column("release_year", sa.Integer()),
        sa.Column("status", sa.String(32), nullable=False, server_default="published"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('published', 'archived', 'deleted')", name="ck_products_status"),
        sa.UniqueConstraint("normalized_name", "brand_normalized", name="uq_product_brand_name"),
    )
    op.create_index("ix_products_created_by_user_id", "products", ["created_by_user_id"])
    op.create_index("ix_products_category_id", "products", ["category_id"])
    op.create_index("ix_products_subcategory_id", "products", ["subcategory_id"])
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_normalized_name", "products", ["normalized_name"])

    op.create_table(
        "reviews",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "product_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "author_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("overall_rating", sa.Integer(), nullable=False),
        sa.Column("pros", JSONType, nullable=False),
        sa.Column("cons", JSONType, nullable=False),
        sa.Column("recommended", sa.Boolean()),
        sa.Column("review_kind", sa.String(32), nullable=False, server_default="personal"),
        sa.Column("length_of_ownership", sa.String(32)),
        sa.Column("usage_context", sa.String(200)),
        sa.Column("purchase_date", sa.Date()),
        sa.Column("state", sa.String(32), nullable=False, server_default="draft"),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("overall_rating >= 1 AND overall_rating <= 5", name="ck_reviews_rating"),
        sa.CheckConstraint(
            "state IN ('draft', 'pending_moderation', 'needs_review', 'published', "
            "'rejected', 'archived', 'deleted')",
            name="ck_reviews_state",
        ),
    )
    op.create_index("ix_reviews_product_id", "reviews", ["product_id"])
    op.create_index("ix_reviews_author_id", "reviews", ["author_id"])
    op.create_index("ix_reviews_title", "reviews", ["title"])
    op.create_index("ix_reviews_state", "reviews", ["state"])
    op.create_index("ix_reviews_published_at", "reviews", ["published_at"])

    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("actor_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("resource_type", sa.String(32)),
        sa.Column("resource_id", sa.String(64)),
        sa.Column("extra", JSONType),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_events_actor_id", "audit_events", ["actor_id"])
    op.create_index("ix_audit_events_action", "audit_events", ["action"])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("reviews")
    op.drop_table("products")
    op.drop_table("subcategories")
    op.drop_table("categories")
    op.drop_table("beta_configurations")
    op.drop_table("invitation_codes")
    op.drop_table("profiles")
    op.drop_table("users")
