import importlib.util
import re
from pathlib import Path

DOC_PATHS = [
    Path("README.md"),
    *Path("docs").glob("*.md"),
]


def read_docs() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in DOC_PATHS)


def test_readme_local_doc_links_exist() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    links = re.findall(r"\]\((docs/[^)]+\.md|LICENSE)\)", readme)

    assert links
    assert all(Path(link).exists() for link in links)


def test_documented_commands_match_makefile_and_pyproject() -> None:
    docs = read_docs()
    makefile = Path("Makefile").read_text(encoding="utf-8")
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")

    for command in [
        "python -m pytest",
        "python -m ruff check .",
        "python -m ruff format --check .",
        "python -m uvicorn securebank.main:app --reload",
    ]:
        assert command in docs

    assert "test:" in makefile
    assert "lint:" in makefile
    assert "format-check:" in makefile
    assert 'testpaths = ["tests"]' in pyproject


def test_docs_keep_runtime_and_ci_status_honest() -> None:
    docs = read_docs().lower()

    assert "docker runtime verification is pending" in docs
    assert "github actions ci is configured but not yet verified on github" in docs
    assert "codeql is configured but not yet verified on github" in docs
    assert "zap baseline workflow is configured but not yet verified" in docs
    assert "docker runtime: pending locally" in docs
    assert "docker runtime verification passed" not in docs
    assert "ci passed" not in docs
    assert "codeql passed" not in docs
    assert "zap passed" not in docs


def test_docs_do_not_include_real_financial_identifier_examples() -> None:
    docs = read_docs()
    iban_like = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")
    long_digit_sequence = re.compile(r"\b\d{12,19}\b")

    assert iban_like.search(docs) is None
    assert long_digit_sequence.search(docs) is None


def test_reusable_docs_check_script_passes() -> None:
    script_path = Path("scripts/check-docs.py")
    spec = importlib.util.spec_from_file_location("check_docs", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.main() == 0
