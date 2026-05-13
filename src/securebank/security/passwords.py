"""Password hashing helpers."""

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError

password_hasher = PasswordHasher()
DUMMY_PASSWORD_HASH = password_hasher.hash("Dummy-Password-For-Missing-Users-123!")


def hash_password(password: str) -> str:
    """Hash a password using Argon2id."""
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against an Argon2id hash."""
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False


def verify_dummy_password(password: str) -> bool:
    """Run password verification for missing-user login attempts."""
    return verify_password(password, DUMMY_PASSWORD_HASH)
