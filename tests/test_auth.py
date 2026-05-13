from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from securebank.models import AuditEvent, User
from securebank.security.passwords import verify_password

from .conftest import get_csrf_token

VALID_PASSWORD = "StrongPass123!"


def register(client: TestClient, username: str = "alice", password: str = VALID_PASSWORD):
    csrf_token = get_csrf_token(client, "/register")
    return client.post(
        "/register",
        data={"username": username, "password": password, "csrf_token": csrf_token},
        follow_redirects=False,
    )


def login(client: TestClient, username: str = "alice", password: str = VALID_PASSWORD):
    csrf_token = get_csrf_token(client, "/login")
    return client.post(
        "/login",
        data={"username": username, "password": password, "csrf_token": csrf_token},
        follow_redirects=False,
    )


def test_registration_stores_hash_not_plaintext(client: TestClient, db_session: Session) -> None:
    response = register(client)

    assert response.status_code == 303
    user = db_session.scalar(select(User).where(User.username == "alice"))
    assert user is not None
    assert user.password_hash != VALID_PASSWORD
    assert user.password_hash.startswith("$argon2")
    assert verify_password(VALID_PASSWORD, user.password_hash)


def test_duplicate_registration_returns_safe_error(client: TestClient) -> None:
    assert register(client).status_code == 303

    response = register(client)

    assert response.status_code == 400
    assert "Registration could not be completed." in response.text
    assert VALID_PASSWORD not in response.text


def test_login_success_creates_session(client: TestClient, settings) -> None:
    assert register(client).status_code == 303

    response = login(client)

    assert response.status_code == 303
    assert response.headers["location"] == "/me"
    set_cookie = response.headers["set-cookie"]
    assert settings.session_cookie_name in set_cookie
    assert "HttpOnly" in set_cookie
    assert "samesite=strict" in set_cookie.lower()


def test_login_failure_uses_generic_message(client: TestClient) -> None:
    response = login(client, username="missing_user", password="WrongPass123!")

    assert response.status_code == 400
    assert "Invalid username or password." in response.text
    assert "missing_user" in response.text


def test_real_and_missing_user_login_failures_match(client: TestClient) -> None:
    assert register(client).status_code == 303

    wrong_password = login(client, username="alice", password="WrongPass123!")
    missing_user = login(client, username="missing_user", password="WrongPass123!")

    assert wrong_password.status_code == missing_user.status_code == 400
    assert "Invalid username or password." in wrong_password.text
    assert "Invalid username or password." in missing_user.text


def test_missing_user_login_uses_dummy_verification(client: TestClient, monkeypatch) -> None:
    calls = {"count": 0}

    def fake_verify_dummy_password(password: str) -> bool:
        calls["count"] += 1
        return False

    monkeypatch.setattr("securebank.auth.service.verify_dummy_password", fake_verify_dummy_password)

    response = login(client, username="missing_user", password="WrongPass123!")

    assert response.status_code == 400
    assert calls["count"] == 1


def test_audit_events_emitted_without_password(client: TestClient, db_session: Session) -> None:
    assert register(client).status_code == 303
    assert login(client).status_code == 303
    assert login(client, password="WrongPass123!").status_code == 400

    events = db_session.scalars(select(AuditEvent)).all()
    event_types = {event.event_type for event in events}

    assert {"register_success", "login_success", "login_failure"} <= event_types
    assert all(VALID_PASSWORD not in (event.detail or "") for event in events)
    assert all("WrongPass123!" not in (event.detail or "") for event in events)
