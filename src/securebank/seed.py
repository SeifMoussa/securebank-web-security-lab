"""Deterministic fictional lab seed data."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from securebank.models import Account, User
from securebank.security.passwords import hash_password

DEMO_PASSWORD = "LabDemo123!"
DEMO_USERS = (
    ("alice", 5000),
    ("bob", 3000),
    ("carol", 2500),
)


def seed_demo_data(db: Session) -> None:
    """Create deterministic fictional users and lab-credit accounts."""
    for username, balance_credits in DEMO_USERS:
        user = db.scalar(select(User).where(User.username == username))
        if user is None:
            user = User(username=username, password_hash=hash_password(DEMO_PASSWORD))
            db.add(user)
            db.flush()

        account = db.scalar(select(Account).where(Account.user_id == user.id))
        if account is None:
            db.add(Account(user_id=user.id, balance_credits=balance_credits))

    db.commit()
