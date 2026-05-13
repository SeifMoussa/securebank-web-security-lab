from fastapi.testclient import TestClient

from .conftest import get_csrf_token
from .test_banking import login_demo_user, transfer


def test_register_requires_csrf_token(client: TestClient) -> None:
    response = client.post(
        "/register",
        data={"username": "alice", "password": "StrongPass123!"},
    )

    assert response.status_code == 403


def test_register_rejects_invalid_csrf_token(client: TestClient) -> None:
    client.get("/register")

    response = client.post(
        "/register",
        data={"username": "alice", "password": "StrongPass123!", "csrf_token": "invalid"},
    )

    assert response.status_code == 403


def test_register_accepts_valid_csrf_token(client: TestClient) -> None:
    csrf_token = get_csrf_token(client, "/register")

    response = client.post(
        "/register",
        data={"username": "alice", "password": "StrongPass123!", "csrf_token": csrf_token},
        follow_redirects=False,
    )

    assert response.status_code == 303


def test_login_requires_csrf_token(client: TestClient) -> None:
    response = client.post(
        "/login",
        data={"username": "alice", "password": "StrongPass123!"},
    )

    assert response.status_code == 403


def test_logout_requires_csrf_token(client: TestClient) -> None:
    csrf_token = get_csrf_token(client, "/register")
    assert (
        client.post(
            "/register",
            data={"username": "alice", "password": "StrongPass123!", "csrf_token": csrf_token},
            follow_redirects=False,
        ).status_code
        == 303
    )
    csrf_token = get_csrf_token(client, "/login")
    assert (
        client.post(
            "/login",
            data={"username": "alice", "password": "StrongPass123!", "csrf_token": csrf_token},
            follow_redirects=False,
        ).status_code
        == 303
    )

    response = client.post("/logout", follow_redirects=False)

    assert response.status_code == 403


def test_transfer_requires_csrf_token(seeded_client: TestClient) -> None:
    login_demo_user(seeded_client, "alice")

    response = seeded_client.post(
        "/transfer",
        data={"recipient_username": "bob", "amount_credits": "10", "memo": "missing csrf"},
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_transfer_rejects_invalid_csrf_token(seeded_client: TestClient) -> None:
    login_demo_user(seeded_client, "alice")
    seeded_client.get("/transfer")

    response = seeded_client.post(
        "/transfer",
        data={
            "recipient_username": "bob",
            "amount_credits": "10",
            "memo": "invalid csrf",
            "csrf_token": "invalid-token",
        },
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_transfer_valid_csrf_still_requires_business_rules(seeded_client: TestClient) -> None:
    login_demo_user(seeded_client, "alice")

    failure = transfer(seeded_client, "bob", "0", "business rules still apply")
    success = transfer(seeded_client, "bob", "10", "valid csrf and valid transfer")

    assert failure.status_code == 400
    assert success.status_code == 303
