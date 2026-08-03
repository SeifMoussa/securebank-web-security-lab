"""Authentication service functions."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from securebank.models import MfaRecoveryCode, User, utc_now
from securebank.schemas import validate_password_strength, validate_username
from securebank.security.mfa import (
    generate_recovery_codes,
    hash_recovery_code,
    verify_recovery_code,
    verify_totp_code,
)
from securebank.security.passwords import hash_password, verify_dummy_password, verify_password

GENERIC_LOGIN_ERROR = "Invalid username or password."
MFA_REQUIRED_ROLES = frozenset({"admin"})


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


def requires_mfa(user: User) -> bool:
    """Return whether a user's role tier must complete a TOTP challenge at login."""
    return user.role in MFA_REQUIRED_ROLES


def activate_mfa(db: Session, user: User, secret: str, recovery_code_count: int) -> list[str]:
    """Confirm a TOTP secret, replace any recovery codes, and return the new plaintext codes."""
    user.totp_secret = secret
    user.mfa_enabled = True
    user.mfa_last_verified_step = None
    db.query(MfaRecoveryCode).filter(MfaRecoveryCode.user_id == user.id).delete()

    codes = generate_recovery_codes(recovery_code_count)
    for code in codes:
        db.add(MfaRecoveryCode(user_id=user.id, code_hash=hash_recovery_code(code)))
    db.commit()
    return codes


def verify_mfa_totp(db: Session, user: User, code: str) -> bool:
    """Verify a TOTP code and advance the user's last-verified step on success."""
    if user.totp_secret is None:
        return False
    step = verify_totp_code(user.totp_secret, code, user.mfa_last_verified_step)
    if step is None:
        return False
    user.mfa_last_verified_step = step
    db.commit()
    return True


def consume_mfa_recovery_code(db: Session, user: User, code: str) -> bool:
    """Verify and consume a single-use recovery code."""
    unused_codes = db.scalars(
        select(MfaRecoveryCode).where(
            MfaRecoveryCode.user_id == user.id,
            MfaRecoveryCode.used_at.is_(None),
        )
    )
    for recovery_code in unused_codes:
        if verify_recovery_code(code, recovery_code.code_hash):
            recovery_code.used_at = utc_now()
            db.commit()
            return True
    return False
