"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from securebank.audit.service import record_audit_event
from securebank.auth.service import (
    GENERIC_LOGIN_ERROR,
    activate_mfa,
    authenticate_user,
    consume_mfa_recovery_code,
    get_user_by_id,
    register_user,
    requires_mfa,
    verify_mfa_totp,
)
from securebank.config import Settings
from securebank.database import get_db
from securebank.security.csrf import (
    CSRF_FORM_FIELD,
    clear_csrf_cookie,
    create_csrf_token,
    set_csrf_cookie,
    validate_csrf_token,
)
from securebank.security.mfa import (
    build_provisioning_uri,
    clear_pending_cookie,
    create_pending_token,
    generate_totp_secret,
    get_pending_data,
    set_pending_cookie,
    verify_totp_code,
)
from securebank.security.sessions import clear_session_cookie, get_session_data, set_session_cookie

MFA_GENERIC_ERROR = "Invalid or expired code."

router = APIRouter()


def _settings(request: Request) -> Settings:
    return request.app.state.settings


def _templates(request: Request):
    return request.app.state.templates


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def render_form(
    request: Request,
    template_name: str,
    context: dict,
    settings: Settings,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    """Render a form with a fresh CSRF token."""
    token = create_csrf_token(settings)
    response = _templates(request).TemplateResponse(
        request,
        template_name,
        {**context, "csrf_token": token},
        status_code=status_code,
    )
    set_csrf_cookie(response, token, settings)
    return response


def require_csrf(request: Request, csrf_token: str, settings: Settings) -> None:
    """Reject missing or invalid CSRF tokens."""
    if not validate_csrf_token(request, csrf_token, settings):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token.")


def _finish_login(user, settings: Settings) -> RedirectResponse:
    """Set the real session cookie and clear any pending-MFA/CSRF cookies."""
    response = RedirectResponse("/me", status_code=status.HTTP_303_SEE_OTHER)
    set_session_cookie(response, user.id, settings)
    clear_pending_cookie(response, settings)
    clear_csrf_cookie(response, settings)
    return response


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request) -> HTMLResponse:
    settings = _settings(request)
    return render_form(request, "auth/register.html", {"error": None, "username": ""}, settings)


@router.post("/register", response_class=HTMLResponse, response_model=None)
def register_submit(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Annotated[Session, Depends(get_db)],
    csrf_token: Annotated[str | None, Form(alias=CSRF_FORM_FIELD)] = None,
) -> HTMLResponse | RedirectResponse:
    settings = _settings(request)
    require_csrf(request, csrf_token, settings)

    try:
        user = register_user(db, username, password)
    except (ValueError, IntegrityError):
        db.rollback()
        record_audit_event(
            db,
            "register_failure",
            username=username[:32],
            request_id=_request_id(request),
            detail="registration rejected",
        )
        return render_form(
            request,
            "auth/register.html",
            {"error": "Registration could not be completed.", "username": username},
            settings,
            status.HTTP_400_BAD_REQUEST,
        )

    record_audit_event(
        db,
        "register_success",
        username=user.username,
        user_id=user.id,
        request_id=_request_id(request),
    )
    response = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    clear_csrf_cookie(response, settings)
    return response


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request) -> HTMLResponse:
    settings = _settings(request)
    return render_form(request, "auth/login.html", {"error": None, "username": ""}, settings)


@router.post("/login", response_class=HTMLResponse, response_model=None)
def login_submit(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Annotated[Session, Depends(get_db)],
    csrf_token: Annotated[str | None, Form(alias=CSRF_FORM_FIELD)] = None,
) -> HTMLResponse | RedirectResponse:
    settings = _settings(request)
    require_csrf(request, csrf_token, settings)
    user = authenticate_user(db, username, password)

    if user is None:
        record_audit_event(
            db,
            "login_failure",
            username=username[:32],
            request_id=_request_id(request),
            detail="invalid credentials",
        )
        return render_form(
            request,
            "auth/login.html",
            {"error": GENERIC_LOGIN_ERROR, "username": username},
            settings,
            status.HTTP_400_BAD_REQUEST,
        )

    if requires_mfa(user):
        stage = "challenge" if user.mfa_enabled else "enroll"
        pending_secret = None if user.mfa_enabled else generate_totp_secret()
        pending_token = create_pending_token(user.id, stage, settings, secret=pending_secret)
        record_audit_event(
            db,
            "login_mfa_required",
            username=user.username,
            user_id=user.id,
            request_id=_request_id(request),
            detail=stage,
        )
        response = RedirectResponse(f"/mfa/{stage}", status_code=status.HTTP_303_SEE_OTHER)
        set_pending_cookie(response, pending_token, settings)
        clear_csrf_cookie(response, settings)
        return response

    record_audit_event(
        db,
        "login_success",
        username=user.username,
        user_id=user.id,
        request_id=_request_id(request),
    )
    return _finish_login(user, settings)


@router.post("/logout")
def logout(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    csrf_token: Annotated[str | None, Form(alias=CSRF_FORM_FIELD)] = None,
) -> RedirectResponse:
    settings = _settings(request)
    require_csrf(request, csrf_token, settings)

    session_data = get_session_data(request, settings)
    user_id = session_data["user_id"] if session_data else None
    user = get_user_by_id(db, user_id) if user_id is not None else None
    record_audit_event(
        db,
        "logout",
        username=user.username if user else None,
        user_id=user.id if user else None,
        request_id=_request_id(request),
    )
    response = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    clear_session_cookie(response, settings)
    clear_csrf_cookie(response, settings)
    return response


@router.get("/me", response_class=HTMLResponse, response_model=None)
def me(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> HTMLResponse | RedirectResponse:
    settings = _settings(request)
    session_data = get_session_data(request, settings)
    if session_data is None:
        record_audit_event(
            db,
            "authz_denied",
            request_id=_request_id(request),
            detail="missing session",
        )
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    user = get_user_by_id(db, session_data["user_id"])
    if user is None:
        record_audit_event(
            db,
            "authz_denied",
            request_id=_request_id(request),
            detail="invalid session",
        )
        response = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
        clear_session_cookie(response, settings)
        return response

    return render_form(request, "auth/me.html", {"user": user}, settings)


def _load_pending_user(
    request: Request,
    db: Session,
    settings: Settings,
    expected_stage: str,
):
    """Return the (pending_data, user) pair for a pending-MFA cookie, or None if invalid."""
    pending = get_pending_data(request, settings)
    if pending is None or pending["stage"] != expected_stage:
        return None
    user = get_user_by_id(db, pending["user_id"])
    if user is None or not requires_mfa(user):
        return None
    if expected_stage == "enroll" and (user.mfa_enabled or "secret" not in pending):
        return None
    if expected_stage == "challenge" and not user.mfa_enabled:
        return None
    return pending, user


@router.get("/mfa/enroll", response_class=HTMLResponse, response_model=None)
def mfa_enroll_form(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> HTMLResponse | RedirectResponse:
    settings = _settings(request)
    loaded = _load_pending_user(request, db, settings, "enroll")
    if loaded is None:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    pending, user = loaded

    provisioning_uri = build_provisioning_uri(pending["secret"], user.username, settings)
    return render_form(
        request,
        "auth/mfa_enroll.html",
        {"error": None, "secret": pending["secret"], "provisioning_uri": provisioning_uri},
        settings,
    )


@router.post("/mfa/enroll", response_class=HTMLResponse, response_model=None)
def mfa_enroll_submit(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    code: Annotated[str, Form()],
    csrf_token: Annotated[str | None, Form(alias=CSRF_FORM_FIELD)] = None,
) -> HTMLResponse | RedirectResponse:
    settings = _settings(request)
    require_csrf(request, csrf_token, settings)

    loaded = _load_pending_user(request, db, settings, "enroll")
    if loaded is None:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    pending, user = loaded
    secret = pending["secret"]
    step = verify_totp_code(secret, code, None)
    if step is None:
        record_audit_event(
            db,
            "mfa_enroll_failed",
            username=user.username,
            user_id=user.id,
            request_id=_request_id(request),
            detail="invalid enrollment code",
        )
        provisioning_uri = build_provisioning_uri(secret, user.username, settings)
        return render_form(
            request,
            "auth/mfa_enroll.html",
            {
                "error": "That code did not match. Try the current code from your app.",
                "secret": secret,
                "provisioning_uri": provisioning_uri,
            },
            settings,
            status.HTTP_400_BAD_REQUEST,
        )

    recovery_codes = activate_mfa(db, user, secret, settings.mfa_recovery_code_count)
    user.mfa_last_verified_step = step
    db.commit()
    record_audit_event(
        db,
        "mfa_enrolled",
        username=user.username,
        user_id=user.id,
        request_id=_request_id(request),
    )

    response = _templates(request).TemplateResponse(
        request,
        "auth/mfa_recovery_codes.html",
        {"recovery_codes": recovery_codes},
    )
    set_session_cookie(response, user.id, settings)
    clear_pending_cookie(response, settings)
    clear_csrf_cookie(response, settings)
    return response


@router.get("/mfa/challenge", response_class=HTMLResponse, response_model=None)
def mfa_challenge_form(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> HTMLResponse | RedirectResponse:
    settings = _settings(request)
    loaded = _load_pending_user(request, db, settings, "challenge")
    if loaded is None:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    return render_form(request, "auth/mfa_challenge.html", {"error": None}, settings)


@router.post("/mfa/challenge", response_class=HTMLResponse, response_model=None)
def mfa_challenge_submit(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    code: Annotated[str, Form()],
    csrf_token: Annotated[str | None, Form(alias=CSRF_FORM_FIELD)] = None,
) -> HTMLResponse | RedirectResponse:
    settings = _settings(request)
    require_csrf(request, csrf_token, settings)

    loaded = _load_pending_user(request, db, settings, "challenge")
    if loaded is None:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    _, user = loaded

    if verify_mfa_totp(db, user, code):
        record_audit_event(
            db,
            "mfa_success",
            username=user.username,
            user_id=user.id,
            request_id=_request_id(request),
        )
        return _finish_login(user, settings)

    if consume_mfa_recovery_code(db, user, code):
        record_audit_event(
            db,
            "mfa_recovery_used",
            username=user.username,
            user_id=user.id,
            request_id=_request_id(request),
        )
        return _finish_login(user, settings)

    record_audit_event(
        db,
        "mfa_failure",
        username=user.username,
        user_id=user.id,
        request_id=_request_id(request),
        detail="invalid code",
    )
    return render_form(
        request,
        "auth/mfa_challenge.html",
        {"error": MFA_GENERIC_ERROR},
        settings,
        status.HTTP_400_BAD_REQUEST,
    )
