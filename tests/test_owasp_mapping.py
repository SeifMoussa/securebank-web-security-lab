from pathlib import Path


def test_owasp_mapping_document_covers_all_categories() -> None:
    path = Path("docs/owasp-top-10-mapping.md")

    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "OWASP Top 10" in content
    for category in [
        "A01",
        "A02",
        "A03",
        "A04",
        "A05",
        "A06",
        "A07",
        "A08",
        "A09",
        "A10",
    ]:
        assert category in content
    assert "SSRF" in content
    assert "out of scope" in content
