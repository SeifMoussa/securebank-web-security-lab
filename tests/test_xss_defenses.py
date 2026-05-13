from pathlib import Path

from fastapi.testclient import TestClient

from .test_banking import login_demo_user, transfer


def test_jinja_autoescape_enabled(client: TestClient) -> None:
    template_env = client.app.state.templates.env

    assert template_env.autoescape("template.html") is True
    assert template_env.autoescape(None) is True
    template = template_env.from_string("{{ value }}")
    assert template.render(value="<script>alert(1)</script>") == (
        "&lt;script&gt;alert(1)&lt;/script&gt;"
    )


def test_templates_do_not_use_safe_filter() -> None:
    template_dir = Path("src/securebank/templates")

    safe_usages = [
        path for path in template_dir.rglob("*.html") if "|safe" in path.read_text(encoding="utf-8")
    ]

    assert safe_usages == []


def test_transaction_memo_script_looking_text_renders_escaped(seeded_client) -> None:
    login_demo_user(seeded_client, "alice")
    memo = "<script>alert('local-test')</script>"

    assert transfer(seeded_client, "bob", "10", memo).status_code == 303
    response = seeded_client.get("/transactions")

    assert response.status_code == 200
    assert memo not in response.text
    assert "&lt;script&gt;alert(&#39;local-test&#39;)&lt;/script&gt;" in response.text


def test_csp_header_supports_xss_mitigation_story(client: TestClient) -> None:
    response = client.get("/login")

    assert response.headers["Content-Security-Policy"] == "default-src 'self'"
