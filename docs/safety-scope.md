# Safety Scope

SecureBank Web Security Lab is a fictional, lab-only defensive security project.

## Allowed Scope

- Fictional users.
- Fictional accounts.
- Fictional integer lab-credit balances.
- Fictional transfers between seeded lab users.
- Local defensive tests.
- Harmless malicious-looking strings used only to prove defensive controls.
- Static safety scans.
- Recruiter and portfolio review.

## Prohibited Scope

- Real bank names, branding, or logos.
- Real customer data.
- Real money movement.
- Real payment integrations.
- Real account numbers, IBANs, SWIFT codes, routing numbers, or card numbers.
- Credential harvesting behavior.
- Exploit tooling.
- Attack instructions for third-party systems.
- Tests against systems outside this local lab.

## Safe Test Payloads

The test suite includes harmless strings that look like SQL or script input. They are local test data used only to verify escaping, parameterized queries, and defensive behavior.

These payloads must not be presented as attack instructions or used against third-party systems.

## Public Repository Safety

The repository is intended to be safe for public GitHub and recruiter review.

Safety checks include:

- No committed `.env`.
- No committed SQLite databases.
- No obvious committed secret material.
- No real financial identifier examples.
- No unallowlisted template `|safe` usage.
- No raw SQL string-concatenation patterns.
