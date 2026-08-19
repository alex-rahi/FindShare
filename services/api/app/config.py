from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "FindShare"
    app_env: str = "local"
    app_public_url: str = "http://localhost:3000"
    log_level: str = "INFO"
    secret_key: str = "replace-with-a-long-random-local-secret-at-least-32-chars"

    database_url: str = "postgresql+psycopg://findshare:findshare_local_only@postgres:5432/findshare"
    redis_url: str = "redis://redis:6379/0"

    auth_provider: str = "local_jwt"
    jwt_access_ttl_minutes: int = 15
    jwt_refresh_ttl_days: int = 7
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    cors_origins: str = "http://localhost:3000"

    registration_mode: str = "invite_only"
    maximum_active_users: int = 10
    reviews_per_user: int = 25
    images_per_review: int = 5
    maximum_image_size_mb: int = 10
    registration_enabled: bool = True
    image_uploads_enabled: bool = False
    comments_enabled: bool = False
    price_submissions_enabled: bool = False
    public_collections_enabled: bool = False
    placeholder_ads_enabled: bool = False
    live_advertising_enabled: bool = False
    advertising_provider: str = "mock"
    maintenance_mode: bool = False

    seed_on_startup: bool = True
    seed_admin_email: str = "admin@findshare.local"
    seed_admin_username: str = "admin"
    seed_admin_password: str = "FindShareAdmin!dev"
    seed_moderator_email: str = "moderator@findshare.local"
    seed_moderator_username: str = "moderator"
    seed_moderator_password: str = "FindShareMod!dev"
    seed_demo_email: str = "demo.reviewer@findshare.local"
    seed_demo_username: str = "demo_reviewer"
    seed_demo_password: str = "FindShareDemo!dev"
    seed_invitation_code: str = "FINDSHARE-DEV-INVITE"

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def is_local(self) -> bool:
        return self.app_env == "local"


@lru_cache
def get_settings() -> Settings:
    return Settings()
