from fastapi.testclient import TestClient

from securebank.config import Settings
from securebank.main import create_app


def test_security_headers_present(client: TestClient) -> None:
    response = client.get("/healthz")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.headers["Content-Security-Policy"] == "default-src 'self'"
    assert "Strict-Transport-Security" not in response.headers
    assert "X-Request-ID" in response.headers


def test_hsts_only_when_enabled(tmp_path) -> None:
    settings = Settings(
        environment="test",
        database_url=f"sqlite:///{tmp_path / 'hsts.sqlite3'}",
        secret_key="test-secret-key-for-securebank",
        hsts_enabled=True,
        seed_demo_data=False,
    )
    app = create_app(settings)

    with TestClient(app) as test_client:
        response = test_client.get("/healthz")

    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
