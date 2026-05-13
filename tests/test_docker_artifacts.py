from pathlib import Path


def test_dockerfile_uses_expected_runtime_contract() -> None:
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

    assert "FROM python:3.12-slim" in dockerfile
    assert "python -m pip install ." in dockerfile
    assert "USER securebank" in dockerfile
    assert "EXPOSE 8000" in dockerfile
    assert "/healthz" in dockerfile
    assert '"python", "-m", "uvicorn"' in dockerfile


def test_dockerignore_excludes_local_runtime_state() -> None:
    dockerignore = Path(".dockerignore").read_text(encoding="utf-8").splitlines()

    for required_entry in [
        ".git/",
        ".venv/",
        "__pycache__/",
        ".pytest_cache/",
        ".ruff_cache/",
        ".env",
        "*.sqlite",
        "*.sqlite3",
        "*.db",
        "htmlcov/",
        "coverage.xml",
        "zap-report.html",
        "zap-report.json",
    ]:
        assert required_entry in dockerignore


def test_compose_uses_named_volume_and_healthz() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "127.0.0.1:8000:8000" in compose
    assert "securebank-data:/data" in compose
    assert "sqlite:////data/securebank_lab.sqlite3" in compose
    assert "/healthz" in compose
    assert "python -m uvicorn securebank.main:app" in compose
