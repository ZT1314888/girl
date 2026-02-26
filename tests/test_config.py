import pytest

from app.config import ConfigError, load_settings


def _set_minimal_env(monkeypatch):
    monkeypatch.setenv("WECHAT_APP_ID", "app_id")
    monkeypatch.setenv("WECHAT_APP_SECRET", "app_secret")
    monkeypatch.setenv("WECHAT_TEMPLATE_ID", "template_id")
    monkeypatch.setenv("WECHAT_TO_USER_OPENIDS", '["openid"]')


def test_load_settings_minimal(monkeypatch):
    _set_minimal_env(monkeypatch)
    settings = load_settings()
    assert settings.wechat_app_id == "app_id"
    assert settings.enable_weather is False
    assert settings.tz == "Asia/Shanghai"
    assert settings.wechat_to_user_openids == ["openid"]


def test_load_settings_multiple_users(monkeypatch):
    _set_minimal_env(monkeypatch)
    monkeypatch.setenv("WECHAT_TO_USER_OPENIDS", '["user1", "user2", "user3"]')
    settings = load_settings()
    assert settings.wechat_to_user_openids == ["user1", "user2", "user3"]


def test_load_settings_comma_separated_users(monkeypatch):
    _set_minimal_env(monkeypatch)
    monkeypatch.setenv("WECHAT_TO_USER_OPENIDS", "user1,user2,user3")
    settings = load_settings()
    assert settings.wechat_to_user_openids == ["user1", "user2", "user3"]


def test_legacy_single_user_format(monkeypatch):
    # Support old WECHAT_TO_USER_OPENID format
    monkeypatch.setenv("WECHAT_APP_ID", "app_id")
    monkeypatch.setenv("WECHAT_APP_SECRET", "app_secret")
    monkeypatch.setenv("WECHAT_TEMPLATE_ID", "template_id")
    monkeypatch.setenv("WECHAT_TO_USER_OPENID", "legacy_user")
    settings = load_settings()
    assert settings.wechat_to_user_openids == ["legacy_user"]


def test_missing_required_env_raises(monkeypatch):
    monkeypatch.delenv("WECHAT_APP_ID", raising=False)
    monkeypatch.delenv("WECHAT_APP_SECRET", raising=False)
    monkeypatch.delenv("WECHAT_TEMPLATE_ID", raising=False)
    monkeypatch.delenv("WECHAT_TO_USER_OPENIDS", raising=False)
    monkeypatch.delenv("WECHAT_TO_USER_OPENID", raising=False)
    with pytest.raises(ConfigError):
        load_settings()


def test_enable_weather_requires_key(monkeypatch):
    _set_minimal_env(monkeypatch)
    monkeypatch.setenv("ENABLE_WEATHER", "true")
    monkeypatch.delenv("WEATHER_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        load_settings()


def test_invalid_anniversary_date_raises(monkeypatch):
    _set_minimal_env(monkeypatch)
    monkeypatch.setenv("ANNIVERSARY_DATE", "2026/01/01")
    with pytest.raises(ConfigError):
        load_settings()
