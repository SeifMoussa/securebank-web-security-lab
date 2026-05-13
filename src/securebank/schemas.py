"""Input validation helpers for Phase 2."""

import re

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,32}$")


def validate_username(username: str) -> str:
    """Validate and normalize a username."""
    username = username.strip()
    if not USERNAME_PATTERN.fullmatch(username):
        raise ValueError("Username must be 3-32 characters using letters, numbers, or underscore.")
    return username


def validate_password_strength(password: str) -> None:
    """Validate Phase 2 password complexity requirements."""
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters.")
    if not any(char.isupper() for char in password):
        raise ValueError("Password must include an uppercase letter.")
    if not any(char.islower() for char in password):
        raise ValueError("Password must include a lowercase letter.")
    if not any(char.isdigit() for char in password):
        raise ValueError("Password must include a digit.")
    if not any(not char.isalnum() for char in password):
        raise ValueError("Password must include a symbol.")
