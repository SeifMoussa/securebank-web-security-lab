from sqlalchemy import select
from sqlalchemy.orm import Session

from securebank.models import AuditEvent

from .test_auth import login, register
from .test_banking import login_demo_user, transfer


def test_logout_audit_event(client, db_session: Session) -> None:
    assert register(client).status_code == 303
    assert login(client).status_code == 303
    response = client.get("/me")
    csrf_token = response.text.split('name="csrf_token" value="', 1)[1].split('"', 1)[0]

    assert client.post("/logout", data={"csrf_token": csrf_token}).status_code == 200

    events = db_session.scalars(select(AuditEvent)).all()
    assert "logout" in {event.event_type for event in events}
    assert all(event.request_id for event in events)


def test_register_success_and_failure_audit_events(client, db_session: Session) -> None:
    assert register(client).status_code == 303
    assert register(client).status_code == 400

    events = db_session.scalars(select(AuditEvent)).all()
    event_types = {event.event_type for event in events}
    assert "register_success" in event_types
    assert "register_failure" in event_types


def test_transfer_and_authz_audit_events(seeded_client, seeded_db: Session) -> None:
    assert seeded_client.get("/dashboard", follow_redirects=False).status_code == 303
    login_demo_user(seeded_client, "alice")
    assert transfer(seeded_client, "bob", "10", "audit success").status_code == 303
    assert transfer(seeded_client, "bob", "999999", "audit insufficient").status_code == 400
    assert transfer(seeded_client, "missing_user", "10", "audit recipient").status_code == 400
    assert transfer(seeded_client, "alice", "10", "audit failure").status_code == 400

    events = seeded_db.scalars(select(AuditEvent)).all()
    event_types = {event.event_type for event in events}
    assert {
        "authz_denied",
        "transfer_success",
        "transfer_insufficient_funds",
        "transfer_recipient_not_found",
        "transfer_failure",
    } <= event_types


def test_audit_events_do_not_contain_passwords_or_session_secrets(
    client,
    db_session: Session,
    settings,
) -> None:
    password = "StrongPass123!"
    assert register(client, password=password).status_code == 303
    login_response = login(client, password=password)
    assert login_response.status_code == 303
    session_cookie = client.cookies.get(settings.session_cookie_name)
    assert session_cookie is not None

    events = db_session.scalars(select(AuditEvent)).all()
    serialized_events = "\n".join(
        f"{event.event_type} {event.username} {event.user_id} {event.request_id} {event.detail}"
        for event in events
    )
    assert password not in serialized_events
    assert session_cookie not in serialized_events
