# Development Guide

## Python Setup

Use Python 3.12.

Install the project and development tools:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Windows fallback if `python` is not recognized:

```powershell
py -m pip install --upgrade pip
py -m pip install -e ".[dev]"
```

## Run The App Locally

```bash
python -m uvicorn securebank.main:app --reload
```

Open:

- `http://localhost:8000/healthz`
- `http://localhost:8000/login`
- `http://localhost:8000/register`

Seeded demo users:

- `alice`
- `bob`
- `carol`

Demo password:

```text
LabDemo123!
```

## Run Tests And Lint

```bash
python -m pytest
python -m ruff check .
python -m ruff format --check .
```

Make targets:

```bash
make test
make lint
make format-check
```

## Local SQLite Behavior

By default, local development uses:

```text
sqlite:///./securebank_lab.sqlite3
```

That file is local runtime state. It is ignored by `.gitignore` and `.dockerignore`.

To reset local data, stop the app and remove the local SQLite file manually.

## Environment Variables

Start from `.env.example` if you want local overrides. Do not commit a real `.env`.

Important settings:

- `SECUREBANK_ENV`
- `SECUREBANK_DEBUG`
- `SECUREBANK_DATABASE_URL`
- `SECUREBANK_SECRET_KEY`
- `SECUREBANK_SESSION_COOKIE_NAME`
- `SECUREBANK_SESSION_MAX_AGE_SECONDS`
- `SECUREBANK_CSRF_COOKIE_NAME`
- `SECUREBANK_CSRF_TOKEN_MAX_AGE_SECONDS`
- `SECUREBANK_SECURE_COOKIE`
- `SECUREBANK_HSTS_ENABLED`
- `SECUREBANK_SEED_DEMO_DATA`

## Docker Compose

Docker files and smoke scripts are implemented. Docker runtime verification is pending locally because Docker is not installed or not on PATH in this environment.

On a Docker-capable machine:

```bash
docker compose build
docker compose up -d
curl http://localhost:8000/healthz
curl http://localhost:8000/login
curl http://localhost:8000/register
docker compose down
```

Smoke scripts:

```bash
scripts/verify-docker.sh
```

```powershell
.\scripts\smoke-test.ps1
```

The Compose file uses a named volume, `securebank-data`, for SQLite data at `/data/securebank_lab.sqlite3`. The Compose defaults are lab-only placeholders and are not production secrets.

## Troubleshooting

- If imports fail, install the project with `python -m pip install -e ".[dev]"`.
- If forms return 403, refresh the form page and submit with the new CSRF token.
- If local data looks stale, stop the app and remove the ignored SQLite file.
- If Docker commands fail with "docker not recognized", install Docker Desktop or run on a Docker-capable CI runner.
- If `make` is unavailable on Windows, run the underlying `python -m` commands directly.

## GitHub Workflows

GitHub Actions CI, CodeQL, and ZAP baseline workflows are configured in `.github/workflows/`. They are not yet verified on GitHub until the repository is pushed and the workflows run.
