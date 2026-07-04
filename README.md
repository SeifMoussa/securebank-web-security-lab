# SecureBank Web Security Lab

[![CI](https://github.com/SeifMoussa/securebank-web-security-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/SeifMoussa/securebank-web-security-lab/actions/workflows/ci.yml)
[![CodeQL](https://github.com/SeifMoussa/securebank-web-security-lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/SeifMoussa/securebank-web-security-lab/actions/workflows/codeql.yml)
[![ZAP Baseline](https://github.com/SeifMoussa/securebank-web-security-lab/actions/workflows/zap-baseline.yml/badge.svg)](https://github.com/SeifMoussa/securebank-web-security-lab/actions/workflows/zap-baseline.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Fictional lab-only project.** This is not a real bank, does not move real money, does not connect to payment systems, and must not contain real customer data or real financial identifiers.

SecureBank Web Security Lab is a deliberately small server-rendered FastAPI application for demonstrating secure software engineering practices in a recruiter-friendly portfolio project. It uses fictional users, fictional accounts, and integer "lab credits" only.

## Why I Built This

I wanted a small application where security decisions were visible in the code and test suite, not just listed in a checklist. A fictional banking flow gave me useful boundaries to work against: authentication, authorization, transfers, audit events, and hostile input all matter, while no real financial data or payment rails are involved. I used the OWASP Top 10 as a coverage map, then backed the controls with security-focused tests and a ZAP baseline rather than treating the mapping itself as proof.

## What Was Harder Than Expected

Authentication safety was the part with the most edge cases. Adding Argon2id hashing was straightforward; making login failures generic, doing dummy verification for unknown users, handling signed sessions, and testing tampered cookies required more care. The fictional transfer path also needed deliberate transaction boundaries so a failed write could not leave the lab-credit balances half-updated. Keeping the ZAP baseline useful without presenting every scanner warning as an exploitable finding was another judgment call, which is why its workflow keeps a report for review.

## What It Demonstrates

- Defensive authentication design with Argon2id password hashing.
- Signed session cookies and CSRF protection for server-rendered forms.
- SQL injection prevention through SQLAlchemy expression APIs and static checks.
- XSS prevention through global Jinja2 autoescape, CSP, and template scans.
- Access control for authenticated banking-style pages.
- Atomic fictional transfer behavior with rollback on persistence failure.
- Security audit logging without plaintext passwords or session secrets.
- Practical pytest coverage for OWASP Top 10 controls.
- Docker Compose files and smoke scripts for later runtime verification.
- GitHub Actions CI, CodeQL, and optional ZAP baseline workflow configuration.

## Current Features

- Register, login, logout, and authenticated landing page.
- Demo users `alice`, `bob`, and `carol` with fictional lab-credit accounts.
- Dashboard showing the current user's lab-credit balance and recent transactions.
- Fictional transfer flow between demo users.
- Transaction history page.
- Health endpoints: `/healthz` and `/health`.
- Plain CSS, server-rendered templates, and no React.

## Tech Stack

- FastAPI
- Jinja2 server-rendered templates
- SQLAlchemy 2
- SQLite
- Pydantic v2 and pydantic-settings
- Argon2id via `argon2-cffi`
- `itsdangerous` signed tokens
- Plain CSS
- pytest
- ruff
- Docker Compose

Verified on GitHub: GitHub Actions CI, CodeQL, Docker smoke, and OWASP ZAP baseline workflow.

## Security Controls

- Argon2id password hashing.
- Generic login failure message.
- Dummy password verification for missing users to reduce username enumeration risk.
- Signed HttpOnly SameSite=Strict session cookies.
- Configurable Secure cookie and HSTS settings.
- CSRF tokens for state-changing forms.
- Security headers including CSP `default-src 'self'`.
- Jinja2 autoescape enabled globally.
- No template `|safe` usage.
- SQLAlchemy parameterized query style.
- Server-side authorization based on the authenticated session.
- Atomic debit, credit, and transaction creation for fictional transfers.
- Audit events for auth, authorization, and transfer outcomes.
- Static safety scans for raw SQL patterns, unsafe template filters, real financial identifiers, and committed secret material.

## OWASP Top 10 Summary

- A01 Broken Access Control: protected routes, session-derived sender, IDOR tests.
- A02 Cryptographic Failures: Argon2id passwords and signed session tokens.
- A03 Injection: SQLAlchemy queries and malicious-looking input tests.
- A04 Insecure Design: fictional lab scope, integer lab credits, atomic transfers.
- A05 Security Misconfiguration: security headers, CSP, HSTS gating, autoescape.
- A06 Vulnerable and Outdated Components: dependencies declared; automated scanning pending.
- A07 Identification and Authentication Failures: validation, generic failures, dummy verification, logout, tampered-session tests.
- A08 Software and Data Integrity Failures: signed session/CSRF tokens; CI integrity checks pending.
- A09 Security Logging and Monitoring Failures: audit events and sensitive-data exclusion tests.
- A10 SSRF: documented as out of scope because the app performs no outbound HTTP requests.

See [docs/owasp-top-10-mapping.md](docs/owasp-top-10-mapping.md).

## Quick Start Without Docker

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m uvicorn securebank.main:app --reload
```

Open:

- `http://localhost:8000/healthz`
- `http://localhost:8000/login`
- `http://localhost:8000/register`

Demo password for seeded users:

```text
LabDemo123!
```

## Docker Quick Start

Docker files and smoke scripts are implemented, but Docker runtime verification is pending locally because Docker is not installed or not on PATH in the current environment.

On a Docker-capable machine:

```bash
docker compose build
docker compose up -d
curl http://localhost:8000/healthz
docker compose down
```

Smoke scripts:

```bash
scripts/verify-docker.sh
```

```powershell
.\scripts\smoke-test.ps1
```

## Test Commands

```bash
python -m pytest
python -m ruff check .
python -m ruff format --check .
```

Make targets are also available:

```bash
make test
make lint
make format-check
```

## Project Structure

```text
src/securebank/
  auth/          authentication routes and services
  audit/         audit event helper
  banking/       fictional lab-credit pages and transfer service
  security/      password, session, CSRF, and header helpers
  templates/     server-rendered Jinja2 templates
  static/        plain CSS
tests/           unit, route, security, static safety, and Docker artifact tests
docs/            threat model, controls, OWASP mapping, testing, and safety docs
scripts/         Docker smoke verification scripts
```

## Screenshots

Screenshots are pending. No fake screenshots are included.

Planned real screenshots:

- Login page
- Dashboard
- Transfer form
- Transaction history

## Current Verification Status

- pytest: 70 passed
- coverage: 96.02%
- ruff check: passed
- ruff format check: passed
- docs check: passed
- Docker files and smoke scripts: implemented
- Docker runtime: verified through GitHub Actions Docker smoke
- GitHub Actions CI: verified on GitHub
- CodeQL: verified on GitHub
- ZAP baseline workflow: verified on GitHub

## Known Limitations

- This is a fictional banking security lab, not a production banking system.
- It has no real payment rails, bank integrations, customer data, or financial identifiers; the seeded users and lab-credit balances are demo data only.
- Deployment hardening is limited. The repository demonstrates configurable secure cookies and HSTS, but it does not provide production secrets management, infrastructure isolation, monitoring, backups, or disaster recovery.
- The OWASP Top 10 mapping, security tests, and ZAP baseline provide useful coverage, but they are not a substitute for a threat-model review, manual penetration test, or production risk assessment.
- Docker runtime is unavailable on the machine used for the local project notes; the Docker smoke and ZAP baseline paths are exercised through GitHub Actions.

## What I Would Improve Next

My next step would be to add a repeatable hardened deployment example with external secret injection, TLS termination, persistent database backups, and observable audit-event handling. I would also add explicit login throttling and session revocation, then extend the security tests around those controls. For scanner coverage, I would review and document ZAP baseline changes over time instead of letting the workflow become a badge that nobody reads.

## How to Verify It Works

Install the development dependencies, then run the same local checks used by the repository:

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m ruff format --check .
python scripts/check-docs.py
```

For a runtime check on a machine with Docker, use the repository's Compose configuration and verify the health endpoint:

```bash
docker compose build
docker compose up -d
curl http://localhost:8000/healthz
docker compose down
```

The ZAP baseline is defined in `.github/workflows/zap-baseline.yml` and runs against the local lab app in GitHub Actions. Review that workflow's uploaded report as well as its status; a green baseline is not a claim that the application is production-ready.

## License

MIT. See [LICENSE](LICENSE).
