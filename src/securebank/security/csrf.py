"""CSRF token helpers for server-rendered forms."""

import secrets

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from starlette.requests import Request
from starlette.responses import Response

from securebank.config import Settings

CSRF_SALT = "securebank-csrf"
CSRF_FORM_FIELD = "csrf_token"


def _serializer(settings: Settings) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.secret_key, salt=CSRF_SALT)


def create_csrf_token(settings: Settings) -> str:
    """Create a signed CSRF token."""
    return _serializer(settings).dumps(secrets.token_urlsafe(32))


def set_csrf_cookie(response: Response, token: str, settings: Settings) -> None:
    """Set the CSRF cookie used to validate server-rendered forms."""
    response.set_cookie(
        key=settings.csrf_cookie_name,
        value=token,
        max_age=settings.csrf_token_max_age_seconds,
        httponly=True,
        secure=settings.secure_cookie,
        samesite="strict",
    )


def clear_csrf_cookie(response: Response, settings: Settings) -> None:
    """Clear the CSRF cookie."""
    response.delete_cookie(
        key=settings.csrf_cookie_name,
        httponly=True,
        secure=settings.secure_cookie,
        samesite="strict",
    )


def validate_csrf_token(request: Request, form_token: str | None, settings: Settings) -> bool:
    """Validate the submitted token against the signed CSRF cookie."""
    cookie_token = request.cookies.get(settings.csrf_cookie_name)
    if not cookie_token or not form_token or cookie_token != form_token:
        return False
    try:
        _serializer(settings).loads(cookie_token, max_age=settings.csrf_token_max_age_seconds)
    except (BadSignature, SignatureExpired):
        return False
    return True
