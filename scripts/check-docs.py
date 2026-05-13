"""Documentation consistency checks for SecureBank Web Security Lab."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    Path("README.md"),
    Path("SECURITY_NOTES.md"),
    Path("TESTING_REPORT.md"),
    Path("PROJECT_COMPLETION_CHECKLIST.md"),
    Path("docs/threat-model.md"),
    Path("docs/security-controls.md"),
    Path("docs/owasp-top-10-mapping.md"),
    Path("docs/testing-guide.md"),
    Path("docs/development-guide.md"),
    Path("docs/zap-review-policy.md"),
    Path("docs/safety-scope.md"),
]

DOC_GLOBS = [
    Path("README.md"),
    Path("SECURITY_NOTES.md"),
    Path("TESTING_REPORT.md"),
    Path("PROJECT_COMPLETION_CHECKLIST.md"),
    *Path("docs").glob("*.md"),
]


def read(path: Path) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def fail(message: str) -> None:
    raise AssertionError(message)


def all_docs_text() -> str:
    return "\n".join(read(path) for path in DOC_GLOBS if (ROOT / path).exists())


def check_required_docs() -> None:
    missing = [str(path) for path in REQUIRED_DOCS if not (ROOT / path).exists()]
    if missing:
        fail(f"Missing required docs: {', '.join(missing)}")


def check_readme_local_links() -> None:
    readme = read(Path("README.md"))
    links = re.findall(r"\]\(([^)]+)\)", readme)
    missing = []
    for link in links:
        if link.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = ROOT / link.split("#", 1)[0]
        if not target.exists():
            missing.append(link)
    if missing:
        fail(f"README has missing local links: {', '.join(missing)}")


def check_documented_commands() -> None:
    docs = all_docs_text()
    makefile = read(Path("Makefile"))
    pyproject = read(Path("pyproject.toml"))
    required_commands = [
        "python -m pytest",
        "python -m ruff check .",
        "python -m ruff format --check .",
        "python -m uvicorn securebank.main:app --reload",
    ]
    missing = [command for command in required_commands if command not in docs]
    if missing:
        fail(f"Docs are missing expected commands: {', '.join(missing)}")

    for target in ["test:", "lint:", "format-check:"]:
        if target not in makefile:
            fail(f"Makefile missing target {target}")
    if 'testpaths = ["tests"]' not in pyproject:
        fail("pyproject.toml pytest testpaths setting was not found")


def check_status_honesty() -> None:
    docs = all_docs_text().lower()
    required_phrases = [
        "docker runtime verification is pending",
        "github actions ci is configured but not yet verified on github",
        "codeql is configured but not yet verified on github",
        "zap baseline workflow is configured but not yet verified",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in docs]
    if missing:
        fail(f"Docs are missing status honesty phrases: {', '.join(missing)}")

    prohibited_phrases = [
        "docker runtime verification passed",
        "ci passed",
        "github actions passed",
        "codeql passed",
        "zap passed",
    ]
    found = [phrase for phrase in prohibited_phrases if phrase in docs]
    if found:
        fail(f"Docs contain premature success claims: {', '.join(found)}")


def check_financial_identifier_examples() -> None:
    docs = all_docs_text()
    iban_like = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")
    long_digit_sequence = re.compile(r"\b\d{12,19}\b")
    if iban_like.search(docs):
        fail("Docs contain an IBAN-like identifier")
    if long_digit_sequence.search(docs):
        fail("Docs contain a long card/account-number-like digit sequence")


def main() -> int:
    checks = [
        check_required_docs,
        check_readme_local_links,
        check_documented_commands,
        check_status_honesty,
        check_financial_identifier_examples,
    ]
    for check in checks:
        check()
    print("Documentation checks passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"Documentation check failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
