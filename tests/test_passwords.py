from securebank.security.passwords import hash_password, verify_dummy_password, verify_password


def test_password_hash_is_argon2id_and_verifies() -> None:
    password = "StrongPass123!"

    password_hash = hash_password(password)

    assert password_hash.startswith("$argon2id$")
    assert password not in password_hash
    assert verify_password(password, password_hash)


def test_wrong_password_rejected() -> None:
    password_hash = hash_password("StrongPass123!")

    assert not verify_password("WrongPass123!", password_hash)


def test_dummy_verification_path_exists() -> None:
    assert not verify_dummy_password("WrongPass123!")
