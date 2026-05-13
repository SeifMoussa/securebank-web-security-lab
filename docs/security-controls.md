# Security Controls

This document summarizes implemented defensive controls and where they are tested.

## Authentication

- Username validation allows only letters, numbers, and underscore with a length of 3-32 characters.
- Password validation requires at least 12 characters with uppercase, lowercase, digit, and symbol.
- Passwords are stored only as Argon2id hashes through `argon2-cffi`.
- Login failures use a generic message.
- Missing-user login attempts perform dummy password verification to reduce username enumeration risk.
- The project does not claim exact constant-time login behavior.

Tests:

- `tests/test_auth.py`
- `tests/test_passwords.py`

## Sessions

- Sessions are signed with `itsdangerous`.
- Session cookies are HttpOnly, SameSite=Strict, expiry-bound, and configurable for Secure.
- Logout clears the session cookie.
- Tampered sessions are rejected.

Tests:

- `tests/test_sessions.py`
- `tests/test_auth.py`

## CSRF

- Register, login, logout, and transfer forms require CSRF tokens.
- Tokens are signed and paired with a SameSite cookie.
- Missing and invalid tokens return 403.

Tests:

- `tests/test_csrf.py`

## Security Headers

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'`
- HSTS only when configured.

Tests:

- `tests/test_security_headers.py`

## XSS Prevention

- Jinja2 autoescape is enabled globally.
- User-controlled transaction memos render escaped.
- No template uses `|safe`.
- CSP supports defense in depth.

Tests:

- `tests/test_xss_defenses.py`
- `tests/test_static_safety.py`

## SQL Injection Prevention

- SQLAlchemy expression APIs are used for login, lookup, and transfer queries.
- Malicious-looking strings are tested as data, not executable SQL.
- Static tests scan for raw SQL execution and string-concatenation patterns.

Tests:

- `tests/test_sql_injection_defenses.py`
- `tests/test_static_safety.py`

## Access Control

- Banking pages require a valid session.
- Sender account is derived from the current authenticated session.
- Submitted account IDs do not influence transfer sender selection.
- Invalid or missing sessions emit audit events.

Tests:

- `tests/test_access_control.py`
- `tests/test_banking.py`
- `tests/test_sessions.py`

## Audit Logging

- Audit events are emitted for register success/failure, login success/failure, logout, authorization denial, transfer success/failure, insufficient funds, and recipient not found.
- Audit tests verify plaintext passwords and session secrets are not written to audit event fields.

Tests:

- `tests/test_audit_logging.py`

## Atomic Transfers

- Fictional transfers debit the sender, credit the recipient, and create a transaction record in one database transaction.
- Persistence errors roll back the full transfer.
- Balances are integer lab credits, not floats.

Tests:

- `tests/test_banking.py`

## Static Safety Scans

- No raw SQL string-concatenation patterns.
- No unallowlisted `|safe` in templates.
- No real financial identifier examples.
- No obvious committed secret material.

Tests:

- `tests/test_static_safety.py`
