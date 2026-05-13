# Release Checklist

Phase 9 release preparation is complete locally. Do not publish, tag, or create a release until manual approval is given.

## Local Completion

- [x] Code complete for v0.1.0 release candidate.
- [x] Tests passing locally.
- [x] Coverage passing locally.
- [x] Ruff lint passing locally.
- [x] Ruff format check passing locally.
- [x] Documentation complete for current scope.
- [x] README honest and complete.
- [x] CHANGELOG updated.
- [x] TESTING_REPORT updated.
- [x] SECURITY_NOTES updated.
- [x] RELEASE.md created.
- [x] No fake screenshots included.

## Configured But Pending GitHub Verification

- [x] GitHub Actions CI workflow configured.
- [x] GitHub Actions CI verified on GitHub.
- [x] CodeQL workflow configured.
- [x] CodeQL verified on GitHub.
- [x] ZAP baseline workflow configured.
- [x] ZAP baseline verified on GitHub.
- [x] Dependabot configured.
- [x] Dependabot initial update checks ran on GitHub.

## Docker And ZAP Runtime

- [x] Dockerfile implemented.
- [x] Docker Compose implemented.
- [x] Docker smoke scripts implemented.
- [x] Docker runtime verified through GitHub Actions.
- [x] ZAP runtime verified through GitHub Actions.

Docker runtime remains unavailable locally because Docker is not installed or not on PATH, but it has been verified through GitHub Actions.

## Safety Checks

- [x] No real customer data.
- [x] No real banking identifiers.
- [x] No real payment integrations.
- [x] No real money movement.
- [x] No offensive tooling.
- [x] Safe test payload language documented.
- [x] No `.env` committed.
- [x] No SQLite database should be committed.
- [x] Local ignored `securebank_lab.sqlite3` is development runtime state only.

## Pending First-Push Items

- Confirm README badges resolve.
- Review any CodeQL, Dependabot, or ZAP findings.
- Add real screenshots if desired.
- Only then prepare and publish a GitHub release.
