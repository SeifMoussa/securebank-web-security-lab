# OWASP ZAP Review Policy

OWASP ZAP baseline scanning is configured as a separate optional workflow. It is not yet verified on GitHub.

Planned policy:

- ZAP runs as a separate optional workflow, not as the default fast test path.
- HIGH findings fail the ZAP job.
- WARN and MEDIUM findings are documented for human review.
- Findings are evaluated in the context of this fictional local lab.
- The workflow must not be presented as exploit tooling.
- The workflow must not target third-party systems.

Current status:

- ZAP baseline workflow is configured but not yet verified until its first GitHub run.
- No ZAP runtime result is claimed.
- Docker runtime verification is still pending locally.

The configured workflow starts the local Docker Compose lab app and runs the baseline scan against `http://localhost:8000`. It is defensive scanning of this repository's local lab app only.
