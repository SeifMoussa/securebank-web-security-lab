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
- [ ] GitHub Actions CI verified on GitHub.
- [x] CodeQL workflow configured.
- [ ] CodeQL verified on GitHub.
- [x] ZAP baseline workflow configured.
- [ ] ZAP baseline verified on GitHub.
- [x] Dependabot configured.
- [ ] Dependabot verified on GitHub.

## Docker And ZAP Runtime

- [x] Dockerfile implemented.
- [x] Docker Compose implemented.
- [x] Docker smoke scripts implemented.
- [ ] Docker runtime verified.
- [ ] ZAP runtime verified.

Docker runtime remains pending locally because Docker is not installed or not on PATH.

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

- Push repository to GitHub.
- Confirm README badges resolve.
- Confirm CI workflow runs.
- Confirm CodeQL workflow runs.
- Confirm Docker smoke job runs.
- Manually run ZAP baseline workflow.
- Review any CodeQL, Dependabot, or ZAP findings.
- Add real screenshots if desired.
- Only then prepare and publish a GitHub release.
