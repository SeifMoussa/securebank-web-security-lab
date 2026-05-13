# Testing Guide

The current local verification suite has 65 tests.

## Run Tests

```bash
python -m pytest
```

Windows fallback if `python` is not recognized:

```powershell
py -m pytest
```

## Run Ruff

```bash
python -m ruff check .
python -m ruff format --check .
```

Windows fallback:

```powershell
py -m ruff check .
py -m ruff format --check .
```

Make targets:

```bash
make test
make lint
make format-check
```

## What The Tests Cover

- Health endpoints.
- Settings loading.
- Password hashing and verification.
- Authentication success and failure behavior.
- Signed session creation, logout, and tamper rejection.
- CSRF behavior for register, login, logout, and transfer.
- Security headers.
- Jinja2 autoescape and no `|safe`.
- Fictional seed data.
- Dashboard, transfer, and transaction history behavior.
- Atomic transfer rollback.
- Access control and IDOR-style checks.
- SQL injection defensive behavior.
- XSS defensive behavior.
- Audit event creation and sensitive-data exclusion.
- OWASP mapping document coverage.
- Docker artifact static checks.
- Static safety scans.

## Security Test Organization

- `tests/test_auth.py`: registration, login, generic failures, password storage, and auth audit coverage.
- `tests/test_passwords.py`: Argon2id helpers.
- `tests/test_sessions.py`: signed session helpers and tamper rejection.
- `tests/test_csrf.py`: state-changing route CSRF behavior.
- `tests/test_security_headers.py`: browser security headers and HSTS gating.
- `tests/test_xss_defenses.py`: Jinja2 escaping and CSP.
- `tests/test_sql_injection_defenses.py`: malicious-looking input as data and SQL query style checks.
- `tests/test_access_control.py`: protected route and session authorization checks.
- `tests/test_audit_logging.py`: audit event coverage.
- `tests/test_static_safety.py`: repository safety checks.

## Static Safety Tests

Static tests check for practical, low-maintenance risks:

- Raw SQL execution and string-concatenation patterns.
- Template `|safe` usage.
- Real financial identifier examples.
- Obvious committed secret material.

These tests are intentionally simple. They are not a replacement for code review or future CI scanning.

## Docker Tests

`tests/test_docker_artifacts.py` verifies that Dockerfile, Compose, and `.dockerignore` contain the expected settings.

Docker runtime verification has not passed locally because Docker is not installed or not on PATH in this environment. Runtime smoke verification is pending until run on a Docker-capable machine or CI runner.

## Not Covered Yet

- GitHub Actions CI execution on GitHub.
- CodeQL analysis on GitHub.
- OWASP ZAP baseline workflow execution on GitHub.
- Docker runtime smoke results.
- Production-grade rate limiting or lockout enforcement.
