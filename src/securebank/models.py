"""Database models for Phase 2."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from securebank.database import Base


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)


class User(Base):
    """Application user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    audit_events: Mapped[list["AuditEvent"]] = relationship(back_populates="user")
    accounts: Mapped[list["Account"]] = relationship(back_populates="user")


class AuditEvent(Base):
    """Security-relevant audit event."""

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped[User | None] = relationship(back_populates="audit_events")


class Account(Base):
    """Fictional lab-credit account owned by a user."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    balance_credits: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped[User] = relationship(back_populates="accounts")
    sent_transactions: Mapped[list["Transaction"]] = relationship(
        foreign_keys="Transaction.sender_account_id",
        back_populates="sender_account",
    )
    received_transactions: Mapped[list["Transaction"]] = relationship(
        foreign_keys="Transaction.recipient_account_id",
        back_populates="recipient_account",
    )


class Transaction(Base):
    """Fictional lab-credit transfer record."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sender_account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    recipient_account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    amount_credits: Mapped[int] = mapped_column(Integer, nullable=False)
    memo: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    sender_account: Mapped[Account] = relationship(
        foreign_keys=[sender_account_id],
        back_populates="sent_transactions",
    )
    recipient_account: Mapped[Account] = relationship(
        foreign_keys=[recipient_account_id],
        back_populates="received_transactions",
    )
