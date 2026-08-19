"""Idempotent local seed. Demonstration data is clearly labeled."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import SessionLocal
from app.domain import normalize_name
from app.models.catalog import Category, Product, ProductStatus, Subcategory
from app.models.platform import BetaConfiguration
from app.models.review import Review, ReviewKind, ReviewState
from app.models.user import InvitationCode, Profile, User, UserStatus
from app.security import hash_password

CATEGORIES = [
    (
        "technology",
        "Technology",
        "Consumer electronics and computing.",
        False,
        10,
        [("headphones", "Headphones"), ("laptops", "Laptops")],
    ),
    (
        "fitness",
        "Fitness",
        "Exercise equipment and accessories.",
        True,
        20,
        [("mats", "Mats"), ("wearables", "Wearables")],
    ),
    ("clothing", "Clothing", "Apparel and everyday wear.", False, 30, [("outerwear", "Outerwear")]),
    ("beauty", "Beauty", "Skincare, hair, and cosmetics.", True, 40, [("skincare", "Skincare")]),
    ("home-goods", "Home goods", "Household products and décor.", False, 50, []),
    (
        "food-and-beverages",
        "Food and beverages",
        "Packaged foods and drinks.",
        True,
        60,
        [("snacks", "Snacks")],
    ),
    ("kitchen", "Kitchen products", "Cookware and kitchen tools.", False, 70, [("kettles", "Kettles")]),
    ("appliances", "Appliances", "Home and kitchen appliances.", False, 80, []),
    (
        "outdoor-equipment",
        "Outdoor equipment",
        "Camping, hiking, and outdoor gear.",
        False,
        90,
        [],
    ),
    ("games", "Games and entertainment", "Games, hobbies, and entertainment products.", False, 100, []),
    ("automotive", "Automotive accessories", "Vehicle accessories and care.", False, 110, []),
    ("general", "General consumer products", "Products that do not fit a more specific category.", False, 120, []),
]


def _user(db: Session, email: str, username: str, password: str, role: str) -> User:
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        return existing
    user = User(
        email=email,
        username=username,
        password_hash=hash_password(password),
        role=role,
        status=UserStatus.ACTIVE.value,
        email_verified_at=datetime.now(UTC),
    )
    db.add(user)
    db.flush()
    db.add(
        Profile(
            user_id=user.id,
            display_name=username,
            biography="Demonstration account for FindShare local development. Not a real person.",
            interests=["technology", "kitchen"],
        )
    )
    return user


def seed(db: Session | None = None) -> None:
    settings = get_settings()
    own_session = db is None
    db = db or SessionLocal()
    try:
        config = db.get(BetaConfiguration, 1)
        if config is None:
            config = BetaConfiguration(
                id=1,
                registration_mode=settings.registration_mode,
                maximum_active_users=settings.maximum_active_users,
                reviews_per_user=settings.reviews_per_user,
                images_per_review=settings.images_per_review,
                maximum_image_size_mb=settings.maximum_image_size_mb,
                registration_enabled=settings.registration_enabled,
                image_uploads_enabled=settings.image_uploads_enabled,
                comments_enabled=settings.comments_enabled,
                price_submissions_enabled=settings.price_submissions_enabled,
                public_collections_enabled=settings.public_collections_enabled,
                placeholder_ads_enabled=settings.placeholder_ads_enabled,
                live_advertising_enabled=settings.live_advertising_enabled,
                advertising_provider=settings.advertising_provider,
                maintenance_mode=settings.maintenance_mode,
            )
            db.add(config)

        admin = _user(
            db,
            settings.seed_admin_email,
            settings.seed_admin_username,
            settings.seed_admin_password,
            "admin",
        )
        _user(
            db,
            settings.seed_moderator_email,
            settings.seed_moderator_username,
            settings.seed_moderator_password,
            "moderator",
        )
        demo = _user(
            db,
            settings.seed_demo_email,
            settings.seed_demo_username,
            settings.seed_demo_password,
            "user",
        )

        invite = db.scalar(select(InvitationCode).where(InvitationCode.code == settings.seed_invitation_code))
        if invite is None:
            db.add(
                InvitationCode(
                    code=settings.seed_invitation_code,
                    created_by_user_id=admin.id,
                    max_uses=25,
                    note="Local development invitation. Demonstration data.",
                )
            )

        categories: dict[str, Category] = {}
        for slug, name, description, health, order, subs in CATEGORIES:
            category = db.scalar(select(Category).where(Category.slug == slug))
            if category is None:
                category = Category(
                    slug=slug,
                    name=name,
                    description=description,
                    requires_health_notice=health,
                    position=order,
                )
                db.add(category)
                db.flush()
            categories[slug] = category
            for sub_slug, sub_name in subs:
                existing_sub = db.scalar(
                    select(Subcategory).where(
                        Subcategory.category_id == category.id, Subcategory.slug == sub_slug
                    )
                )
                if existing_sub is None:
                    db.add(Subcategory(category_id=category.id, slug=sub_slug, name=sub_name))

        db.flush()

        demo_products = [
            {
                "name": "QuietLine Over-Ear Headphones",
                "brand_name": "Harbor Audio",
                "category": "technology",
                "description": (
                    "Demonstration catalog item. Over-ear wireless headphones used in local seed data. "
                    "Not a real commercial listing."
                ),
                "typical_price_min": 79,
                "typical_price_max": 129,
            },
            {
                "name": "Northline Studio Yoga Mat",
                "brand_name": "Northline",
                "category": "fitness",
                "description": (
                    "Demonstration catalog item. A 6mm yoga mat used in local seed data. "
                    "Not a real commercial listing."
                ),
                "typical_price_min": 25,
                "typical_price_max": 45,
            },
            {
                "name": "Harbor Home Cast-Iron Skillet",
                "brand_name": "Harbor Home",
                "category": "kitchen",
                "description": (
                    "Demonstration catalog item. A 12-inch skillet used in local seed data. "
                    "Not a real commercial listing."
                ),
                "typical_price_min": 40,
                "typical_price_max": 70,
            },
        ]

        products: list[Product] = []
        for item in demo_products:
            normalized = normalize_name(item["name"])
            brand_norm = normalize_name(item["brand_name"])
            existing = db.scalar(
                select(Product).where(
                    Product.normalized_name == normalized,
                    Product.brand_normalized == brand_norm,
                )
            )
            if existing:
                products.append(existing)
                continue
            product = Product(
                name=item["name"],
                normalized_name=normalized,
                description=item["description"],
                category_id=categories[item["category"]].id,
                brand_name=item["brand_name"],
                brand_normalized=brand_norm,
                typical_price_min=item["typical_price_min"],
                typical_price_max=item["typical_price_max"],
                currency="USD",
                status=ProductStatus.PUBLISHED.value,
                created_by_user_id=admin.id,
            )
            db.add(product)
            db.flush()
            products.append(product)

        now = datetime.now(UTC)
        if products and db.scalar(select(Review).where(Review.author_id == demo.id)) is None:
            db.add(
                Review(
                    product_id=products[0].id,
                    author_id=demo.id,
                    title="Quiet enough for a noisy office",
                    body=(
                        "This is demonstration seed content, not a real purchase review. "
                        "The headphones isolate office noise well and stay comfortable for a workday. "
                        "Battery life in this fixture is described as lasting through commuting."
                    ),
                    overall_rating=5,
                    pros=["Comfortable fit (demo)", "Clear calls (demo)"],
                    cons=["Case is bulky (demo)"],
                    recommended=True,
                    review_kind=ReviewKind.PERSONAL.value,
                    length_of_ownership="3 months",
                    usage_context="Commuting and desk work",
                    state=ReviewState.PUBLISHED.value,
                    published_at=now,
                )
            )
            db.add(
                Review(
                    product_id=products[0].id,
                    author_id=demo.id,
                    title="Unfinished notes (draft)",
                    body="Demonstration draft that must stay out of the public feed and search.",
                    overall_rating=3,
                    pros=[],
                    cons=[],
                    review_kind=ReviewKind.PERSONAL.value,
                    state=ReviewState.DRAFT.value,
                )
            )
            db.add(
                Review(
                    product_id=products[2].id,
                    author_id=admin.id,
                    title="Even heat across the pan",
                    body=(
                        "This is demonstration seed content, not a real purchase review. "
                        "The skillet holds even heat and is used as a fixture for ownership tests."
                    ),
                    overall_rating=4,
                    pros=["Even heat (demo)"],
                    cons=["Heavy (demo)"],
                    recommended=True,
                    review_kind=ReviewKind.RECOMMENDATION.value,
                    state=ReviewState.PUBLISHED.value,
                    published_at=now,
                )
            )

        db.commit()
    finally:
        if own_session:
            db.close()


def seed_demo(db: Session) -> None:
    seed(db)


def seed_if_needed() -> None:
    seed()


if __name__ == "__main__":
    seed()
