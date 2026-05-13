"""Fictional lab-credit banking services."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from securebank.models import Account, Transaction, User

MAX_MEMO_LENGTH = 120


class TransferError(ValueError):
    """Expected transfer validation or persistence error."""

    def __init__(self, message: str, reason: str) -> None:
        super().__init__(message)
        self.reason = reason


def get_user_account(db: Session, user_id: int) -> Account | None:
    """Return the account owned by a user."""
    return db.scalar(select(Account).where(Account.user_id == user_id))


def get_account_owner(db: Session, account: Account) -> User | None:
    """Return the owner for an account."""
    return db.get(User, account.user_id)


def get_recent_transactions(db: Session, account_id: int, limit: int = 10) -> list[Transaction]:
    """Return recent transactions involving an account."""
    return list(
        db.scalars(
            select(Transaction)
            .where(
                or_(
                    Transaction.sender_account_id == account_id,
                    Transaction.recipient_account_id == account_id,
                )
            )
            .order_by(Transaction.created_at.desc(), Transaction.id.desc())
            .limit(limit)
        )
    )


def create_transaction_record(
    db: Session,
    sender_account: Account,
    recipient_account: Account,
    amount_credits: int,
    memo: str,
) -> Transaction:
    """Create a transaction record in the current database transaction."""
    transaction = Transaction(
        sender_account_id=sender_account.id,
        recipient_account_id=recipient_account.id,
        amount_credits=amount_credits,
        memo=memo,
    )
    db.add(transaction)
    return transaction


def perform_transfer(
    db: Session,
    sender: User,
    recipient_username: str,
    amount_text: str,
    memo: str,
) -> Transaction:
    """Perform an atomic fictional lab-credit transfer."""
    normalized_recipient = recipient_username.strip()
    memo = memo.strip()

    try:
        amount_credits = int(amount_text)
    except ValueError as exc:
        raise TransferError("Amount must be a positive whole number.", "invalid_amount") from exc

    if amount_credits <= 0:
        raise TransferError("Amount must be greater than zero.", "invalid_amount")
    if len(memo) > MAX_MEMO_LENGTH:
        raise TransferError("Memo is too long.", "invalid_memo")

    sender_account = get_user_account(db, sender.id)
    if sender_account is None:
        raise TransferError("Sender account was not found.", "sender_account_missing")

    recipient = db.scalar(select(User).where(User.username == normalized_recipient))
    if recipient is None:
        raise TransferError("Recipient was not found.", "recipient_not_found")
    if recipient.id == sender.id:
        raise TransferError("Self-transfer is not allowed.", "self_transfer")

    recipient_account = get_user_account(db, recipient.id)
    if recipient_account is None:
        raise TransferError("Recipient account was not found.", "recipient_account_missing")
    if sender_account.balance_credits < amount_credits:
        raise TransferError("Insufficient lab credits.", "insufficient_funds")

    try:
        sender_account.balance_credits -= amount_credits
        recipient_account.balance_credits += amount_credits
        transaction = create_transaction_record(
            db,
            sender_account,
            recipient_account,
            amount_credits,
            memo,
        )
        db.commit()
        db.refresh(transaction)
    except Exception as exc:
        db.rollback()
        raise TransferError("Transfer could not be completed.", "transfer_rollback") from exc

    return transaction
