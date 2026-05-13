# SecureBank Web Security Lab Release Preparation

Repository: `securebank-web-security-lab`

Owner: `SeifMoussa`

Target URL: `https://github.com/SeifMoussa/securebank-web-security-lab`

## Repository Metadata

Description:

```text
Fictional FastAPI banking security lab demonstrating OWASP Top 10 mitigations, authentication security, CSRF, XSS and SQL injection defenses, audit logging, Docker, and CI configuration.
```

GitHub About section:

```text
Fictional server-rendered FastAPI banking security lab for demonstrating secure software engineering, OWASP Top 10 mitigations, authentication, CSRF, XSS and SQL injection defenses, audit logging, Docker, and CI.
```

Suggested topics:

```text
fastapi, security, owasp, web-security, sqlalchemy, jinja2, pytest, argon2, csrf, xss, sql-injection, codeql, docker, portfolio
```

Suggested visibility: public.

License: MIT.

## Project Summary

SecureBank Web Security Lab is a fictional, lab-only secure software engineering portfolio project. It demonstrates defensive implementation and testing practices in a deliberately small server-rendered FastAPI application.

The app uses fictional users, fictional accounts, and integer lab credits only. It does not use real banking data, real money, real payment integrations, real financial identifiers, or real customer data.

## Verified Local Results

As of Phase 9 local release preparation:

- `python -m pytest`: 70 passed.
- `python -m pytest --cov=securebank --cov-report=term-missing --cov-fail-under=80`: 70 passed, 96.02% coverage.
- `python -m ruff check .`: passed.
- `python -m ruff format --check .`: passed.
- `python scripts/check-docs.py`: passed.
- `python -m py_compile scripts/check-docs.py`: passed.

## Pending Post-Push Checks

These are configured but not yet verified on GitHub:

- GitHub Actions CI.
- CodeQL.
- Optional OWASP ZAP baseline workflow.
- Dependabot.

These are pending until a Docker-capable machine or GitHub Actions runner runs them:

- Docker Compose runtime smoke verification.
- ZAP baseline runtime verification.

## Git Publishing Commands

Do not run these until manual approval is given.

```bash
git init
git status
git add .
git commit -m "Initial commit: SecureBank Web Security Lab v0.1.0"
git branch -M main
git remote add origin https://github.com/SeifMoussa/securebank-web-security-lab.git
git push -u origin main
```

## GitHub CLI Publishing Commands

Do not run these until manual approval is given.

```bash
gh repo create SeifMoussa/securebank-web-security-lab \
  --public \
  --description "Fictional FastAPI banking security lab demonstrating OWASP Top 10 mitigations, authentication security, CSRF, XSS and SQL injection defenses, audit logging, Docker, and CI configuration." \
  --source . \
  --remote origin \
  --push

gh repo edit SeifMoussa/securebank-web-security-lab \
  --add-topic fastapi \
  --add-topic security \
  --add-topic owasp \
  --add-topic web-security \
  --add-topic sqlalchemy \
  --add-topic jinja2 \
  --add-topic pytest \
  --add-topic argon2 \
  --add-topic csrf \
  --add-topic xss \
  --add-topic sql-injection \
  --add-topic codeql \
  --add-topic docker \
  --add-topic portfolio
```

## Post-Push Verification Checklist

- Confirm README badges resolve.
- Confirm CI workflow runs on `main`.
- Confirm CodeQL workflow runs.
- Confirm Dependabot page shows configured ecosystems.
- Confirm Docker smoke job runs on `main` or manual dispatch.
- Manually run the ZAP baseline workflow.
- Review ZAP WARN/MEDIUM findings for context.
- Confirm no HIGH ZAP findings, or fix before release.
- Confirm repository security alerts and CodeQL alerts.
- Confirm no `.env`, SQLite database, coverage output, or ZAP reports were pushed.

## v0.1.0 Release Plan

Do not execute until GitHub verification is complete.

Tag command:

```bash
git tag -a v0.1.0 -m "SecureBank Web Security Lab v0.1.0"
git push origin v0.1.0
```

Release title:

```text
SecureBank Web Security Lab v0.1.0
```

Release notes draft:

```markdown
## SecureBank Web Security Lab v0.1.0

Initial portfolio release of a fictional, lab-only secure software engineering project.

### Included

- FastAPI server-rendered app with Jinja2 templates.
- SQLAlchemy 2 and SQLite.
- Argon2id password hashing.
- Signed sessions.
- CSRF protection.
- Security headers.
- Fictional lab-credit accounts and transfers.
- Atomic transfer behavior.
- Audit logging.
- OWASP Top 10 mapping.
- 70 local tests with 96.02% coverage.
- Dockerfile, Docker Compose, and smoke scripts.
- GitHub Actions CI, CodeQL, ZAP baseline, and Dependabot configuration.

### Verified Locally

- pytest: 70 passed.
- coverage: 96.02%.
- ruff check: passed.
- ruff format check: passed.
- docs check: passed.

### Pending Until GitHub/Docker Runtime

- GitHub Actions CI first run.
- CodeQL first run.
- ZAP baseline first run.
- Docker runtime verification.

### Notes

This is a fictional lab project only. It is not a real bank and does not process real money or real customer data.

Screenshots are pending unless real screenshots are captured before release.
```

## Docker And ZAP Verification Notes

Docker is not installed locally, so Docker runtime verification is pending.

After pushing to GitHub, verify Docker through the `docker-smoke` job or on a Docker-capable machine:

```bash
docker compose build
docker compose up -d
curl http://localhost:8000/healthz
curl http://localhost:8000/login
curl http://localhost:8000/register
docker compose down
```

ZAP baseline verification should be run through the separate GitHub Actions workflow. It should fail only on HIGH findings. WARN/MEDIUM findings should be reviewed and documented.

## Screenshots Plan

No fake screenshots should be added.

Capture real screenshots after running the app locally or in Docker:

- `docs/screenshots/login.png`
- `docs/screenshots/dashboard.png`
- `docs/screenshots/transfer.png`
- `docs/screenshots/transactions.png`
- `docs/screenshots/tests.png`

After adding real screenshots:

- Update README with a Screenshots section.
- Confirm screenshots do not contain secrets, real customer data, or real financial identifiers.
- Re-run documentation and static safety checks.

## LinkedIn Post Draft

```text
I built SecureBank Web Security Lab, a fictional FastAPI web application designed to demonstrate secure software engineering practices in a small, reviewable portfolio project.

The project is intentionally lab-only: no real banking, no real money, no payment integrations, and no real customer data.

What it demonstrates:
- Argon2id password hashing
- Signed sessions and CSRF protection
- SQL injection and XSS defenses
- Server-side access control
- Atomic fictional transfer logic
- Audit logging
- OWASP Top 10 mapping
- 70 local tests with 96.02% coverage
- Docker, GitHub Actions, CodeQL, ZAP baseline, and Dependabot configuration

GitHub Actions, CodeQL, ZAP, and Docker runtime verification are configured/pending until the repository is pushed and workflows run.
```

## LinkedIn Projects Section Draft

```text
SecureBank Web Security Lab

Fictional FastAPI banking-style security lab demonstrating OWASP Top 10 mitigations, authentication security, signed sessions, CSRF protection, SQL injection prevention, XSS prevention, access control, audit logging, Docker, and CI configuration.

Built with FastAPI, Jinja2, SQLAlchemy 2, SQLite, Pydantic v2, Argon2id, pytest, ruff, Docker Compose, GitHub Actions, CodeQL, and OWASP ZAP baseline configuration.
```

## CV Bullet Points

- Built a fictional FastAPI banking-style security lab demonstrating OWASP Top 10 mitigations across authentication, sessions, CSRF, access control, injection defense, XSS prevention, and audit logging.
- Implemented Argon2id password hashing, signed HttpOnly SameSite session cookies, CSRF-protected server-rendered forms, and security headers including CSP.
- Designed fictional lab-credit transfer logic with SQLAlchemy 2, integer balances, server-side authorization, and atomic rollback behavior.
- Added 70 pytest tests covering app behavior, security controls, static safety scans, documentation consistency, and Docker artifact checks, with 96.02% local coverage.
- Configured GitHub Actions CI, CodeQL, Dependabot, Docker Compose, and a separate OWASP ZAP baseline workflow for post-push verification.

## Recruiter Summary

SecureBank Web Security Lab is a fictional, recruiter-safe secure software engineering project. It demonstrates how I design, implement, test, and document defensive controls in a realistic web application shape while keeping the scope safe for public review.

The project is intentionally server-rendered and small enough to audit. It emphasizes secure defaults, testable controls, honest documentation, and clear separation between implemented local verification and pending GitHub/Docker runtime checks.
