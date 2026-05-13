# Security Notes

This project is intentionally scoped as a fictional, lab-only defensive security portfolio project.

Implemented Phase 2 controls:

- Authentication routes for registration, login, logout, and a minimal authenticated page.
- Username validation for 3-32 characters using letters, numbers, and underscore.
- Password validation requiring length, uppercase, lowercase, digit, and symbol.
- Argon2id password hashing via `argon2-cffi`.
- Generic login failure messages.
- Dummy password verification for missing users to reduce username enumeration risk.
- Signed session cookies with HttpOnly, SameSite=Strict, configurable Secure flag, and expiry.
- Tampered session rejection.
- CSRF token generation and validation for register, login, and logout forms.
- Jinja2 environment with global autoescape enabled.
- No Jinja2 `|safe` usage.
- Security headers: X-Content-Type-Options, X-Frame-Options, Referrer-Policy, and Content-Security-Policy.
- Optional HSTS controlled by settings.
- Audit events for registration success/failure, login success/failure, logout, and authorization denial.
- Request IDs attached to responses and audit events where available.

Implemented Phase 3 controls:

- Fictional lab-credit account model owned by a user.
- Fictional transaction model using internal integer IDs only.
- Balances stored as integer lab credits, not floating point values.
- Deterministic demo users `alice`, `bob`, and `carol` with fictional balances.
- Authenticated dashboard, transfer form, and transaction history.
- Sender account is derived from the authenticated session, not submitted form data.
- Transfer validation for recipient existence, self-transfer, positive amount, sufficient credits, and memo length.
- Debit, credit, and transaction record creation are committed together and rolled back together on persistence failure.
- Transfer memos are rendered through Jinja2 autoescape.
- Audit events for transfer success, transfer failure, insufficient funds, recipient not found, and authorization denial.

Tested Phase 4 security coverage:

- SQL injection defenses are tested with harmless malicious-looking login, recipient lookup, and memo inputs.
- Source scans check for raw SQL execution and string-concatenated SQL patterns.
- XSS defenses are tested through global Jinja2 autoescape, escaped transaction memos, no `|safe`, and CSP.
- Access-control tests cover unauthenticated banking access, tampered sessions, other-user balance exposure, and ignored submitted sender account IDs.
- CSRF tests cover register, login, logout, and transfer state-changing routes.
- Authentication security tests cover Argon2id storage, no plaintext passwords, generic login failure messages, dummy verification, logout invalidation, and tampered session rejection.
- Audit tests cover register success/failure, login success/failure, logout, transfer success/failure, insufficient funds, recipient not found, authorization denial, and exclusion of plaintext passwords and session secrets.
- Static safety scans check for unsafe template filters, raw SQL patterns, real financial identifier examples, and committed secret material.
- OWASP Top 10 mapping documents A01-A10, with A10 SSRF honestly marked out of scope because the app performs no outbound HTTP requests.

Phase 5 Docker/runtime notes:

- Dockerfile uses Python 3.12 slim and runs the app with `python -m uvicorn`.
- Container runtime uses a non-root `securebank` user.
- Compose publishes only `127.0.0.1:8000:8000`.
- Compose stores SQLite runtime data in a named volume at `/data`.
- `.dockerignore` excludes local SQLite databases, `.env`, caches, coverage output, ZAP reports, editor files, and Git data.
- Compose defaults are lab-only placeholders and are not production secrets.
- Docker runtime verification is pending in this environment because Docker is not installed or not on PATH.

Phase 6 documentation notes:

- README and docs now describe implemented controls, tests, limitations, and pending phases.
- Documentation explicitly states that Docker runtime verification is pending locally.
- Documentation explicitly states that GitHub Actions CI, CodeQL, and ZAP are configured but not yet verified on GitHub.
- Documentation consistency tests check local links, documented commands, status honesty, and absence of real financial identifier examples.

Phase 7 CI/ZAP safety notes:

- GitHub Actions CI is configured but not yet verified on GitHub.
- CodeQL is configured but not yet verified on GitHub.
- ZAP baseline workflow is configured as a separate defensive scan against the local lab app only.
- ZAP baseline workflow is configured but not yet verified until its first GitHub run.
- ZAP policy remains: fail on HIGH findings only, document WARN/MEDIUM findings for human review.
- Dependabot is configured for weekly pip, GitHub Actions, and Docker ecosystem updates.

Phase 8 QA notes:

- Final QA verified core app flows, security controls, workflow configuration, documentation honesty, and local uvicorn smoke behavior.
- Docker and ZAP runtime verification remain pending because Docker is not installed or not on PATH locally.
- No GitHub Actions, CodeQL, or ZAP success is claimed before GitHub execution.

Phase 9 release safety notes:

- Release preparation is local only; no GitHub publishing, tag, or release was created.
- Docker runtime, ZAP runtime, GitHub Actions CI, CodeQL, and Dependabot verification remain pending until first GitHub run.
- `RELEASE.md` documents manual publishing commands, post-push checks, screenshot policy, and recruiter-facing portfolio copy.

Important limitations:

- The login response path reduces username enumeration risk but does not claim exact constant-time behavior.
- Lab credits are fictional and do not represent money, payments, deposits, cards, account numbers, IBANs, SWIFT codes, or routing numbers.
- Dependency and code scanning automation are not implemented until later CI phases.
