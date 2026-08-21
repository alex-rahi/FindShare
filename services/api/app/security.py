import re
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import bcrypt
import jwt
import redis
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_db

bearer_scheme = HTTPBearer(auto_error=False)

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,32}$")
PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{10,128}$")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def validate_username(username: str) -> None:
    if not USERNAME_RE.match(username):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username must be 3–32 letters, numbers, or underscores.",
        )


def validate_password(password: str) -> None:
    if not PASSWORD_RE.match(password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be 10+ characters with upper, lower, digit, and symbol.",
        )


def get_redis(settings: Settings | None = None) -> redis.Redis:
    settings = settings or get_settings()
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def rate_limit(key: str, limit: int, window_seconds: int) -> None:
    from app.errors import AppError

    settings = get_settings()
    if settings.app_env == "test":
        return
    try:
        client = get_redis()
        count = int(client.incr(key))
        if count == 1:
            client.expire(key, window_seconds)
        if count > limit:
            raise AppError("RATE_LIMITED", "Too many attempts. Try again later.", 429)
    except redis.RedisError:
        return


def create_token(
    subject: UUID,
    token_type: str,
    settings: Settings,
    extra: dict[str, Any] | None = None,
) -> tuple[str, str, datetime]:
    jti = str(uuid4())
    now = datetime.now(UTC)
    if token_type == "access":
        expires = now + timedelta(minutes=settings.jwt_access_ttl_minutes)
    else:
        expires = now + timedelta(days=settings.jwt_refresh_ttl_days)
    payload = {
        "sub": str(subject),
        "typ": token_type,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }
    if extra:
        payload.update(extra)
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    return token, jti, expires


def decode_token(token: str, settings: Settings) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def random_urlsafe(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    from app.models.user import User, UserStatus

    token = None
    if credentials:
        token = credentials.credentials
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_token(token, settings)
    if payload.get("typ") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    from app.tokens import is_jti_denied

    if payload.get("jti") and is_jti_denied(str(payload["jti"])):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

    user = db.get(User, UUID(payload["sub"]))
    if user is None or user.status == UserStatus.DELETED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if user.status == UserStatus.SUSPENDED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account suspended")
    return user


def get_current_user_optional(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    from app.models.user import User, UserStatus

    token = None
    if credentials:
        token = credentials.credentials
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = decode_token(token, settings)
    except HTTPException:
        return None
    if payload.get("typ") != "access":
        return None
    user = db.get(User, UUID(payload["sub"]))
    if user is None or user.status in {UserStatus.DELETED, UserStatus.SUSPENDED}:
        return None
    return user


def require_verified_user(user=Depends(get_current_user)):
    from app.models.user import UserStatus

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verify your email before performing this action.",
        )
    return user
