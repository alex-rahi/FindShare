from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import catalog_service, review_service
from app.auth_service import count_active_users, get_beta
from app.db import get_db
from app.models.user import User
from app.schemas import (
    BetaStatus,
    CategoryOut,
    Notices,
    ProductCreate,
    ProductOut,
    ProductUpdate,
    ReviewCreate,
    ReviewOut,
    ReviewUpdate,
)
from app.security import get_current_user_optional, require_verified_user

router = APIRouter(prefix="/api/v1")

GENERAL = (
    "Reviews, ratings, product details, prices, and availability may be submitted by users and may "
    "contain errors. FindShare does not independently guarantee product quality, safety, authenticity, "
    "suitability, or availability. Verify important product information with the manufacturer or "
    "retailer before purchasing or using a product."
)
PRICING = (
    "Prices and availability may vary by retailer, location, product variant, and date. Verify current "
    "pricing and availability with the retailer before purchasing."
)
HEALTH = (
    "User content is not medical, nutritional, health, or safety advice. Consult a qualified professional "
    "when appropriate and follow manufacturer instructions and warnings."
)


@router.get("/categories", response_model=list[CategoryOut])
def categories(db: Session = Depends(get_db)):
    return [catalog_service.category_out(c) for c in catalog_service.list_categories(db)]


@router.get("/categories/{slug}", response_model=CategoryOut)
def category(slug: str, db: Session = Depends(get_db)):
    return catalog_service.category_out(catalog_service.get_category(db, slug))


@router.get("/products")
def products(
    db: Session = Depends(get_db),
    q: str | None = None,
    category: str | None = None,
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    rows, total = catalog_service.list_products(db, q=q, category=category, limit=limit, offset=offset)
    stats = catalog_service.rating_stats(db, [p.id for p in rows])
    return {
        "items": [
            catalog_service.product_out(p, average=stats.get(p.id, (None, 0))[0], review_count=stats.get(p.id, (None, 0))[1])
            for p in rows
        ],
        "limit": limit,
        "offset": offset,
        "total": total,
    }


@router.post("/products", response_model=ProductOut, status_code=201)
def create_product(body: ProductCreate, user: User = Depends(require_verified_user), db: Session = Depends(get_db)):
    product = catalog_service.create_product(db, user, body)
    return catalog_service.product_out(product)


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    product = catalog_service.get_product(db, product_id, user)
    stats = catalog_service.rating_stats(db, [product.id])
    average, count = stats.get(product.id, (None, 0))
    return catalog_service.product_out(product, average=average, review_count=count)


@router.patch("/products/{product_id}", response_model=ProductOut)
def patch_product(
    product_id: UUID,
    body: ProductUpdate,
    user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
):
    return catalog_service.product_out(catalog_service.update_product(db, user, product_id, body))


@router.get("/reviews")
def reviews(
    db: Session = Depends(get_db),
    product_id: UUID | None = None,
    author: str | None = None,
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    rows, total = review_service.list_published(
        db, product_id=product_id, author=author, limit=limit, offset=offset
    )
    return {"items": [review_service.to_out(r) for r in rows], "limit": limit, "offset": offset, "total": total}


@router.post("/reviews", response_model=ReviewOut, status_code=201)
def create_review(body: ReviewCreate, user: User = Depends(require_verified_user), db: Session = Depends(get_db)):
    return review_service.to_out(review_service.create_review(db, user, body))


@router.get("/reviews/{review_id}", response_model=ReviewOut)
def get_review(
    review_id: UUID,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    return review_service.to_out(review_service.get_review(db, review_id, user))


@router.patch("/reviews/{review_id}", response_model=ReviewOut)
def patch_review(
    review_id: UUID,
    body: ReviewUpdate,
    user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
):
    return review_service.to_out(review_service.update_review(db, user, review_id, body))


@router.post("/reviews/{review_id}/publish", response_model=ReviewOut)
def publish_review(review_id: UUID, user: User = Depends(require_verified_user), db: Session = Depends(get_db)):
    return review_service.to_out(review_service.publish_review(db, user, review_id))


@router.delete("/reviews/{review_id}", status_code=204)
def delete_review(review_id: UUID, user: User = Depends(require_verified_user), db: Session = Depends(get_db)):
    review_service.delete_review(db, user, review_id)


@router.get("/feed")
def feed(
    db: Session = Depends(get_db),
    sort: str = "recent",
    category: str | None = None,
    min_rating: int | None = None,
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    rows, total = review_service.list_published(
        db, category=category, min_rating=min_rating, sort=sort, limit=limit, offset=offset
    )
    return {"items": [review_service.to_out(r) for r in rows], "limit": limit, "offset": offset, "total": total}


@router.get("/search")
def search(
    q: str,
    db: Session = Depends(get_db),
    type: str = "all",
    limit: int = Query(20, ge=1, le=50),
):
    result: dict = {"products": [], "reviews": [], "users": []}
    if type in {"all", "product"}:
        products, _ = catalog_service.list_products(db, q=q, limit=limit)
        stats = catalog_service.rating_stats(db, [p.id for p in products])
        result["products"] = [
            catalog_service.product_out(p, average=stats.get(p.id, (None, 0))[0], review_count=stats.get(p.id, (None, 0))[1])
            for p in products
        ]
    if type in {"all", "review"}:
        reviews, _ = review_service.list_published(db, q=q, limit=limit)
        result["reviews"] = [review_service.to_out(r) for r in reviews]
    if type in {"all", "user"}:
        users = review_service.list_users_matching(db, q, limit=limit)
        result["users"] = [
            {
                "username": u.username,
                "display_name": u.profile.display_name if u.profile else None,
            }
            for u in users
        ]
    return result


@router.get("/beta/status", response_model=BetaStatus)
def beta_status(db: Session = Depends(get_db)):
    beta = get_beta(db)
    active = count_active_users(db)
    remaining = max(beta.maximum_active_users - active, 0)
    return BetaStatus(
        registration_mode=beta.registration_mode,
        registration_enabled=beta.registration_enabled,
        maximum_active_users=beta.maximum_active_users,
        active_users=active,
        seats_remaining=remaining,
        maintenance_mode=beta.maintenance_mode,
    )


@router.get("/meta/notices", response_model=Notices)
def notices():
    return Notices(general=GENERAL, pricing=PRICING, health=HEALTH, legal_review_required=True)
