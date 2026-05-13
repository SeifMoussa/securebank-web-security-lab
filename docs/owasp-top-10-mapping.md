# OWASP Top 10 Mapping

This mapping describes the current defensive coverage for the fictional SecureBank Web Security Lab. It is intentionally honest: some categories are demonstrated directly, while others are documented through project constraints and verification checks.

## A01 Broken Access Control

Implemented controls:

- Protected banking routes require a valid authenticated session.
- Sender account is derived from the signed session, not submitted form data.
- Users cannot influence the transfer sender through account or user identifiers in forms.
- Missing or invalid sessions redirect to login and emit audit events.

Tests:

- `tests/test_access_control.py`
- `tests/test_banking.py`
- `tests/test_sessions.py`

Limitations:

- There are no admin roles or multi-role authorization paths yet.

## A02 Cryptographic Failures

Implemented controls:

- Passwords are hashed with Argon2id through `argon2-cffi`.
- Plaintext passwords are not stored.
- Signed sessions use `itsdangerous`.
- Session cookies are HttpOnly, SameSite=Strict, expiry-bound, and configurable for Secure.

Tests:

- `tests/test_passwords.py`
- `tests/test_auth.py`
- `tests/test_sessions.py`
- `tests/test_audit_logging.py`

Limitations:

- Secrets are supplied through local environment settings; secret rotation is outside the lab scope.

## A03 Injection

Implemented controls:

- Application queries use SQLAlchemy expression APIs.
- Raw SQL execution and string-concatenated SQL patterns are covered by static tests.
- Malicious-looking login and transfer inputs are treated as data, not executable SQL.
- Transaction memos can store harmless malicious-looking strings as text.

Tests:

- `tests/test_sql_injection_defenses.py`
- `tests/test_static_safety.py`

Limitations:

- Static scans are practical guardrails, not a substitute for manual code review.

## A04 Insecure Design

Implemented controls:

- The app is explicitly fictional and lab-only.
- Balances are integer lab credits, not real money.
- There are no payment integrations or real financial identifiers.
- Transfers validate recipient, self-transfer, positive amount, sufficient credits, and memo length.
- Debit, credit, and transaction creation are committed atomically.

Tests:

- `tests/test_banking.py`
- `tests/test_static_safety.py`

Limitations:

- The project is intentionally small and does not model production banking workflows.

## A05 Security Misconfiguration

Implemented controls:

- Security headers are added by middleware.
- CSP uses `default-src 'self'`.
- HSTS is set only when configured.
- Jinja2 autoescape is enabled globally.
- No template uses `|safe`.

Tests:

- `tests/test_security_headers.py`
- `tests/test_xss_defenses.py`
- `tests/test_static_safety.py`

Limitations:

- Production deployment hardening is outside the current local lab scope.

## A06 Vulnerable and Outdated Components

Current coverage:

- Runtime and development dependencies are declared in `pyproject.toml`.
- Automated dependency scanning is not implemented yet; this belongs to later CI work.

Planned later coverage:

- GitHub Actions dependency installation.
- CodeQL workflow.
- Optional dependency review or similar GitHub-native checks if added later.

Limitations:

- No automated dependency scanning workflow is implemented yet.

## A07 Identification and Authentication Failures

Implemented controls:

- Username and password validation.
- Generic login failure message.
- Dummy password verification path for missing users to reduce username enumeration risk.
- Logout clears the session cookie.
- Tampered sessions are rejected.

Tests:

- `tests/test_auth.py`
- `tests/test_passwords.py`
- `tests/test_sessions.py`

Limitations:

- The project reduces username enumeration risk but does not claim exact constant-time login responses.
- Full rate limiting or account lockout enforcement is not implemented yet.

## A08 Software and Data Integrity Failures

Current coverage:

- No dynamic plugin loading.
- No update mechanism.
- No unsafe deserialization.
- Session and CSRF tokens are signed.

Planned later coverage:

- CI workflow integrity checks.
- CodeQL workflow.
- Release preparation checks.

Tests:

- `tests/test_sessions.py`
- `tests/test_csrf.py`

Limitations:

- CI workflow integrity checks are planned for a later phase.

## A09 Security Logging and Monitoring Failures

Implemented controls:

- Audit events are emitted for registration success/failure, login success/failure, logout, transfer success/failure, insufficient funds, recipient not found, and authorization denial.
- Audit events include request IDs where available.
- Audit tests check that plaintext passwords and session secrets are not stored in audit events.

Tests:

- `tests/test_audit_logging.py`
- `tests/test_auth.py`
- `tests/test_banking.py`

Limitations:

- Audit events are stored locally in SQLite; external monitoring integration is outside scope.

## A10 Server-Side Request Forgery

Status: documented as out of scope for current functionality.

Reason:

- The application performs no outbound HTTP requests.
- Users cannot submit URLs for server-side fetching.
- No integrations, webhooks, metadata-service requests, or payment-provider calls exist.

Tests:

- `tests/test_owasp_mapping.py` verifies A10 SSRF is documented as out of scope.

Limitations:

- If outbound HTTP functionality is added in a future phase, this category must be revisited.
