"""Shared pytest fixtures."""

import re
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from securebank.config import Settings
from securebank.database import SessionLocal
from securebank.main import create_app


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(
        environment="test",
        debug=False,
        database_url=f"sqlite:///{tmp_path / 'test.sqlite3'}",
        secret_key="test-secret-key-for-securebank",
        secure_cookie=False,
        hsts_enabled=False,
        seed_demo_data=False,
    )


@pytest.fixture
def client(settings: Settings) -> Generator[TestClient, None, None]:
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session(client: TestClient) -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def seeded_client(tmp_path) -> Generator[TestClient, None, None]:
    seeded_settings = Settings(
        environment="test",
        debug=False,
        database_url=f"sqlite:///{tmp_path / 'seeded.sqlite3'}",
        secret_key="test-secret-key-for-securebank",
        secure_cookie=False,
        hsts_enabled=False,
        seed_demo_data=True,
    )
    app = create_app(seeded_settings)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def seeded_db(seeded_client: TestClient) -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_csrf_token(client: TestClient, path: str) -> str:
    response = client.get(path)
    assert response.status_code == 200
    match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    assert match is not None
    return match.group(1)
