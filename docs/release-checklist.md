# Release Checklist

Use this checklist before tagging a new release. It is a working template, not a log of past releases — see `TESTING_REPORT.md` and `CHANGELOG.md` for what has already shipped.

## Local Checks

- [ ] `python -m pytest` passes.
- [ ] `python -m pytest --cov=securebank --cov-report=term-missing --cov-fail-under=80` passes.
- [ ] `python -m ruff check .` passes.
- [ ] `python -m ruff format --check .` passes.
- [ ] `python scripts/check-docs.py` passes.
- [ ] CHANGELOG, TESTING_REPORT, and SECURITY_NOTES reflect the current state.
- [ ] README badges and local doc links resolve.

## GitHub Checks

- [ ] GitHub Actions CI is green on the release branch.
- [ ] CodeQL is green.
- [ ] ZAP baseline is green, and any WARN/MEDIUM findings have been reviewed.
- [ ] Dependabot has no unreviewed open alerts.

## Docker

- [ ] `docker compose build` and `docker compose up -d` succeed.
- [ ] `/healthz` responds after `docker compose up -d`.
- [ ] Smoke scripts (`scripts/verify-docker.sh`, `scripts/smoke-test.ps1`) pass.

## Safety Checks

- [ ] No real customer data, banking identifiers, payment integrations, or money movement introduced.
- [ ] No `.env` or local SQLite database committed.
- [ ] No offensive tooling added.

## Before Tagging

- [ ] Review the full diff since the last tag.
- [ ] Confirm the version bump in `pyproject.toml`.
- [ ] Only then create the GitHub release.
