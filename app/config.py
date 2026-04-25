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
        fixed_remark=os.getenv("FIXED_REMARK", (
            "张彤你好，我是王昊琨，那次的分手对你来说可能很突然，"
            "我知道你当时很不安很难受，我也一样，"
            "那时的你应该把我想的很恶心吧，"
            "自上次工作结束后，其实对我而言是场回不了头的灾难，"
            "投递了简历无果后我开始怀疑自己，"
            "怀疑自己当时是不是靠运气去实习的，"
            "怀疑自己是不是没有硬实力，"
            "怀疑自己是不是方向走错了，"
            "面对这些我第一次难受了起来，"
            "我也想起过你和我之间的点点滴滴，"
            "我相信你也了解我有时候很要强但是我经不住考验，"
            "我不知道当时自己做的是否是100%正确，"
            "但是失败就意味着以后的日子就是空谈，"
            "我也喜欢你爱你，所以才采用当时的那种方式，"
            "我在家内耗了很长时间，也变瘦了，"
            "当时的我估计只能用这种方式来对你说，"
            "我不想从正面来谈论这些，所以一直逃避，"
            "这一个月你也听了很多人的话吧，"
            "如果你看到这条信息，希望你可以在不经意间想起那段日子，"
            "你也因为莽撞而无意间伤害过我，"
            "你有时候傻傻的挺可爱的，"
            "现在回看那些照片我还是有点难受，"
            "我们都一路磕磕碰碰的走过，"
            "希望你以后的日子过的越来越好，平平淡淡\n"
            "-王昊琨"
        )).strip(),
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
