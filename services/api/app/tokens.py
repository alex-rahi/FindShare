from datetime import UTC, datetime, timedelta

import redis

from app.config import get_settings
from app.security import get_redis, random_urlsafe

_memory: dict[str, tuple[str, datetime]] = {}


def _set(key: str, value: str, seconds: int) -> None:
    try:
        get_redis().set(key, value, ex=seconds)
    except redis.RedisError:
        _memory[key] = (value, datetime.now(UTC) + timedelta(seconds=seconds))


def _get(key: str) -> str | None:
    try:
        value = get_redis().get(key)
        if isinstance(value, bytes):
            return value.decode()
        return value
    except redis.RedisError:
        row = _memory.get(key)
        if not row:
            return None
        value, expires = row
        if expires < datetime.now(UTC):
            _memory.pop(key, None)
            return None
        return value


def _delete(key: str) -> None:
    try:
        get_redis().delete(key)
    except redis.RedisError:
        _memory.pop(key, None)


def store_email_token(user_id: str, ttl_seconds: int = 172800) -> str:
    token = random_urlsafe(24)
    _set(f"verify:{token}", user_id, ttl_seconds)
    return token


def consume_email_token(token: str) -> str | None:
    key = f"verify:{token}"
    user_id = _get(key)
    if user_id:
        _delete(key)
    return user_id


def store_reset_token(user_id: str, ttl_seconds: int = 7200) -> str:
    token = random_urlsafe(24)
    _set(f"reset:{token}", user_id, ttl_seconds)
    return token


def consume_reset_token(token: str) -> str | None:
    key = f"reset:{token}"
    user_id = _get(key)
    if user_id:
        _delete(key)
    return user_id


def deny_jti(jti: str, ttl_seconds: int) -> None:
    _set(f"token:deny:{jti}", "1", ttl_seconds)


def is_jti_denied(jti: str) -> bool:
    return _get(f"token:deny:{jti}") == "1"


def maybe_log_local_token(kind: str, token: str) -> None:
    settings = get_settings()
    if settings.app_env == "local":
        print(f"[local-only] {kind} token: {token}")
