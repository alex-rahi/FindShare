from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RegisterIn(BaseModel):
    email: EmailStr
    username: str
    password: str
    invitation_code: str | None = None


class LoginIn(BaseModel):
    email_or_username: str
    password: str


class TokenPair(APIModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserOut(APIModel):
    id: UUID
    email: str
    username: str
    role: str
    status: str
    email_verified_at: datetime | None = None


class ProfileOut(APIModel):
    username: str
    display_name: str | None = None
    biography: str | None = None
    interests: list[str] = Field(default_factory=list)


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(None, max_length=80)
    biography: str | None = Field(None, max_length=500)
    interests: list[str] | None = None


class AuthMeOut(APIModel):
    user: UserOut
    profile: ProfileOut | None = None


class RegisterOut(APIModel):
    user: UserOut
    tokens: TokenPair
    email_verification_required: bool = True
    local_verify_token: str | None = None


class VerifyIn(BaseModel):
    token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetOut(APIModel):
    detail: str
    code: str = "ACCEPTED"
    local_reset_token: str | None = None


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class SubcategoryOut(APIModel):
    id: UUID
    name: str
    slug: str


class CategoryOut(APIModel):
    id: UUID
    name: str
    slug: str
    description: str | None = None
    requires_health_notice: bool = False
    subcategories: list[SubcategoryOut] = Field(default_factory=list)


class AuthorOut(APIModel):
    id: UUID | None = None
    username: str
    display_name: str | None = None


class ProductRef(APIModel):
    id: UUID
    name: str
    brand_name: str
    category: CategoryOut


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    category_id: UUID
    subcategory_id: UUID | None = None
    brand_name: str = Field(min_length=1, max_length=120)
    model_version: str | None = None
    website_url: str | None = None
    typical_price_min: Decimal | None = None
    typical_price_max: Decimal | None = None
    currency: str = "USD"
    release_year: int | None = Field(default=None, ge=1900, le=2100)

    @field_validator("typical_price_min", "typical_price_max")
    @classmethod
    def non_negative(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and value < 0:
            raise ValueError("Prices cannot be negative")
        if value is not None and value > Decimal("10000000"):
            raise ValueError("Price is implausibly large")
        return value

    @field_validator("currency")
    @classmethod
    def currency_ok(cls, value: str) -> str:
        allowed = {"USD", "CAD", "EUR", "GBP"}
        upper = value.upper()
        if upper not in allowed:
            raise ValueError("Unsupported currency")
        return upper


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: UUID | None = None
    subcategory_id: UUID | None = None
    brand_name: str | None = None
    model_version: str | None = None
    website_url: str | None = None
    typical_price_min: Decimal | None = None
    typical_price_max: Decimal | None = None
    currency: str | None = None
    release_year: int | None = None
    status: str | None = None
    version: int | None = None

    @field_validator("typical_price_min", "typical_price_max")
    @classmethod
    def non_negative(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and value < 0:
            raise ValueError("Prices cannot be negative")
        if value is not None and value > Decimal("10000000"):
            raise ValueError("Price is implausibly large")
        return value


class ProductOut(APIModel):
    id: UUID
    name: str
    description: str | None = None
    brand_name: str
    model_version: str | None = None
    website_url: str | None = None
    typical_price_min: Decimal | None = None
    typical_price_max: Decimal | None = None
    currency: str
    release_year: int | None = None
    status: str
    category: CategoryOut
    subcategory: SubcategoryOut | None = None
    created_by: AuthorOut
    average_rating: float | None = None
    review_count: int = 0
    created_at: datetime | None = None


class ReviewCreate(BaseModel):
    product_id: UUID
    title: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=20000)
    overall_rating: int = Field(ge=1, le=5)
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    recommended: bool | None = None
    review_kind: str = "personal"
    length_of_ownership: str | None = None
    usage_context: str | None = Field(None, max_length=200)
    purchase_date: date | None = None
    publish: bool = False

    @field_validator("review_kind")
    @classmethod
    def kind_ok(cls, value: str) -> str:
        allowed = {
            "personal",
            "recommendation",
            "first_impression",
            "long_term",
            "comparison",
            "question",
        }
        if value not in allowed:
            raise ValueError("Invalid review kind")
        return value


class ReviewUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    overall_rating: int | None = Field(default=None, ge=1, le=5)
    pros: list[str] | None = None
    cons: list[str] | None = None
    recommended: bool | None = None
    review_kind: str | None = None
    length_of_ownership: str | None = None
    usage_context: str | None = None
    purchase_date: date | None = None
    version: int | None = None


class ReviewOut(APIModel):
    id: UUID
    product: ProductRef
    author: AuthorOut
    title: str
    body: str
    overall_rating: int
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    recommended: bool | None = None
    review_kind: str
    length_of_ownership: str | None = None
    usage_context: str | None = None
    purchase_date: date | None = None
    state: str
    published_at: datetime | None = None
    created_at: datetime | None = None


class BetaStatus(APIModel):
    registration_mode: str
    registration_enabled: bool
    maximum_active_users: int
    active_users: int
    seats_remaining: int
    maintenance_mode: bool


class Notices(APIModel):
    general: str
    pricing: str
    health: str
    legal_review_required: bool = True


class FeatureFlags(APIModel):
    registration_mode: str
    registration_enabled: bool
    image_uploads_enabled: bool
    comments_enabled: bool
    price_submissions_enabled: bool
    public_collections_enabled: bool
    placeholder_ads_enabled: bool
    live_advertising_enabled: bool
    advertising_provider: str
    maintenance_mode: bool
    reviews_per_user: int
    images_per_review: int
    maximum_image_size_mb: int
