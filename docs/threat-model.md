# Threat Model

This threat model covers the fictional SecureBank Web Security Lab application as of Phase 6.

## Scope

- Server-rendered FastAPI application.
- Fictional users and fictional lab-credit accounts.
- Local SQLite database.
- Authentication, signed sessions, CSRF-protected forms, dashboard, transfer flow, and transaction history.
- Local development, portfolio review, and future CI verification.

## Out of Scope

- Real banking services.
- Real money movement.
- Real payment integrations.
- Real customer data.
- Real bank names, logos, account numbers, IBANs, SWIFT codes, routing numbers, or card numbers.
- Instructions or tooling for attacking third-party systems.
- Server-side URL fetching or integrations with external services.

## Assets

- User identities and password hashes.
- Signed session cookies.
- CSRF tokens.
- Fictional lab-credit balances.
- Fictional transaction records and memos.
- Audit events.
- Application configuration, especially secret-key material supplied through environment variables.

## Actors

- Anonymous visitor: can view login and register forms.
- Authenticated lab user: can view their own dashboard and create fictional transfers from their own account.
- Reviewer or recruiter: can inspect code, tests, and documentation.
- Local developer: can run the app, tests, and Docker artifacts.
- Malicious local test actor: represented only by harmless test inputs against the local app.

## Trust Boundaries

- Browser to FastAPI application over local HTTP.
- Signed cookies crossing the browser/server boundary.
- Form posts carrying CSRF tokens.
- FastAPI service layer to SQLite through SQLAlchemy.
- Environment variables into application settings.
- Docker container filesystem to named SQLite volume.

## Abuse Cases

- Attempting to log in with malicious-looking SQL input.
- Attempting to inject script-looking text into transaction memos.
- Attempting to access banking pages without a valid session.
- Tampering with the signed session cookie.
- Attempting to submit a sender account ID for another user.
- Submitting missing or invalid CSRF tokens.
- Attempting self-transfers, negative amounts, zero amounts, excessive amounts, or unknown recipients.
- Attempting to leak plaintext passwords or session tokens through audit events.

## Mitigations

- Argon2id password hashing.
- Generic login failure messages.
- Dummy password verification for missing users.
- Signed session cookies with expiry.
- HttpOnly and SameSite=Strict session cookies.
- CSRF tokens on state-changing forms.
- SQLAlchemy expression APIs for queries.
- Jinja2 autoescape globally enabled.
- No `|safe` usage in templates.
- CSP and other browser security headers.
- Server-side authorization from the authenticated session.
- Atomic transfer service with rollback on persistence failure.
- Audit logging for important auth, authorization, and transfer events.
- Static tests for raw SQL patterns, unsafe template filters, real financial identifiers, and committed secret material.

## Residual Risks

- This is a teaching lab and has not undergone production security review.
- Rate limiting and lockout settings are present as configuration placeholders but not implemented as a complete abuse-prevention system.
- SQLite is suitable for the local lab but not a production deployment choice.
- Docker runtime verification is pending until run on a Docker-capable machine or CI runner.
- Dependency and CodeQL automation are planned for later phases.
- ZAP baseline workflow is planned but not implemented yet.
