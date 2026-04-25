from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv


class ConfigError(ValueError):
    """Raised when configuration is invalid."""


@dataclass(frozen=True)
class Settings:
    wechat_app_id: str
    wechat_app_secret: str
    wechat_template_id: str
    wechat_to_user_openids: list[str]
    tz: str
    enable_weather: bool
    qweather_api_key: Optional[str]
    weather_location: str
    fixed_title: str
    fixed_remark: str
    anniversary_date: Optional[str]
    anniversary_name: str
    field_first: str
    field_date: str
    field_weekday: str
    field_weather: str
    field_anniversary: str
    field_remark: str
    request_timeout_seconds: int


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    raw = raw.strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    raise ConfigError(f"Invalid boolean value for {name}: {raw}")


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw.strip())
    except ValueError as exc:
        raise ConfigError(f"Invalid integer value for {name}: {raw}") from exc
    if value <= 0:
        raise ConfigError(f"{name} must be greater than 0")
    return value


def _get_openid_list() -> list[str]:
    """Parse multiple user openids from environment variable.

    Supports both formats:
    1. JSON array: '["openid1", "openid2", "openid3"]'
    2. Comma-separated: 'openid1,openid2,openid3'
    """
    raw = os.getenv("WECHAT_TO_USER_OPENIDS", "").strip()
    if not raw:
        # Fallback to old single openid format for backward compatibility
        old_raw = os.getenv("WECHAT_TO_USER_OPENID", "").strip()
        if old_raw:
            return [old_raw]
        raise ConfigError("Missing required environment variable: WECHAT_TO_USER_OPENIDS")

    # Try parsing as JSON array first
    try:
        openids = json.loads(raw)
        if isinstance(openids, list):
            return [oid.strip() for oid in openids if oid.strip()]
    except (json.JSONDecodeError, TypeError):
        pass

    # Fall back to comma-separated format
    return [oid.strip() for oid in raw.split(",") if oid.strip()]


def load_settings() -> Settings:
    load_dotenv()

    enable_weather = _get_bool("ENABLE_WEATHER", default=False)
    qweather_api_key = os.getenv("QWEATHER_API_KEY", "").strip() or None
    if enable_weather and not qweather_api_key:
        raise ConfigError("ENABLE_WEATHER=true requires QWEATHER_API_KEY")

    anniversary_date = os.getenv("ANNIVERSARY_DATE", "").strip() or None
    if anniversary_date:
        try:
            datetime.strptime(anniversary_date, "%Y-%m-%d")
        except ValueError as exc:
            raise ConfigError("ANNIVERSARY_DATE must be in YYYY-MM-DD format") from exc

    return Settings(
        wechat_app_id=_require_env("WECHAT_APP_ID"),
        wechat_app_secret=_require_env("WECHAT_APP_SECRET"),
        wechat_template_id=_require_env("WECHAT_TEMPLATE_ID"),
        wechat_to_user_openids=_get_openid_list(),
        tz=os.getenv("TZ", "Asia/Shanghai").strip() or "Asia/Shanghai",
        enable_weather=enable_weather,
        qweather_api_key=qweather_api_key,
        weather_location=os.getenv("WEATHER_LOCATION", "Beijing").strip() or "Beijing",
        fixed_title=os.getenv("FIXED_TITLE", "早安提醒").strip() or "早安提醒",
        fixed_remark=os.getenv("FIXED_REMARK", "祝你今天顺利").strip() or "祝你今天顺利",
        anniversary_date=anniversary_date,
        anniversary_name=os.getenv("ANNIVERSARY_NAME", "纪念日").strip() or "纪念日",
        field_first=os.getenv("FIELD_FIRST", "first").strip() or "first",
        field_date=os.getenv("FIELD_DATE", "date").strip() or "date",
        field_weekday=os.getenv("FIELD_WEEKDAY", "weekday").strip() or "weekday",
        field_weather=os.getenv("FIELD_WEATHER", "weather").strip() or "weather",
        field_anniversary=os.getenv("FIELD_ANNIVERSARY", "anniversary").strip() or "anniversary",
        field_remark=os.getenv("FIELD_REMARK", "remark").strip() or "remark",
        request_timeout_seconds=_get_int("REQUEST_TIMEOUT_SECONDS", 10),
    )
