"""Signed cookie session helpers."""

from typing import Any

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from starlette.requests import Request
from starlette.responses import Response

from securebank.config import Settings

SESSION_SALT = "securebank-session"


def _serializer(settings: Settings) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.secret_key, salt=SESSION_SALT)


def create_session_token(user_id: int, settings: Settings) -> str:
    """Create a signed session token."""
    return _serializer(settings).dumps({"user_id": user_id})


def read_session_token(token: str, settings: Settings) -> dict[str, Any] | None:
    """Read and validate a signed session token."""
    try:
        data = _serializer(settings).loads(token, max_age=settings.session_max_age_seconds)
    except (BadSignature, SignatureExpired):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("user_id"), int):
        return None
    return data


def get_session_data(request: Request, settings: Settings) -> dict[str, Any] | None:
    """Read session data from the configured cookie."""
    token = request.cookies.get(settings.session_cookie_name)
    if token is None:
        return None
    return read_session_token(token, settings)


def set_session_cookie(response: Response, user_id: int, settings: Settings) -> None:
    """Set the signed session cookie."""
    response.set_cookie(
        key=settings.session_cookie_name,
        value=create_session_token(user_id, settings),
        max_age=settings.session_max_age_seconds,
        httponly=True,
        secure=settings.secure_cookie,
        samesite="strict",
    )


def clear_session_cookie(response: Response, settings: Settings) -> None:
    """Clear the session cookie."""
    response.delete_cookie(
        key=settings.session_cookie_name,
        httponly=True,
        secure=settings.secure_cookie,
        samesite="strict",
    )
