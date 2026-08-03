import re

import pyotp
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from securebank.auth.service import activate_mfa
from securebank.config import Settings
from securebank.models import AuditEvent, MfaRecoveryCode, User
from securebank.security.mfa import generate_totp_secret, verify_totp_code
from securebank.seed import DEMO_ADMIN_PASSWORD, DEMO_ADMIN_USERNAME, DEMO_PASSWORD

DEFAULT_RECOVERY_CODE_COUNT = Settings().mfa_recovery_code_count


def csrf_from_html(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match is not None
    return match.group(1)


def start_admin_login(client: TestClient):
    login_page = client.get("/login")
    csrf_token = csrf_from_html(login_page.text)
    return client.post(
        "/login",
        data={
            "username": DEMO_ADMIN_USERNAME,
            "password": DEMO_ADMIN_PASSWORD,
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )


def submit_enroll_code(client: TestClient, code: str):
    enroll_page = client.get("/mfa/enroll")
    csrf_token = csrf_from_html(enroll_page.text)
    return client.post(
        "/mfa/enroll",
        data={"code": code, "csrf_token": csrf_token},
        follow_redirects=False,
    )


def submit_challenge_code(client: TestClient, code: str):
    challenge_page = client.get("/mfa/challenge")
    csrf_token = csrf_from_html(challenge_page.text)
    return client.post(
        "/mfa/challenge",
        data={"code": code, "csrf_token": csrf_token},
        follow_redirects=False,
    )


def extract_secret(enroll_html: str) -> str:
    match = re.search(r"Secret: <code>([A-Z2-7]+)</code>", enroll_html)
    assert match is not None
    return match.group(1)


def extract_recovery_codes(html: str) -> list[str]:
    return re.findall(r"<li><code>([2-9A-HJ-NP-Z]{10})</code></li>", html)


def enroll_admin(client: TestClient) -> list[str]:
    """Log in as the demo admin and complete MFA enrollment, returning recovery codes."""
    response = start_admin_login(client)
    assert response.status_code == 303
    assert response.headers["location"] == "/mfa/enroll"

    enroll_page = client.get("/mfa/enroll")
    secret = extract_secret(enroll_page.text)
    code = pyotp.TOTP(secret, interval=30).now()

    response = submit_enroll_code(client, code)
    assert response.status_code == 200
    return extract_recovery_codes(response.text)


def test_customer_login_is_not_affected_by_mfa(seeded_client: TestClient) -> None:
    login_page = seeded_client.get("/login")
    csrf_token = csrf_from_html(login_page.text)

    response = seeded_client.post(
        "/login",
        data={"username": "alice", "password": DEMO_PASSWORD, "csrf_token": csrf_token},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/me"


def test_admin_login_without_mfa_redirects_to_enrollment(seeded_client: TestClient) -> None:
    response = start_admin_login(seeded_client)

    assert response.status_code == 303
    assert response.headers["location"] == "/mfa/enroll"
    assert "securebank_lab_session" not in response.headers.get("set-cookie", "")


def test_enrollment_with_correct_code_activates_mfa_and_shows_recovery_codes_once(
    seeded_client: TestClient,
    seeded_db: Session,
) -> None:
    recovery_codes = enroll_admin(seeded_client)

    assert len(recovery_codes) == DEFAULT_RECOVERY_CODE_COUNT
    assert len(set(recovery_codes)) == DEFAULT_RECOVERY_CODE_COUNT

    admin = seeded_db.scalar(select(User).where(User.username == DEMO_ADMIN_USERNAME))
    assert admin is not None
    assert admin.mfa_enabled is True
    assert admin.totp_secret is not None

    stored_codes = seeded_db.scalars(
        select(MfaRecoveryCode).where(MfaRecoveryCode.user_id == admin.id)
    ).all()
    assert len(stored_codes) == DEFAULT_RECOVERY_CODE_COUNT
    assert all(code.used_at is None for code in stored_codes)
    assert all(code.code_hash not in recovery_codes for code in stored_codes)


def test_enrollment_with_wrong_code_is_rejected(
    seeded_client: TestClient,
    seeded_db: Session,
) -> None:
    response = start_admin_login(seeded_client)
    assert response.status_code == 303

    response = submit_enroll_code(seeded_client, "000000")

    assert response.status_code == 400
    assert "did not match" in response.text
    admin = seeded_db.scalar(select(User).where(User.username == DEMO_ADMIN_USERNAME))
    assert admin is not None
    assert admin.mfa_enabled is False


def test_challenge_with_correct_code_logs_in(
    seeded_client: TestClient,
    seeded_db: Session,
) -> None:
    enroll_admin(seeded_client)
    admin = seeded_db.scalar(select(User).where(User.username == DEMO_ADMIN_USERNAME))
    assert admin is not None and admin.totp_secret is not None

    response = start_admin_login(seeded_client)
    assert response.status_code == 303
    assert response.headers["location"] == "/mfa/challenge"

    # Enrollment already consumed the current time-step, so use the next
    # step's code rather than `.now()` to avoid an incidental replay rejection.
    totp = pyotp.TOTP(admin.totp_secret, interval=30)
    code = totp.generate_otp(admin.mfa_last_verified_step + 1)
    response = submit_challenge_code(seeded_client, code)

    assert response.status_code == 303
    assert response.headers["location"] == "/me"
    assert "securebank_lab_session" in response.headers.get("set-cookie", "")


def test_wrong_code_at_challenge_is_rejected(seeded_client: TestClient) -> None:
    enroll_admin(seeded_client)

    response = start_admin_login(seeded_client)
    assert response.status_code == 303

    response = submit_challenge_code(seeded_client, "000000")

    assert response.status_code == 400
    assert "Invalid or expired code." in response.text
    assert "securebank_lab_session" not in response.headers.get("set-cookie", "")


def test_totp_code_reuse_is_rejected_but_next_step_succeeds(
    seeded_client: TestClient,
    seeded_db: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    enroll_admin(seeded_client)
    admin = seeded_db.scalar(select(User).where(User.username == DEMO_ADMIN_USERNAME))
    assert admin is not None
    secret = admin.totp_secret
    assert secret is not None

    # Enrollment already consumed the current time-step, so the first
    # challenge login in this test uses the following step's code.
    totp = pyotp.TOTP(secret, interval=30)
    current_code = totp.generate_otp(admin.mfa_last_verified_step + 1)

    first_login = start_admin_login(seeded_client)
    assert first_login.status_code == 303
    first_attempt = submit_challenge_code(seeded_client, current_code)
    assert first_attempt.status_code == 303
    assert first_attempt.headers["location"] == "/me"

    # Same time-step code submitted again for a second login attempt must be
    # rejected: the replay check compares against mfa_last_verified_step, not
    # just the previously submitted string, so resubmitting the identical
    # code that already advanced the step is treated as a replay.
    second_login = start_admin_login(seeded_client)
    assert second_login.status_code == 303
    replay_attempt = submit_challenge_code(seeded_client, current_code)
    assert replay_attempt.status_code == 400
    assert "Invalid or expired code." in replay_attempt.text

    # A code from a later, not-yet-consumed step must still succeed, proving
    # the replay check only blocks already-verified steps, not all future
    # logins. The valid window is only +/-1 step around real time, so the
    # clock is advanced by one full interval rather than relying on wall-clock
    # drift, which would make this assertion flaky.
    seeded_db.refresh(admin)
    target_step = admin.mfa_last_verified_step + 1
    advanced_time = target_step * 30 + 5
    monkeypatch.setattr("securebank.security.mfa.time.time", lambda: advanced_time)
    next_step_code = totp.generate_otp(target_step)

    third_login = start_admin_login(seeded_client)
    assert third_login.status_code == 303
    next_attempt = submit_challenge_code(seeded_client, next_step_code)
    assert next_attempt.status_code == 303
    assert next_attempt.headers["location"] == "/me"


def test_verify_totp_code_rejects_step_at_or_before_last_verified() -> None:
    secret = generate_totp_secret()
    totp = pyotp.TOTP(secret, interval=30)
    code = totp.now()

    step = verify_totp_code(secret, code, None)
    assert step is not None

    # Exact replay of the same step is rejected.
    assert verify_totp_code(secret, code, step) is None
    # A step before the last verified one is rejected too, not just an exact match.
    assert verify_totp_code(secret, totp.generate_otp(step - 1), step) is None
    # The next step is still accepted.
    assert verify_totp_code(secret, totp.generate_otp(step + 1), step) is not None


def test_recovery_code_login_succeeds_and_is_single_use(seeded_client: TestClient) -> None:
    recovery_codes = enroll_admin(seeded_client)
    recovery_code = recovery_codes[0]

    response = start_admin_login(seeded_client)
    assert response.status_code == 303
    response = submit_challenge_code(seeded_client, recovery_code)
    assert response.status_code == 303
    assert response.headers["location"] == "/me"

    response = start_admin_login(seeded_client)
    assert response.status_code == 303
    response = submit_challenge_code(seeded_client, recovery_code)
    assert response.status_code == 400
    assert "Invalid or expired code." in response.text


def test_regenerating_mfa_replaces_recovery_codes_instead_of_appending(
    seeded_db: Session,
) -> None:
    admin = seeded_db.scalar(select(User).where(User.username == DEMO_ADMIN_USERNAME))
    assert admin is not None

    first_codes = activate_mfa(
        seeded_db, admin, generate_totp_secret(), DEFAULT_RECOVERY_CODE_COUNT
    )
    first_hashes = {
        code.code_hash
        for code in seeded_db.scalars(
            select(MfaRecoveryCode).where(MfaRecoveryCode.user_id == admin.id)
        ).all()
    }

    second_codes = activate_mfa(
        seeded_db, admin, generate_totp_secret(), DEFAULT_RECOVERY_CODE_COUNT
    )
    remaining = seeded_db.scalars(
        select(MfaRecoveryCode).where(MfaRecoveryCode.user_id == admin.id)
    ).all()
    second_hashes = {code.code_hash for code in remaining}

    assert len(remaining) == DEFAULT_RECOVERY_CODE_COUNT
    assert first_hashes.isdisjoint(second_hashes)
    assert set(first_codes) != set(second_codes)


def test_mfa_audit_events_recorded(seeded_client: TestClient, seeded_db: Session) -> None:
    recovery_codes = enroll_admin(seeded_client)
    start_admin_login(seeded_client)
    submit_challenge_code(seeded_client, "000000")
    start_admin_login(seeded_client)
    submit_challenge_code(seeded_client, recovery_codes[0])

    event_types = {event.event_type for event in seeded_db.scalars(select(AuditEvent)).all()}

    assert {
        "login_mfa_required",
        "mfa_enrolled",
        "mfa_failure",
        "mfa_recovery_used",
    } <= event_types


def test_mfa_routes_require_csrf(seeded_client: TestClient) -> None:
    start_admin_login(seeded_client)

    response = seeded_client.post("/mfa/enroll", data={"code": "000000"}, follow_redirects=False)
    assert response.status_code == 403

    response = seeded_client.post("/mfa/challenge", data={"code": "000000"}, follow_redirects=False)
    assert response.status_code == 403
