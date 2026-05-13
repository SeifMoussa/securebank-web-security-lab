"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from securebank.audit.service import record_audit_event
from securebank.auth.service import (
    GENERIC_LOGIN_ERROR,
    authenticate_user,
    get_user_by_id,
    register_user,
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
from securebank.security.sessions import clear_session_cookie, get_session_data, set_session_cookie

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

    record_audit_event(
        db,
        "login_success",
        username=user.username,
        user_id=user.id,
        request_id=_request_id(request),
    )
    response = RedirectResponse("/me", status_code=status.HTTP_303_SEE_OTHER)
    set_session_cookie(response, user.id, settings)
    clear_csrf_cookie(response, settings)
    return response


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
