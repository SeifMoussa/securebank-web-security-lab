"""Audit logging foundation."""

from sqlalchemy.orm import Session

from securebank.models import AuditEvent


def record_audit_event(
    db: Session,
    event_type: str,
    *,
    username: str | None = None,
    user_id: int | None = None,
    request_id: str | None = None,
    detail: str | None = None,
) -> AuditEvent:
    """Persist a security-relevant audit event."""
    event = AuditEvent(
        event_type=event_type,
        username=username,
        user_id=user_id,
        request_id=request_id,
        detail=detail,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
