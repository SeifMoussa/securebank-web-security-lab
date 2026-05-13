import re

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from securebank.banking.service import TransferError, perform_transfer
from securebank.models import Account, AuditEvent, Transaction, User
from securebank.seed import DEMO_PASSWORD


def csrf_from_html(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match is not None
    return match.group(1)


def login_demo_user(client: TestClient, username: str = "alice") -> None:
    login_page = client.get("/login")
    csrf_token = csrf_from_html(login_page.text)
    response = client.post(
        "/login",
        data={"username": username, "password": DEMO_PASSWORD, "csrf_token": csrf_token},
        follow_redirects=False,
    )
    assert response.status_code == 303


def get_account(db: Session, username: str) -> Account:
    user = db.scalar(select(User).where(User.username == username))
    assert user is not None
    account = db.scalar(select(Account).where(Account.user_id == user.id))
    assert account is not None
    return account


def transfer(
    client: TestClient,
    recipient: str,
    amount: str,
    memo: str = "",
    extra: dict | None = None,
):
    transfer_page = client.get("/transfer")
    csrf_token = csrf_from_html(transfer_page.text)
    data = {
        "recipient_username": recipient,
        "amount_credits": amount,
        "memo": memo,
        "csrf_token": csrf_token,
    }
    if extra:
        data.update(extra)
    return client.post("/transfer", data=data, follow_redirects=False)


def test_seed_data_creates_users_and_accounts(seeded_db: Session) -> None:
    users = seeded_db.scalars(select(User).order_by(User.username)).all()
    accounts = seeded_db.scalars(select(Account)).all()

    assert [user.username for user in users] == ["alice", "bob", "carol"]
    assert len(accounts) == 3
    assert get_account(seeded_db, "alice").balance_credits == 5000
    assert get_account(seeded_db, "bob").balance_credits == 3000
    assert get_account(seeded_db, "carol").balance_credits == 2500


def test_authenticated_user_can_view_dashboard(seeded_client: TestClient) -> None:
    login_demo_user(seeded_client)

    response = seeded_client.get("/dashboard")

    assert response.status_code == 200
    assert "alice" in response.text
    assert "lab credits" in response.text


def test_unauthenticated_user_cannot_view_dashboard(seeded_client: TestClient) -> None:
    response = seeded_client.get("/dashboard", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_successful_transfer_updates_balances_and_records_transaction(
    seeded_client: TestClient,
    seeded_db: Session,
) -> None:
    login_demo_user(seeded_client, "alice")
    alice_before = get_account(seeded_db, "alice").balance_credits
    bob_before = get_account(seeded_db, "bob").balance_credits

    response = transfer(seeded_client, "bob", "250", "Phase 3 lab memo")

    seeded_db.expire_all()
    assert response.status_code == 303
    assert get_account(seeded_db, "alice").balance_credits == alice_before - 250
    assert get_account(seeded_db, "bob").balance_credits == bob_before + 250
    transaction = seeded_db.scalar(
        select(Transaction).where(Transaction.memo == "Phase 3 lab memo")
    )
    assert transaction is not None
    assert transaction.amount_credits == 250


def test_insufficient_funds_does_not_change_balances(
    seeded_client: TestClient,
    seeded_db: Session,
) -> None:
    login_demo_user(seeded_client, "alice")
    alice_before = get_account(seeded_db, "alice").balance_credits
    bob_before = get_account(seeded_db, "bob").balance_credits

    response = transfer(seeded_client, "bob", "999999", "too much")

    seeded_db.expire_all()
    assert response.status_code == 400
    assert get_account(seeded_db, "alice").balance_credits == alice_before
    assert get_account(seeded_db, "bob").balance_credits == bob_before


def test_invalid_recipient_does_not_change_balances(
    seeded_client: TestClient,
    seeded_db: Session,
) -> None:
    login_demo_user(seeded_client, "alice")
    alice_before = get_account(seeded_db, "alice").balance_credits

    response = transfer(seeded_client, "missing_user", "25")

    seeded_db.expire_all()
    assert response.status_code == 400
    assert get_account(seeded_db, "alice").balance_credits == alice_before


def test_self_transfer_rejected(seeded_client: TestClient, seeded_db: Session) -> None:
    login_demo_user(seeded_client, "alice")
    alice_before = get_account(seeded_db, "alice").balance_credits

    response = transfer(seeded_client, "alice", "25")

    seeded_db.expire_all()
    assert response.status_code == 400
    assert get_account(seeded_db, "alice").balance_credits == alice_before


@pytest.mark.parametrize("amount", ["0", "-5"])
def test_zero_or_negative_amount_rejected(
    seeded_client: TestClient,
    seeded_db: Session,
    amount: str,
) -> None:
    login_demo_user(seeded_client, "alice")
    alice_before = get_account(seeded_db, "alice").balance_credits

    response = transfer(seeded_client, "bob", amount)

    seeded_db.expire_all()
    assert response.status_code == 400
    assert get_account(seeded_db, "alice").balance_credits == alice_before


def test_memo_is_stored_and_rendered_escaped(
    seeded_client: TestClient,
    seeded_db: Session,
) -> None:
    login_demo_user(seeded_client, "alice")
    memo = "<script>alert(1)</script>"

    response = transfer(seeded_client, "bob", "10", memo)
    transactions_page = seeded_client.get("/transactions")

    assert response.status_code == 303
    transaction = seeded_db.scalar(select(Transaction).where(Transaction.memo == memo))
    assert transaction is not None
    assert memo not in transactions_page.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in transactions_page.text


def test_user_cannot_transfer_from_another_users_account(
    seeded_client: TestClient,
    seeded_db: Session,
) -> None:
    login_demo_user(seeded_client, "alice")
    alice_before = get_account(seeded_db, "alice").balance_credits
    bob_before = get_account(seeded_db, "bob").balance_credits
    carol_before = get_account(seeded_db, "carol").balance_credits
    bob_account_id = get_account(seeded_db, "bob").id

    response = transfer(
        seeded_client,
        "carol",
        "50",
        "ignored account id",
        extra={"sender_account_id": str(bob_account_id)},
    )

    seeded_db.expire_all()
    assert response.status_code == 303
    assert get_account(seeded_db, "alice").balance_credits == alice_before - 50
    assert get_account(seeded_db, "bob").balance_credits == bob_before
    assert get_account(seeded_db, "carol").balance_credits == carol_before + 50


def test_transfer_rollback_leaves_balances_unchanged_if_transaction_creation_fails(
    seeded_db: Session,
    monkeypatch,
) -> None:
    alice = seeded_db.scalar(select(User).where(User.username == "alice"))
    assert alice is not None
    alice_before = get_account(seeded_db, "alice").balance_credits
    bob_before = get_account(seeded_db, "bob").balance_credits

    def fail_create_transaction(*args, **kwargs):
        raise RuntimeError("simulated transaction creation failure")

    monkeypatch.setattr(
        "securebank.banking.service.create_transaction_record", fail_create_transaction
    )

    with pytest.raises(TransferError) as exc_info:
        perform_transfer(seeded_db, alice, "bob", "75", "rollback test")

    seeded_db.expire_all()
    assert exc_info.value.reason == "transfer_rollback"
    assert get_account(seeded_db, "alice").balance_credits == alice_before
    assert get_account(seeded_db, "bob").balance_credits == bob_before


def test_transfer_audit_events_emitted(
    seeded_client: TestClient,
    seeded_db: Session,
) -> None:
    login_demo_user(seeded_client, "alice")

    assert transfer(seeded_client, "bob", "10").status_code == 303
    assert transfer(seeded_client, "bob", "999999").status_code == 400
    assert transfer(seeded_client, "missing_user", "10").status_code == 400

    events = seeded_db.scalars(select(AuditEvent)).all()
    event_types = {event.event_type for event in events}
    assert "transfer_success" in event_types
    assert "transfer_insufficient_funds" in event_types
    assert "transfer_recipient_not_found" in event_types
