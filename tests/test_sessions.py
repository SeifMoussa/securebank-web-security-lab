from fastapi.testclient import TestClient

from securebank.security.sessions import create_session_token, read_session_token

from .test_auth import login, register


def test_session_token_round_trip(settings) -> None:
    token = create_session_token(123, settings)

    data = read_session_token(token, settings)

    assert data == {"user_id": 123}


def test_tampered_session_rejected(client: TestClient, settings) -> None:
    client.cookies.set(settings.session_cookie_name, "tampered-session")

    response = client.get("/me", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_logout_clears_session(client: TestClient, settings) -> None:
    assert register(client).status_code == 303
    assert login(client).status_code == 303

    response = client.get("/me")
    assert response.status_code == 200
    csrf_token = response.text.split('name="csrf_token" value="', 1)[1].split('"', 1)[0]

    logout_response = client.post(
        "/logout",
        data={"csrf_token": csrf_token},
        follow_redirects=False,
    )

    assert logout_response.status_code == 303
    assert settings.session_cookie_name in logout_response.headers["set-cookie"]
    assert "Max-Age=0" in logout_response.headers["set-cookie"]
