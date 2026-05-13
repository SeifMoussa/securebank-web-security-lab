import re
from pathlib import Path

TEXT_FILE_SUFFIXES = {
    ".css",
    ".html",
    ".md",
    ".py",
    ".ps1",
    ".toml",
    ".txt",
    ".yml",
    ".yaml",
}


def repo_text_files() -> list[Path]:
    ignored_parts = {".git", ".pytest_cache", ".ruff_cache", "__pycache__"}
    files = []
    for path in Path(".").rglob("*"):
        if any(part in ignored_parts for part in path.parts):
            continue
        if path.is_file() and path.suffix in TEXT_FILE_SUFFIXES:
            files.append(path)
    return files


def test_no_raw_sql_string_concatenation_patterns() -> None:
    patterns = [
        r"\.execute\(f[\"']",
        r"\.execute\([\"'][^\"']*(SELECT|INSERT|UPDATE|DELETE)",
        r"(SELECT|INSERT|UPDATE|DELETE).*\+",
        r"%\s*\(",
    ]
    findings = []
    for path in Path("src/securebank").rglob("*.py"):
        content = path.read_text(encoding="utf-8")
        findings.extend((str(path), pattern) for pattern in patterns if re.search(pattern, content))

    assert findings == []


def test_no_unallowlisted_safe_filter_usage() -> None:
    findings = [
        str(path)
        for path in Path("src/securebank/templates").rglob("*.html")
        if "|safe" in path.read_text(encoding="utf-8")
    ]

    assert findings == []


def test_no_real_financial_identifier_examples() -> None:
    iban_like = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")
    long_digit_sequence = re.compile(r"\b\d{12,19}\b")
    findings = []
    for path in repo_text_files():
        content = path.read_text(encoding="utf-8")
        if iban_like.search(content) or long_digit_sequence.search(content):
            findings.append(str(path))

    assert findings == []


def test_no_committed_secret_material() -> None:
    secret_patterns = [
        "".join(("BEGIN", " PRIVATE KEY")),
        "".join(("AWS", "_SECRET_ACCESS_KEY")),
        "".join(("gh", "p_")),
        "".join(("s", "k-")),
        "".join(("xo", "xb-")),
    ]
    findings = []
    for path in repo_text_files():
        content = path.read_text(encoding="utf-8")
        findings.extend((str(path), pattern) for pattern in secret_patterns if pattern in content)

    assert findings == []
