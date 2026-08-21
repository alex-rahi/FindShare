from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.auth_service import get_beta
from app.domain import can_publish_text_review, is_public_review_state
from app.errors import AppError
from app.models.catalog import Category, Product, ProductStatus
from app.models.review import Review, ReviewState
from app.models.user import Profile, User, UserRole, UserStatus
from app.schemas import (
    AuthorOut,
    CategoryOut,
    ProductRef,
    ReviewCreate,
    ReviewOut,
    ReviewUpdate,
)


def _eager():
    return (
        selectinload(Review.author).selectinload(User.profile),
        selectinload(Review.product).selectinload(Product.category),
        selectinload(Review.product).selectinload(Product.subcategory),
    )


def _author(user: User) -> AuthorOut:
    display = user.profile.display_name if user.profile else None
    return AuthorOut(id=user.id, username=user.username, display_name=display)


def _product_ref(product: Product) -> ProductRef:
    return ProductRef(
        id=product.id,
        name=product.name,
        brand_name=product.brand_name,
        category=CategoryOut(
            id=product.category.id,
            name=product.category.name,
            slug=product.category.slug,
            description=product.category.description,
            requires_health_notice=product.category.requires_health_notice,
            subcategories=[],
        ),
    )


def to_out(review: Review) -> ReviewOut:
    return ReviewOut(
        id=review.id,
        product=_product_ref(review.product),
        author=_author(review.author),
        title=review.title,
        body=review.body,
        overall_rating=review.overall_rating,
        pros=list(review.pros or []),
        cons=list(review.cons or []),
        recommended=review.recommended,
        review_kind=review.review_kind,
        length_of_ownership=review.length_of_ownership,
        usage_context=review.usage_context,
        purchase_date=review.purchase_date,
        state=review.state,
        published_at=review.published_at,
        created_at=review.created_at,
    )


def create_review(db: Session, user: User, data: ReviewCreate) -> Review:
    beta = get_beta(db)
    count = db.scalar(
        select(func.count())
        .select_from(Review)
        .where(Review.author_id == user.id, Review.state != ReviewState.DELETED)
    )
    if int(count or 0) >= beta.reviews_per_user:
        raise AppError("REVIEW_QUOTA", "Review quota for this account has been reached.", 403)
    product = db.get(Product, data.product_id)
    if product is None or product.status != ProductStatus.PUBLISHED:
        raise AppError("NOT_FOUND", "Product not found.", 404)
    review = Review(
        product_id=product.id,
        author_id=user.id,
        title=data.title.strip(),
        body=data.body.strip(),
        overall_rating=data.overall_rating,
        pros=[p.strip() for p in data.pros if p.strip()],
        cons=[c.strip() for c in data.cons if c.strip()],
        recommended=data.recommended,
        review_kind=data.review_kind,
        length_of_ownership=data.length_of_ownership,
        usage_context=data.usage_context,
        purchase_date=data.purchase_date,
        state=ReviewState.DRAFT.value,
    )
    db.add(review)
    db.flush()
    if data.publish:
        _publish(review)
    db.commit()
    return get_review(db, review.id, user)


def get_review(db: Session, review_id: UUID, viewer: User | None) -> Review:
    review = db.scalar(select(Review).options(*_eager()).where(Review.id == review_id))
    if review is None or review.state == ReviewState.DELETED:
        raise AppError("NOT_FOUND", "Review not found.", 404)
    if is_public_review_state(review.state):
        if review.author.status != UserStatus.ACTIVE:
            raise AppError("NOT_FOUND", "Review not found.", 404)
        return review
    if viewer is None or (viewer.id != review.author_id and viewer.role != UserRole.ADMIN):
        raise AppError("NOT_FOUND", "Review not found.", 404)
    return review


def update_review(db: Session, viewer: User, review_id: UUID, data: ReviewUpdate) -> Review:
    review = get_review(db, review_id, viewer)
    if viewer.id != review.author_id and viewer.role != UserRole.ADMIN:
        raise AppError("FORBIDDEN", "You may only modify your own resources.", 403)
    if data.version is not None and data.version != review.version:
        raise AppError("VERSION_CONFLICT", "This review was updated by someone else.", 409)
    fields = data.model_dump(exclude_unset=True, exclude={"version"})
    if review.state == ReviewState.PUBLISHED and fields:
        review.state = ReviewState.DRAFT.value
        review.published_at = None
    for key, value in fields.items():
        setattr(review, key, value)
    review.version += 1
    db.commit()
    return get_review(db, review.id, viewer)


def _publish(review: Review) -> None:
    if review.state == ReviewState.DELETED.value:
        raise AppError("NOT_FOUND", "Review not found.", 404)
    if not can_publish_text_review(title=review.title, body=review.body, rating=review.overall_rating):
        raise AppError("CANNOT_PUBLISH", "Review needs a title, body, and rating before it can be published.", 403)
    review.state = ReviewState.PUBLISHED.value
    review.published_at = datetime.now(UTC)


def publish_review(db: Session, viewer: User, review_id: UUID) -> Review:
    review = get_review(db, review_id, viewer)
    if viewer.id != review.author_id and viewer.role != UserRole.ADMIN:
        raise AppError("FORBIDDEN", "You may only modify your own resources.", 403)
    _publish(review)
    db.commit()
    return get_review(db, review.id, viewer)


def archive_review(db: Session, viewer: User, review_id: UUID) -> Review:
    review = get_review(db, review_id, viewer)
    if viewer.id != review.author_id and viewer.role != UserRole.ADMIN:
        raise AppError("FORBIDDEN", "You may only modify your own resources.", 403)
    if review.state not in {ReviewState.PUBLISHED.value, ReviewState.DRAFT.value}:
        raise AppError("CANNOT_ARCHIVE", "Only draft or published reviews can be archived.", 403)
    review.state = ReviewState.ARCHIVED.value
    review.published_at = None
    review.version += 1
    db.commit()
    return get_review(db, review.id, viewer)


def delete_review(db: Session, viewer: User, review_id: UUID) -> None:
    review = get_review(db, review_id, viewer)
    if viewer.id != review.author_id and viewer.role != UserRole.ADMIN:
        raise AppError("FORBIDDEN", "You may only modify your own resources.", 403)
    review.state = ReviewState.DELETED.value
    review.deleted_at = datetime.now(UTC)
    db.commit()


def list_published(
    db: Session,
    *,
    q: str | None = None,
    category: str | None = None,
    product_id: UUID | None = None,
    author: str | None = None,
    min_rating: int | None = None,
    sort: str = "recent",
    limit: int = 20,
    offset: int = 0,
):
    stmt = (
        select(Review)
        .options(*_eager())
        .join(User, User.id == Review.author_id)
        .join(Product, Product.id == Review.product_id)
        .join(Category, Category.id == Product.category_id)
        .where(
            Review.state == ReviewState.PUBLISHED,
            User.status == UserStatus.ACTIVE,
            Product.status == ProductStatus.PUBLISHED,
        )
    )
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Review.title.ilike(like),
                Review.body.ilike(like),
                Product.name.ilike(like),
                Product.brand_name.ilike(like),
                User.username.ilike(like),
            )
        )
    if category:
        stmt = stmt.where(Category.slug == category.strip().lower())
    if product_id:
        stmt = stmt.where(Review.product_id == product_id)
    if author:
        stmt = stmt.where(User.username == author.strip())
    if min_rating is not None:
        stmt = stmt.where(Review.overall_rating >= min_rating)
    if sort in {"popular", "highest_rated"}:
        stmt = stmt.order_by(Review.overall_rating.desc(), Review.published_at.desc())
    else:
        stmt = stmt.order_by(Review.published_at.desc())
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = list(db.scalars(stmt.limit(limit).offset(offset)).unique().all())
    return rows, int(total or 0)


def list_users_matching(db: Session, q: str, limit: int = 20):
    like = f"%{q.strip()}%"
    return list(
        db.scalars(
            select(User)
            .options(selectinload(User.profile))
            .outerjoin(Profile, Profile.user_id == User.id)
            .where(
                User.status == UserStatus.ACTIVE,
                or_(User.username.ilike(like), Profile.display_name.ilike(like)),
            )
            .limit(limit)
        )
        .unique()
        .all()
    )


def list_mine(db: Session, user: User, *, limit: int = 20, offset: int = 0):
    stmt = (
        select(Review)
        .options(*_eager())
        .where(Review.author_id == user.id, Review.state != ReviewState.DELETED)
        .order_by(Review.updated_at.desc())
    )
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = list(db.scalars(stmt.limit(limit).offset(offset)).unique().all())
    return rows, int(total or 0)
