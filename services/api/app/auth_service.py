from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.errors import AppError
from app.models.platform import AuditEvent, BetaConfiguration
from app.models.review import Review, ReviewState
from app.models.user import InvitationCode, Profile, User, UserRole, UserStatus
from app.schemas import ProfileOut, TokenPair, UserOut
from app.security import create_token, hash_password, validate_password, validate_username, verify_password
from app.tokens import (
    consume_email_token,
    consume_reset_token,
    deny_jti,
    maybe_log_local_token,
    store_email_token,
    store_reset_token,
)


def get_beta(db: Session) -> BetaConfiguration:
    row = db.get(BetaConfiguration, 1)
    if row is None:
        settings = get_settings()
        row = BetaConfiguration(
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
        db.add(row)
        db.flush()
    return row


def count_active_users(db: Session) -> int:
    return int(
        db.scalar(
            select(func.count()).select_from(User).where(User.status.in_((UserStatus.ACTIVE, UserStatus.PENDING_VERIFICATION)))
        )
        or 0
    )


def audit(db: Session, actor_id: UUID | None, action: str, **kwargs) -> None:
    db.add(
        AuditEvent(
            actor_id=actor_id,
            action=action,
            resource_type=kwargs.pop("resource_type", None),
            resource_id=kwargs.pop("resource_id", None),
            extra=kwargs or None,
        )
    )


def user_out(user: User) -> UserOut:
    return UserOut.model_validate(user)


def profile_out(user: User) -> ProfileOut | None:
    if user.profile is None:
        return None
    return ProfileOut(
        username=user.username,
        display_name=user.profile.display_name,
        biography=user.profile.biography,
        interests=list(user.profile.interests or []),
    )


def issue_tokens(user: User) -> TokenPair:
    settings = get_settings()
    access, _jti, _exp = create_token(user.id, "access", settings, extra={"role": user.role})
    return TokenPair(access_token=access, expires_in=settings.jwt_access_ttl_minutes * 60)


def register_user(db: Session, *, email: str, username: str, password: str, invitation_code: str | None) -> tuple[User, str]:
    settings = get_settings()
    beta = get_beta(db)
    validate_username(username)
    validate_password(password)
    email_norm = email.strip().lower()

    if beta.maintenance_mode:
        raise AppError("MAINTENANCE", "FindShare is in maintenance mode.", 503)
    if not beta.registration_enabled or beta.registration_mode == "closed":
        raise AppError("REGISTRATION_CLOSED", "Registration is closed.", 403)
    if beta.registration_mode == "invite_only":
        if not invitation_code:
            raise AppError("INVITE_REQUIRED", "An invitation code is required.", 403)
        invite = db.scalar(select(InvitationCode).where(InvitationCode.code == invitation_code.strip()))
        now = datetime.now(UTC)
        if (
            invite is None
            or invite.revoked_at is not None
            or (invite.expires_at is not None and invite.expires_at < now)
            or invite.use_count >= invite.max_uses
        ):
            raise AppError("INVALID_INVITE", "Invitation code is invalid or expired.", 403)
    else:
        invite = None

    if beta.registration_mode == "invite_only" and count_active_users(db) >= beta.maximum_active_users:
        raise AppError("BETA_FULL", "This invitation-only beta is at capacity.", 403)

    if db.scalar(select(User).where(User.email == email_norm)):
        raise AppError("EMAIL_TAKEN", "An account with that email already exists.", 409)
    if db.scalar(select(User).where(User.username == username)):
        raise AppError("USERNAME_TAKEN", "That username is taken.", 409)

    user = User(
        email=email_norm,
        username=username,
        password_hash=hash_password(password),
        role=UserRole.USER.value,
        status=UserStatus.PENDING_VERIFICATION.value,
    )
    db.add(user)
    db.flush()
    db.add(Profile(user_id=user.id, display_name=username, interests=[]))
    if invite is not None:
        invite.use_count += 1
    raw = store_email_token(str(user.id))
    audit(db, user.id, "user.register")
    db.commit()
    db.refresh(user)
    user = db.scalar(select(User).options(selectinload(User.profile)).where(User.id == user.id))
    maybe_log_local_token("email verification", raw)
    _ = settings
    return user, raw


def authenticate(db: Session, email_or_username: str, password: str) -> User:
    ident = email_or_username.strip()
    stmt = select(User).options(selectinload(User.profile)).where(
        or_(User.email == ident.lower(), User.username == ident)
    )
    user = db.scalar(stmt)
    if user is None or not verify_password(password, user.password_hash):
        raise AppError("INVALID_CREDENTIALS", "Email or password is incorrect.", 401)
    if user.status == UserStatus.DELETED:
        raise AppError("INVALID_CREDENTIALS", "Email or password is incorrect.", 401)
    if user.status == UserStatus.SUSPENDED:
        raise AppError("ACCOUNT_SUSPENDED", "This account is suspended.", 403)
    user.last_login_at = datetime.now(UTC)
    audit(db, user.id, "user.login")
    db.commit()
    return user


def verify_email(db: Session, token: str) -> None:
    user_id = consume_email_token(token)
    if not user_id:
        raise AppError("INVALID_TOKEN", "Verification token is invalid or expired.", 400)
    user = db.get(User, UUID(user_id))
    if user is None:
        raise AppError("INVALID_TOKEN", "Verification token is invalid or expired.", 400)
    user.status = UserStatus.ACTIVE.value
    user.email_verified_at = datetime.now(UTC)
    audit(db, user.id, "user.verify_email")
    db.commit()


def request_password_reset(db: Session, email: str) -> str | None:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None or user.status in {UserStatus.DELETED, UserStatus.SUSPENDED}:
        return None
    raw = store_reset_token(str(user.id))
    audit(db, user.id, "user.password_reset_request")
    db.commit()
    maybe_log_local_token("password reset", raw)
    return raw


def confirm_password_reset(db: Session, token: str, new_password: str) -> None:
    validate_password(new_password)
    user_id = consume_reset_token(token)
    if not user_id:
        raise AppError("INVALID_TOKEN", "Reset token is invalid or expired.", 400)
    user = db.get(User, UUID(user_id))
    if user is None:
        raise AppError("INVALID_TOKEN", "Reset token is invalid or expired.", 400)
    user.password_hash = hash_password(new_password)
    audit(db, user.id, "user.password_reset_confirm")
    db.commit()


def logout_user(db: Session, user: User, jti: str | None) -> None:
    settings = get_settings()
    if jti:
        deny_jti(jti, settings.jwt_access_ttl_minutes * 60)
    audit(db, user.id, "user.logout")
    db.commit()


def delete_account(db: Session, user: User) -> None:
    user.status = UserStatus.DELETED.value
    user.deleted_at = datetime.now(UTC)
    user.email = f"deleted-{user.id}@invalid.local"
    user.username = f"deleted_{str(user.id)[:8]}"
    user.password_hash = hash_password(store_email_token(str(user.id), ttl_seconds=1) + "Aa1!")
    if user.profile:
        user.profile.display_name = "Deleted user"
        user.profile.biography = None
        user.profile.interests = []
    reviews = db.scalars(select(Review).where(Review.author_id == user.id)).all()
    for review in reviews:
        review.state = ReviewState.DELETED.value
        review.deleted_at = user.deleted_at
    audit(db, user.id, "user.delete_account")
    db.commit()


def update_profile(db: Session, user: User, data) -> ProfileOut:
    if user.profile is None:
        user.profile = Profile(user_id=user.id, interests=[])
        db.add(user.profile)
    if data.display_name is not None:
        user.profile.display_name = data.display_name
    if data.biography is not None:
        user.profile.biography = data.biography
    if data.interests is not None:
        user.profile.interests = data.interests
    db.commit()
    db.refresh(user)
    return profile_out(user)
