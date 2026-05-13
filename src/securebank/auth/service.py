"""Authentication service functions."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from securebank.models import User
from securebank.schemas import validate_password_strength, validate_username
from securebank.security.passwords import hash_password, verify_dummy_password, verify_password

GENERIC_LOGIN_ERROR = "Invalid username or password."


def get_user_by_username(db: Session, username: str) -> User | None:
    """Return a user by username."""
    return db.scalar(select(User).where(User.username == username))


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Return a user by id."""
    return db.get(User, user_id)


def register_user(db: Session, username: str, password: str) -> User:
    """Validate and create a user."""
    normalized_username = validate_username(username)
    validate_password_strength(password)
    user = User(username=normalized_username, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Authenticate a user with a generic missing-user verification path."""
    try:
        normalized_username = validate_username(username)
    except ValueError:
        verify_dummy_password(password)
        return None

    user = get_user_by_username(db, normalized_username)
    if user is None:
        verify_dummy_password(password)
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
