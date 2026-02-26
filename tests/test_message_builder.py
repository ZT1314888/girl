from datetime import datetime

from app.config import Settings
from app.message_builder import build_template_payload


def _build_settings() -> Settings:
    return Settings(
        wechat_app_id="a",
        wechat_app_secret="b",
        wechat_template_id="tpl",
        wechat_to_user_openids=["default_user"],
        tz="Asia/Shanghai",
        enable_weather=False,
        qweather_api_key=None,
        weather_location="Beijing",
        fixed_title="早安",
        fixed_remark="顺利",
        anniversary_date="2026-01-01",
        anniversary_name="在一起",
        field_first="first",
        field_date="date",
        field_weekday="weekday",
        field_weather="weather",
        field_anniversary="anniversary",
        field_remark="remark",
        request_timeout_seconds=10,
    )


def test_build_template_payload_with_weather():
    settings = _build_settings()
    now = datetime(2026, 2, 24, 8, 0, 0)
    payload = build_template_payload(settings, now, weather_text="晴 20°C").to_dict()

    assert payload["touser"] == "default_user"
    assert payload["template_id"] == "tpl"
    assert payload["data"]["first"]["value"] == "早安"
    assert payload["data"]["date"]["value"] == "2026-02-24"
    assert payload["data"]["weekday"]["value"] == "星期二"
    assert payload["data"]["weather"]["value"] == "晴 20°C"
    assert "已过" in payload["data"]["anniversary"]["value"]


def test_build_template_payload_without_weather():
    settings = _build_settings()
    now = datetime(2026, 2, 24, 8, 0, 0)
    payload = build_template_payload(settings, now, weather_text=None).to_dict()
    assert payload["data"]["weather"]["value"] == "天气信息暂不可用"


def test_build_template_payload_with_custom_user():
    settings = _build_settings()
    now = datetime(2026, 2, 24, 8, 0, 0)
    payload = build_template_payload(settings, now, weather_text=None, to_user="custom_user").to_dict()
    assert payload["touser"] == "custom_user"
