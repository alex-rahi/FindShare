import os

os.environ["APP_ENV"] = "test"
os.environ["SEED_ON_STARTUP"] = "false"
os.environ["SECRET_KEY"] = "test-secret-key-which-is-long-enough-32ch"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["JWT_ACCESS_TTL_MINUTES"] = "60"
os.environ["REGISTRATION_MODE"] = "open"
os.environ["MAXIMUM_ACTIVE_USERS"] = "10000"

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.config import get_settings

get_settings.cache_clear()

from app.db import Base, get_db
from app.main import app
from app.models import *  # noqa: F401, F403
from app.seed import seed_demo


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = Session(engine)
    seed_demo(session)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
