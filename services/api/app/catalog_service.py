from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.domain import average_rating, normalize_name
from app.errors import AppError
from app.models.catalog import Category, Product, ProductStatus, Subcategory
from app.models.review import Review, ReviewState
from app.models.user import User, UserRole, UserStatus
from app.schemas import AuthorOut, CategoryOut, ProductCreate, ProductOut, ProductUpdate, SubcategoryOut


def category_out(category: Category, *, children: bool = True) -> CategoryOut:
    subs = []
    if children:
        subs = [SubcategoryOut.model_validate(s) for s in sorted(category.subcategories, key=lambda s: s.name)]
    return CategoryOut(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        requires_health_notice=category.requires_health_notice,
        subcategories=subs,
    )


def author_out(user: User) -> AuthorOut:
    display = user.profile.display_name if user.profile else None
    return AuthorOut(id=user.id, username=user.username, display_name=display)


def _eager():
    return (
        selectinload(Product.category).selectinload(Category.subcategories),
        selectinload(Product.subcategory),
        selectinload(Product.creator).selectinload(User.profile),
    )


def product_out(product: Product, *, average: float | None = None, review_count: int = 0) -> ProductOut:
    return ProductOut(
        id=product.id,
        name=product.name,
        description=product.description,
        brand_name=product.brand_name,
        model_version=product.model_version,
        website_url=product.website_url,
        typical_price_min=product.typical_price_min,
        typical_price_max=product.typical_price_max,
        currency=product.currency,
        release_year=product.release_year,
        status=product.status,
        category=category_out(product.category, children=False),
        subcategory=SubcategoryOut.model_validate(product.subcategory) if product.subcategory else None,
        created_by=author_out(product.creator),
        average_rating=average,
        review_count=review_count,
        created_at=product.created_at,
    )


def list_categories(db: Session) -> list[Category]:
    return list(
        db.scalars(select(Category).options(selectinload(Category.subcategories)).order_by(Category.position)).all()
    )


def get_category(db: Session, slug: str) -> Category:
    category = db.scalar(
        select(Category).options(selectinload(Category.subcategories)).where(Category.slug == slug)
    )
    if category is None:
        raise AppError("NOT_FOUND", "Category not found.", 404)
    return category


def create_product(db: Session, user: User, data: ProductCreate) -> Product:
    category = db.get(Category, data.category_id)
    if category is None:
        raise AppError("NOT_FOUND", "Category not found.", 404)
    sub = None
    if data.subcategory_id:
        sub = db.get(Subcategory, data.subcategory_id)
        if sub is None or sub.category_id != category.id:
            raise AppError("INVALID_SUBCATEGORY", "Subcategory does not belong to that category.", 422)
    normalized = normalize_name(data.name)
    brand_norm = normalize_name(data.brand_name)
    existing = db.scalar(
        select(Product).where(
            Product.normalized_name == normalized,
            Product.brand_normalized == brand_norm,
            Product.status != ProductStatus.DELETED,
        )
    )
    if existing:
        raise AppError("DUPLICATE_PRODUCT", "A product with that brand and name already exists.", 409)
    product = Product(
        created_by_user_id=user.id,
        category_id=category.id,
        subcategory_id=sub.id if sub else None,
        name=data.name.strip(),
        normalized_name=normalized,
        description=data.description,
        brand_name=data.brand_name.strip(),
        brand_normalized=brand_norm,
        model_version=data.model_version,
        website_url=data.website_url,
        typical_price_min=data.typical_price_min,
        typical_price_max=data.typical_price_max,
        currency=data.currency,
        release_year=data.release_year,
        status=ProductStatus.PUBLISHED.value,
    )
    db.add(product)
    db.commit()
    return get_product(db, product.id, user)


def get_product(db: Session, product_id: UUID, viewer: User | None) -> Product:
    product = db.scalar(select(Product).options(*_eager()).where(Product.id == product_id))
    if product is None or product.status == ProductStatus.DELETED:
        raise AppError("NOT_FOUND", "Product not found.", 404)
    if product.status != ProductStatus.PUBLISHED:
        if viewer is None or (viewer.id != product.created_by_user_id and viewer.role != UserRole.ADMIN):
            raise AppError("NOT_FOUND", "Product not found.", 404)
    return product


def update_product(db: Session, viewer: User, product_id: UUID, data: ProductUpdate) -> Product:
    product = get_product(db, product_id, viewer)
    if viewer.id != product.created_by_user_id and viewer.role != UserRole.ADMIN:
        raise AppError("FORBIDDEN", "You may only modify your own resources.", 403)
    if data.version is not None and data.version != product.version:
        raise AppError("VERSION_CONFLICT", "This product was updated by someone else.", 409)
    fields = data.model_dump(exclude_unset=True, exclude={"version"})
    if "name" in fields and fields["name"]:
        product.name = fields["name"].strip()
        product.normalized_name = normalize_name(product.name)
    if "brand_name" in fields and fields["brand_name"]:
        product.brand_name = fields["brand_name"].strip()
        product.brand_normalized = normalize_name(product.brand_name)
    if "category_id" in fields and fields["category_id"]:
        if db.get(Category, fields["category_id"]) is None:
            raise AppError("NOT_FOUND", "Category not found.", 404)
        product.category_id = fields["category_id"]
    if "subcategory_id" in fields:
        product.subcategory_id = fields["subcategory_id"]
    for key in (
        "description",
        "model_version",
        "website_url",
        "typical_price_min",
        "typical_price_max",
        "currency",
        "release_year",
    ):
        if key in fields:
            setattr(product, key, fields[key])
    if fields.get("status") in {ProductStatus.PUBLISHED.value, ProductStatus.ARCHIVED.value}:
        product.status = fields["status"]
    product.version += 1
    db.commit()
    return get_product(db, product.id, viewer)


def list_products(db: Session, *, q: str | None = None, category: str | None = None, limit: int = 20, offset: int = 0):
    stmt = (
        select(Product)
        .options(*_eager())
        .join(Category, Category.id == Product.category_id)
        .where(Product.status == ProductStatus.PUBLISHED)
    )
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Product.name.ilike(like), Product.brand_name.ilike(like)))
    if category:
        stmt = stmt.where(Category.slug == category.strip().lower())
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = list(db.scalars(stmt.order_by(Product.created_at.desc()).limit(limit).offset(offset)).unique().all())
    return rows, int(total or 0)


def rating_stats(db: Session, product_ids: list[UUID]) -> dict[UUID, tuple[float | None, int]]:
    if not product_ids:
        return {}
    rows = db.execute(
        select(Review.product_id, Review.overall_rating)
        .join(User, User.id == Review.author_id)
        .where(
            Review.product_id.in_(product_ids),
            Review.state == ReviewState.PUBLISHED,
            User.status == UserStatus.ACTIVE,
        )
    ).all()
    grouped: dict[UUID, list[int]] = {pid: [] for pid in product_ids}
    for product_id, rating in rows:
        grouped.setdefault(product_id, []).append(int(rating))
    out = {}
    for pid, scores in grouped.items():
        avg = average_rating(scores)
        out[pid] = (float(avg) if avg is not None else None, len(scores))
    return out
