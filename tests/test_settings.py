from securebank.config import Settings


def test_settings_load_defaults() -> None:
    settings = Settings(secret_key="test-secret-key-for-securebank")

    assert settings.environment == "development"
    assert settings.session_cookie_name == "securebank_lab_session"
    assert settings.session_max_age_seconds > 0
    assert settings.csrf_cookie_name == "securebank_lab_csrf"
