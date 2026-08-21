from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import auth_service
from app.config import Settings, get_settings
from app.db import get_db
from app.errors import AppError
from app.models.user import User, UserStatus
from app.schemas import (
    AuthMeOut,
    LoginIn,
    PasswordResetConfirm,
    PasswordResetOut,
    PasswordResetRequest,
    ProfileUpdate,
    RegisterIn,
    RegisterOut,
    TokenPair,
    VerifyIn,
)
from app.security import bearer_scheme, decode_token, get_current_user, rate_limit, require_verified_user

router = APIRouter(prefix="/api/v1")


def _set_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.jwt_access_ttl_minutes * 60,
        path="/",
    )


@router.post("/auth/register", response_model=RegisterOut, status_code=201)
def register(body: RegisterIn, response: Response, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    rate_limit("rl:register", limit=20, window_seconds=3600)
    user, verify_token = auth_service.register_user(
        db,
        email=body.email,
        username=body.username,
        password=body.password,
        invitation_code=body.invitation_code,
    )
    tokens = auth_service.issue_tokens(user)
    _set_cookie(response, tokens.access_token, settings)
    return RegisterOut(
        user=auth_service.user_out(user),
        tokens=tokens,
        email_verification_required=True,
        local_verify_token=verify_token if settings.app_env in {"local", "test"} else None,
    )


@router.post("/auth/login", response_model=RegisterOut)
def login(body: LoginIn, response: Response, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    rate_limit("rl:login", limit=30, window_seconds=300)
    user = auth_service.authenticate(db, body.email_or_username, body.password)
    tokens = auth_service.issue_tokens(user)
    _set_cookie(response, tokens.access_token, settings)
    return RegisterOut(
        user=auth_service.user_out(user),
        tokens=tokens,
        email_verification_required=user.status != UserStatus.ACTIVE,
        local_verify_token=None,
    )


@router.post("/auth/logout", status_code=204)
def logout(
    request: Request,
    response: Response,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    token = credentials.credentials if credentials else request.cookies.get("access_token")
    jti = None
    if token:
        try:
            jti = decode_token(token, settings).get("jti")
        except Exception:
            jti = None
    auth_service.logout_user(db, user, jti=jti)
    response.delete_cookie("access_token", path="/")


@router.post("/auth/refresh", response_model=TokenPair)
def refresh(user: User = Depends(get_current_user), settings: Settings = Depends(get_settings)):
    return auth_service.issue_tokens(user)


@router.post("/auth/verify-email", status_code=204)
def verify_email(body: VerifyIn, db: Session = Depends(get_db)):
    auth_service.verify_email(db, body.token)


@router.post("/auth/password-reset/request", status_code=202, response_model=PasswordResetOut)
def password_reset_request(
    body: PasswordResetRequest, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)
):
    raw = auth_service.request_password_reset(db, body.email)
    return PasswordResetOut(
        detail="If an account exists, a reset token was created.",
        local_reset_token=raw if settings.app_env in {"local", "test"} else None,
    )


@router.post("/auth/password-reset/confirm", status_code=204)
def password_reset_confirm(body: PasswordResetConfirm, db: Session = Depends(get_db)):
    auth_service.confirm_password_reset(db, body.token, body.new_password)


@router.get("/auth/me", response_model=AuthMeOut)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.scalar(select(User).options(selectinload(User.profile)).where(User.id == user.id))
    return AuthMeOut(user=auth_service.user_out(user), profile=auth_service.profile_out(user))


@router.patch("/profiles/me", response_model=AuthMeOut)
def patch_me(body: ProfileUpdate, user: User = Depends(require_verified_user), db: Session = Depends(get_db)):
    user = db.scalar(select(User).options(selectinload(User.profile)).where(User.id == user.id))
    auth_service.update_profile(db, user, body)
    user = db.scalar(select(User).options(selectinload(User.profile)).where(User.id == user.id))
    return AuthMeOut(user=auth_service.user_out(user), profile=auth_service.profile_out(user))


@router.delete("/users/me", status_code=204)
def delete_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    auth_service.delete_account(db, user)


@router.get("/users/{username}")
def public_user(username: str, db: Session = Depends(get_db), limit: int = 20):
    from app import review_service

    user = db.scalar(
        select(User).options(selectinload(User.profile)).where(User.username == username, User.status == UserStatus.ACTIVE)
    )
    if user is None:
        raise AppError("NOT_FOUND", "Profile not found.", 404)
    items, _total = review_service.list_published(db, author=username, limit=min(limit, 50))
    return {
        "username": user.username,
        "display_name": user.profile.display_name if user.profile else None,
        "biography": user.profile.biography if user.profile else None,
        "interests": list(user.profile.interests or []) if user.profile else [],
        "reviews": [review_service.to_out(r) for r in items],
    }
