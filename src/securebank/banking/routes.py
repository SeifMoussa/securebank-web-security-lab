"""Fictional lab-credit banking routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from securebank.audit.service import record_audit_event
from securebank.auth.routes import render_form, require_csrf
from securebank.auth.service import get_user_by_id
from securebank.banking.service import (
    TransferError,
    get_account_owner,
    get_recent_transactions,
    get_user_account,
    perform_transfer,
)
from securebank.database import get_db
from securebank.models import Account, Transaction, User
from securebank.security.csrf import CSRF_FORM_FIELD
from securebank.security.sessions import clear_session_cookie, get_session_data

router = APIRouter()


def _settings(request: Request):
    return request.app.state.settings


def _templates(request: Request):
    return request.app.state.templates


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _redirect_to_login(request: Request, db: Session, detail: str) -> RedirectResponse:
    record_audit_event(db, "authz_denied", request_id=_request_id(request), detail=detail)
    response = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    if detail == "invalid session":
        clear_session_cookie(response, _settings(request))
    return response


def current_user_or_redirect(
    request: Request,
    db: Session,
) -> User | RedirectResponse:
    """Return current user or a login redirect response."""
    session_data = get_session_data(request, _settings(request))
    if session_data is None:
        return _redirect_to_login(request, db, "missing session")

    user = get_user_by_id(db, session_data["user_id"])
    if user is None:
        return _redirect_to_login(request, db, "invalid session")
    return user


def transaction_view(db: Session, account: Account, transaction: Transaction) -> dict:
    """Build a template-safe transaction view dictionary."""
    sender = get_account_owner(db, transaction.sender_account)
    recipient = get_account_owner(db, transaction.recipient_account)
    direction = "sent" if transaction.sender_account_id == account.id else "received"
    return {
        "id": transaction.id,
        "direction": direction,
        "counterparty": recipient.username
        if direction == "sent" and recipient
        else sender.username,
        "amount_credits": transaction.amount_credits,
        "memo": transaction.memo,
        "created_at": transaction.created_at,
    }


def account_context(db: Session, user: User, limit: int = 10) -> dict:
    """Build template context for the user's fictional account."""
    account = get_user_account(db, user.id)
    transactions = []
    if account is not None:
        transactions = [
            transaction_view(db, account, transaction)
            for transaction in get_recent_transactions(db, account.id, limit)
        ]
    return {"user": user, "account": account, "transactions": transactions}


@router.get("/dashboard", response_class=HTMLResponse, response_model=None)
def dashboard(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> HTMLResponse | RedirectResponse:
    user = current_user_or_redirect(request, db)
    if isinstance(user, RedirectResponse):
        return user
    return _templates(request).TemplateResponse(
        request,
        "banking/dashboard.html",
        account_context(db, user),
    )


@router.get("/transfer", response_class=HTMLResponse, response_model=None)
def transfer_form(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> HTMLResponse | RedirectResponse:
    user = current_user_or_redirect(request, db)
    if isinstance(user, RedirectResponse):
        return user
    context = {
        **account_context(db, user, limit=5),
        "error": None,
        "recipient_username": "",
        "amount_credits": "",
        "memo": "",
    }
    return render_form(request, "banking/transfer.html", context, _settings(request))


@router.post("/transfer", response_class=HTMLResponse, response_model=None)
def transfer_submit(
    request: Request,
    recipient_username: Annotated[str, Form()],
    amount_credits: Annotated[str, Form()],
    db: Annotated[Session, Depends(get_db)],
    memo: Annotated[str, Form()] = "",
    csrf_token: Annotated[str | None, Form(alias=CSRF_FORM_FIELD)] = None,
) -> HTMLResponse | RedirectResponse:
    settings = _settings(request)
    require_csrf(request, csrf_token, settings)
    user = current_user_or_redirect(request, db)
    if isinstance(user, RedirectResponse):
        return user

    try:
        perform_transfer(db, user, recipient_username, amount_credits, memo)
    except TransferError as exc:
        event_type = {
            "recipient_not_found": "transfer_recipient_not_found",
            "insufficient_funds": "transfer_insufficient_funds",
        }.get(exc.reason, "transfer_failure")
        record_audit_event(
            db,
            event_type,
            username=user.username,
            user_id=user.id,
            request_id=_request_id(request),
            detail=exc.reason,
        )
        context = {
            **account_context(db, user, limit=5),
            "error": str(exc),
            "recipient_username": recipient_username,
            "amount_credits": amount_credits,
            "memo": memo,
        }
        return render_form(
            request,
            "banking/transfer.html",
            context,
            settings,
            status.HTTP_400_BAD_REQUEST,
        )

    record_audit_event(
        db,
        "transfer_success",
        username=user.username,
        user_id=user.id,
        request_id=_request_id(request),
    )
    return RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/transactions", response_class=HTMLResponse, response_model=None)
def transactions(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> HTMLResponse | RedirectResponse:
    user = current_user_or_redirect(request, db)
    if isinstance(user, RedirectResponse):
        return user
    return _templates(request).TemplateResponse(
        request,
        "banking/transactions.html",
        account_context(db, user, limit=50),
    )
