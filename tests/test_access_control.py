from sqlalchemy import select
from sqlalchemy.orm import Session

from securebank.models import Account, AuditEvent

from .test_banking import get_account, login_demo_user, transfer


def test_authenticated_page_redirects_without_session(client, db_session: Session) -> None:
    response = client.get("/me", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    events = db_session.scalars(select(AuditEvent)).all()
    assert any(event.event_type == "authz_denied" for event in events)


def test_banking_pages_redirect_without_session(seeded_client, seeded_db: Session) -> None:
    for path in ["/dashboard", "/transfer", "/transactions"]:
        response = seeded_client.get(path, follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/login"

    events = seeded_db.scalars(select(AuditEvent)).all()
    assert len([event for event in events if event.event_type == "authz_denied"]) >= 3


def test_tampered_session_cannot_access_banking_pages(seeded_client, seeded_db: Session) -> None:
    seeded_client.cookies.set("securebank_lab_session", "tampered-session")

    response = seeded_client.get("/dashboard", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    events = seeded_db.scalars(select(AuditEvent)).all()
    assert any(event.event_type == "authz_denied" for event in events)


def test_user_dashboard_does_not_expose_other_user_balance(seeded_client) -> None:
    login_demo_user(seeded_client, "alice")

    response = seeded_client.get("/dashboard")

    assert response.status_code == 200
    assert "5000 lab credits" in response.text
    assert "3000 lab credits" not in response.text
    assert "2500 lab credits" not in response.text


def test_submitted_sender_account_id_does_not_change_authorized_sender(
    seeded_client,
    seeded_db: Session,
) -> None:
    login_demo_user(seeded_client, "alice")
    alice_before = get_account(seeded_db, "alice").balance_credits
    bob_before = get_account(seeded_db, "bob").balance_credits
    bob_account = get_account(seeded_db, "bob")

    response = transfer(
        seeded_client,
        "carol",
        "25",
        "sender id ignored",
        extra={"sender_account_id": str(bob_account.id)},
    )

    seeded_db.expire_all()
    assert response.status_code == 303
    assert get_account(seeded_db, "alice").balance_credits == alice_before - 25
    assert seeded_db.get(Account, bob_account.id).balance_credits == bob_before
