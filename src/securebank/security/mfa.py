"""TOTP-based MFA helpers: secrets, recovery codes, and the pending-login token."""

import hmac
import secrets
import time
from typing import Any

import pyotp
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from starlette.requests import Request
from starlette.responses import Response

from securebank.config import Settings
from securebank.security.passwords import hash_password, verify_password

MFA_PENDING_SALT = "securebank-mfa-pending"
TOTP_INTERVAL_SECONDS = 30
TOTP_VALID_WINDOW_STEPS = 1
RECOVERY_CODE_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
RECOVERY_CODE_LENGTH = 10


def generate_totp_secret() -> str:
    """Generate a new random base32 TOTP secret."""
    return pyotp.random_base32()


def build_provisioning_uri(secret: str, username: str, settings: Settings) -> str:
    """Build the otpauth:// URI an authenticator app (or a QR code) would encode."""
    return pyotp.TOTP(secret, interval=TOTP_INTERVAL_SECONDS).provisioning_uri(
        name=username,
        issuer_name=settings.mfa_issuer,
    )


def verify_totp_code(secret: str, code: str, last_verified_step: int | None) -> int | None:
    """Verify a TOTP code, rejecting any time-step at or before last_verified_step.

    Returns the matched time-step on success, or None if no step in the
    validity window produced a match that hasn't already been consumed.
    """
    totp = pyotp.TOTP(secret, interval=TOTP_INTERVAL_SECONDS)
    current_step = int(time.time() // TOTP_INTERVAL_SECONDS)
    for offset in range(-TOTP_VALID_WINDOW_STEPS, TOTP_VALID_WINDOW_STEPS + 1):
        step = current_step + offset
        if last_verified_step is not None and step <= last_verified_step:
            continue
        candidate = totp.generate_otp(step)
        if hmac.compare_digest(candidate, code):
            return step
    return None


def generate_recovery_codes(count: int) -> list[str]:
    """Generate plaintext recovery codes, to be hashed before storage and shown once."""
    return [
        "".join(secrets.choice(RECOVERY_CODE_ALPHABET) for _ in range(RECOVERY_CODE_LENGTH))
        for _ in range(count)
    ]


def hash_recovery_code(code: str) -> str:
    """Hash a recovery code for storage."""
    return hash_password(code)


def verify_recovery_code(code: str, code_hash: str) -> bool:
    """Verify a submitted recovery code against a stored hash."""
    return verify_password(code, code_hash)


def _pending_serializer(settings: Settings) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.secret_key, salt=MFA_PENDING_SALT)


def create_pending_token(
    user_id: int, stage: str, settings: Settings, *, secret: str | None = None
) -> str:
    """Create a signed, short-lived token for a partially authenticated login."""
    payload: dict[str, Any] = {"user_id": user_id, "stage": stage}
    if secret is not None:
        payload["secret"] = secret
    return _pending_serializer(settings).dumps(payload)


def read_pending_token(token: str, settings: Settings) -> dict[str, Any] | None:
    """Read and validate a signed pending-login token."""
    try:
        data = _pending_serializer(settings).loads(
            token, max_age=settings.mfa_pending_max_age_seconds
        )
    except (BadSignature, SignatureExpired):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("user_id"), int):
        return None
    if data.get("stage") not in {"enroll", "challenge"}:
        return None
    return data


def get_pending_data(request: Request, settings: Settings) -> dict[str, Any] | None:
    """Read pending-login data from the configured cookie."""
    token = request.cookies.get(settings.mfa_pending_cookie_name)
    if token is None:
        return None
    return read_pending_token(token, settings)


def set_pending_cookie(response: Response, token: str, settings: Settings) -> None:
    """Set the signed pending-login cookie."""
    response.set_cookie(
        key=settings.mfa_pending_cookie_name,
        value=token,
        max_age=settings.mfa_pending_max_age_seconds,
        httponly=True,
        secure=settings.secure_cookie,
        samesite="strict",
    )


def clear_pending_cookie(response: Response, settings: Settings) -> None:
    """Clear the pending-login cookie."""
    response.delete_cookie(
        key=settings.mfa_pending_cookie_name,
        httponly=True,
        secure=settings.secure_cookie,
        samesite="strict",
    )
