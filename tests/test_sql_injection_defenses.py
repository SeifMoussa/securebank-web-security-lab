"""SQL injection defense tests."""

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from securebank.models import Transaction

from .test_auth import login
from .test_banking import login_demo_user, transfer

SQLI_LOOKING_INPUT = "' OR '1'='1"


def test_application_code_does_not_use_raw_sql_execution_or_concatenation() -> None:
    source_files = Path("src/securebank").rglob("*.py")
    raw_sql_markers = [
        " text(",
        "=text(",
        "(text(",
        "exec_driver_sql",
        ".execute(f",
        ".execute(",
        '.execute("SELECT',
        ".execute('SELECT",
        "SELECT *",
        "WHERE username = '",
    ]

    findings = []
    for path in source_files:
        content = path.read_text(encoding="utf-8")
        findings.extend((str(path), marker) for marker in raw_sql_markers if marker in content)

    assert findings == []


def test_login_payload_does_not_authenticate_user(seeded_client) -> None:
    response = login(seeded_client, username=SQLI_LOOKING_INPUT, password=SQLI_LOOKING_INPUT)

    assert response.status_code == 400
    assert "Invalid username or password." in response.text
    assert seeded_client.get("/dashboard", follow_redirects=False).status_code == 303


def test_transfer_recipient_payload_is_treated_as_data_not_sql(
    seeded_client,
    seeded_db: Session,
) -> None:
    login_demo_user(seeded_client, "alice")
    before_count = len(seeded_db.scalars(select(Transaction)).all())

    response = transfer(seeded_client, SQLI_LOOKING_INPUT, "10", "recipient lookup test")

    assert response.status_code == 400
    assert "Recipient was not found." in response.text
    assert len(seeded_db.scalars(select(Transaction)).all()) == before_count


def test_memo_can_store_malicious_looking_string_as_text(
    seeded_client,
    seeded_db: Session,
) -> None:
    login_demo_user(seeded_client, "alice")
    memo = "' OR '1'='1; DROP TABLE users; --"

    response = transfer(seeded_client, "bob", "15", memo)

    assert response.status_code == 303
    transaction = seeded_db.scalar(select(Transaction).where(Transaction.memo == memo))
    assert transaction is not None
    assert transaction.memo == memo


def test_sqlalchemy_parameterized_query_style_is_used_for_lookups() -> None:
    auth_service = Path("src/securebank/auth/service.py").read_text(encoding="utf-8")
    banking_service = Path("src/securebank/banking/service.py").read_text(encoding="utf-8")

    assert "select(User).where(User.username == username)" in auth_service
    assert "select(User).where(User.username == normalized_recipient)" in banking_service
    assert 'f"SELECT' not in auth_service + banking_service
    assert "f'SELECT" not in auth_service + banking_service
