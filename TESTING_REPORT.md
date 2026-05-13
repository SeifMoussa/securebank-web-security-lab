# Testing Report

## Phase 2 Results

Date: 2026-05-13

Commands run:

- `python -m pytest`
- `python -m ruff check .`
- `python -m ruff format --check .`

Results:

- pytest: 27 passed
- ruff lint: all checks passed
- ruff format check: 33 files already formatted

Coverage areas added:

- Health endpoints
- Settings loading
- Argon2id password hashing and verification
- Dummy password verification path for missing users
- Registration password storage
- Login success and failure behavior
- Signed session cookie behavior
- Logout cookie clearing
- Tampered session rejection
- CSRF valid, missing, and invalid token behavior
- Security headers
- Jinja2 autoescape and absence of `|safe`
- Audit event creation without plaintext passwords
- Basic Phase 2 SQL raw-execution hygiene check

Not yet covered:

- Banking transfer logic, balances, and transaction history
- Full Phase 4 SQL injection malicious-input-as-data tests
- Docker smoke verification
- CI, CodeQL, and ZAP workflows

## Phase 3 Results

Date: 2026-05-13

Commands run:

- `python -m pytest`
- `python -m ruff check .`
- `python -m ruff format --check .`

Results:

- pytest: 40 passed
- ruff lint: all checks passed
- ruff format check: 35 files already formatted

Coverage areas added:

- Deterministic fictional seed users and lab-credit accounts
- Authenticated dashboard access
- Unauthenticated dashboard redirect
- Successful fictional transfer balance updates
- Transaction record creation
- Insufficient funds rollback behavior
- Invalid recipient rollback behavior
- Self-transfer rejection
- Zero and negative amount rejection
- Memo storage and escaped rendering
- Submitted sender account ID ignored in favor of authenticated session user
- Transfer rollback when transaction creation fails
- Transfer audit events for success, insufficient funds, and recipient not found

Not yet covered:

- Full Phase 4 SQL injection malicious-input-as-data expansion
- Broader OWASP mapping tests
- Docker smoke verification
- CI, CodeQL, and ZAP workflows

## Phase 4 Results

Date: 2026-05-13

Commands run:

- `python -m pytest`
- `python -m ruff check .`
- `python -m ruff format --check .`

Results:

- pytest: 62 passed
- ruff lint: all checks passed
- ruff format check: 36 files already formatted

Coverage areas added or strengthened:

- SQL injection defensive behavior tests for login and transfer lookups.
- Malicious-looking memo input stored as ordinary text.
- Static scan for raw SQL execution and string-concatenation patterns.
- Static and behavioral XSS tests for Jinja2 autoescape, escaped memos, no `|safe`, and CSP.
- Access control and IDOR tests for protected banking pages, tampered sessions, other-user balance exposure, and ignored sender account fields.
- CSRF tests for transfer and logout, plus existing login/register coverage.
- Authentication tests for Argon2id storage, generic login failures, dummy verification, logout, and tampered sessions.
- Security header tests including HSTS enabled and disabled behavior.
- Audit logging tests for register, login, logout, transfer, insufficient funds, recipient not found, authz denied, and sensitive-data exclusion.
- OWASP Top 10 mapping coverage for A01-A10.
- Static safety scans for unsafe templates, raw SQL patterns, real financial identifier examples, and committed secret material.

Not yet covered:

- Docker smoke verification.
- GitHub Actions CI.
- CodeQL workflow.
- Optional ZAP baseline workflow.

## Phase 5 Results

Date: 2026-05-13

Commands run:

- `docker --version`
- `docker compose config`
- PowerShell syntax check for `scripts/smoke-test.ps1`
- Conditional shell syntax check for `scripts/verify-docker.sh`
- Static `.dockerignore` required-entry check
- `python -m pytest`
- `python -m ruff check .`
- `python -m ruff format --check .`

Results:

- Docker runtime verification: pending because `docker` is not installed or not on PATH in this environment.
- PowerShell smoke script syntax: passed.
- Shell smoke script syntax: skipped because `bash` is not available in this environment.
- `.dockerignore` required-entry check: passed.
- pytest: 65 passed.
- ruff lint: all checks passed.
- ruff format check: 37 files already formatted.

Coverage areas added:

- Dockerfile static contract test.
- `.dockerignore` static coverage test.
- Docker Compose static configuration test.
- Linux/GitHub Actions smoke script.
- Windows PowerShell smoke script.

Pending:

- Actual `docker compose config`.
- Actual `docker compose build`.
- Actual `docker compose up -d`.
- Runtime HTTP checks against containerized `/healthz`, `/login`, `/register`, and unauthenticated `/dashboard`.
- Docker logs and `docker compose ps` review.

## Phase 6 Results

Date: 2026-05-13

Commands run:

- Documentation consistency tests through `python -m pytest`
- `python -m pytest`
- `python -m ruff check .`
- `python -m ruff format --check .`

Results:

- Documentation pages rewritten or expanded for current Phase 6 status.
- Documentation consistency tests added for local links, command references, status honesty, and financial identifier checks.
- Docker runtime verification remains pending because Docker is not installed or not on PATH in this environment.
- GitHub Actions CI, CodeQL, and ZAP workflow remain pending and are not claimed as implemented.
- pytest: 69 passed.
- ruff lint: all checks passed.
- ruff format check: 38 files already formatted.

## Phase 7 Results

Date: 2026-05-13

Commands run:

- `python scripts/check-docs.py`
- `python -m py_compile scripts/check-docs.py`
- Workflow YAML parse check with Python/PyYAML
- PowerShell syntax check for `scripts/smoke-test.ps1`
- Conditional shell syntax check for `scripts/verify-docker.sh`
- `docker --version`
- `python -m pytest`
- `python -m ruff check .`
- `python -m ruff format --check .`
- `python -m pytest --cov=securebank --cov-report=term-missing --cov-fail-under=80`

Results:

- GitHub Actions workflow files created locally.
- CodeQL workflow file created locally.
- ZAP baseline workflow file created locally.
- Dependabot configuration created locally.
- Documentation check script passed.
- `scripts/check-docs.py` compiled successfully.
- Workflow YAML parsed successfully.
- PowerShell smoke script syntax passed.
- Shell smoke script syntax skipped because `bash` is not available in this environment.
- Docker runtime verification remains pending because `docker` is not installed or not on PATH in this environment.
- pytest: 70 passed.
- ruff lint: all checks passed.
- ruff format check: 39 files already formatted.
- coverage: 96.02%, above the 80% CI threshold.

Pending:

- GitHub Actions CI execution on GitHub.
- CodeQL execution on GitHub.
- ZAP baseline execution on GitHub.
- Docker runtime smoke verification on GitHub Actions or another Docker-capable machine.

## Phase 8 Results

Date: 2026-05-14

Commands and checks run:

- Repository structure audit for required files and folders.
- Application and security QA script using FastAPI `TestClient`.
- Workflow QA script parsing GitHub Actions and Dependabot YAML.
- Docker availability checks: `docker --version` and `docker compose config`.
- Local uvicorn smoke check for `/healthz`, `/login`, and `/register`.
- Hygiene checks for local artifacts and documentation overclaims.
- `python -m pytest`
- `python -m pytest --cov=securebank --cov-report=term-missing --cov-fail-under=80`
- `python -m ruff check .`
- `python -m ruff format --check .`
- `python scripts/check-docs.py`
- `python -m py_compile scripts/check-docs.py`

Results:

- Repository structure audit: passed.
- Application QA: passed.
- Security QA: passed.
- Workflow QA: passed.
- Documentation QA: passed.
- Local uvicorn smoke: passed and process stopped.
- Docker runtime verification: pending because `docker` is not installed or not on PATH.
- ZAP runtime verification: pending until GitHub Actions or another Docker-capable machine.
- pytest: 70 passed.
- coverage: 96.02%, above the 80% threshold.
- ruff lint: all checks passed.
- ruff format check: 39 files already formatted.
- Documentation checks: passed.

Notes:

- Temporary Phase 8 QA SQLite databases were removed.
- A local ignored `securebank_lab.sqlite3` remains as development runtime state.
- Local `.pytest_cache` and `.ruff_cache` exist as ignored tool cache folders.

## Phase 9 Results

Date: 2026-05-14

Commands and checks run:

- `python -m pytest`
- `python -m pytest --cov=securebank --cov-report=term-missing --cov-fail-under=80`
- `python -m ruff check .`
- `python -m ruff format --check .`
- `python scripts/check-docs.py`
- `python -m py_compile scripts/check-docs.py`
- Git hygiene checks for local artifacts, secrets, and financial identifiers.

Results:

- Release preparation materials created.
- GitHub publishing commands prepared but not executed.
- v0.1.0 release plan prepared but not executed.
- Portfolio outputs prepared.
- Docker runtime verification remains pending because Docker is not installed or not on PATH.
- GitHub Actions CI, CodeQL, ZAP, and Dependabot remain pending until first GitHub run.

Final command results are recorded in the Phase 9 final report.
