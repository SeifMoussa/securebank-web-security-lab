# Changelog

All notable changes to this project will be documented here.

## Unreleased

- Confirmed GitHub Actions CI, Docker smoke, CodeQL, and ZAP baseline all pass on GitHub after the initial publish.
- Added release preparation notes, repository metadata, publishing commands, the v0.1.0 release plan, and a final local validation pass.
- Ran a final QA pass over repository structure, app flows, security controls, tests, and workflow configuration, plus local uvicorn smoke checks and general hygiene cleanup.
- Added GitHub Actions CI, CodeQL, an optional ZAP baseline workflow, Dependabot configuration, and a reusable documentation consistency check script.
- Rewrote README, threat model, security controls, OWASP mapping, testing guide, development guide, safety scope, ZAP review policy, and release checklist docs, and added documentation consistency tests.
- Added the Dockerfile, `.dockerignore`, Docker Compose runtime configuration, Linux and Windows smoke verification scripts, Docker artifact tests, and Docker development notes.
- Expanded defensive security tests: OWASP Top 10 mapping, SQL injection checks, XSS checks, access-control tests, CSRF tests, authentication security tests, audit logging tests, security header tests, and static safety scans.
- Added the fictional lab-credit account and transaction models, deterministic seed data, authenticated dashboard, transfer form, transaction history, atomic transfer service, authorization checks, audit events, templates, and tests.
- Added backend core: authentication, signed sessions, CSRF foundation, security headers, audit logging foundation, templates, and tests.
- Initial repository scaffold.
