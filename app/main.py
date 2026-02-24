from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from .config import ConfigError, load_settings
from .message_builder import build_template_payload
from .providers.weather import WeatherProviderError, fetch_openweather_summary
from .wechat_client import WechatApiError, WechatClient


LOGGER = logging.getLogger(__name__)


def _build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Daily WeChat template sender")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Render message payload but do not send",
    )
    parser.add_argument(
        "--send-now",
        action="store_true",
        help="Explicitly trigger immediate send (useful in local testing)",
    )
    return parser.parse_args()


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def _build_weather(settings) -> str | None:
    if not settings.enable_weather:
        return None
    try:
        return fetch_openweather_summary(
            api_key=settings.weather_api_key or "",
            location=settings.weather_location,
            timeout_seconds=settings.request_timeout_seconds,
        )
    except (requests.RequestException, WeatherProviderError, ValueError) as exc:
        LOGGER.warning("Weather lookup failed, fallback to default text: %s", exc)
        return None


def _retry_send(max_attempts: int, wait_seconds: float, fn):
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            LOGGER.warning("Attempt %s/%s failed: %s", attempt, max_attempts, exc)
            if attempt < max_attempts:
                time.sleep(wait_seconds)
    if last_error is None:
        raise RuntimeError("Unknown send error")
    raise last_error


def run() -> int:
    _setup_logging()
    args = _build_args()

    try:
        settings = load_settings()
    except ConfigError as exc:
        LOGGER.error("Configuration error: %s", exc)
        return 2

    now = datetime.now(ZoneInfo(settings.tz))
    weather_text = _build_weather(settings)
    payload = build_template_payload(settings=settings, now=now, weather_text=weather_text).to_dict()

    if args.dry_run:
        LOGGER.info("Dry run enabled; no message will be sent")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.send_now:
        LOGGER.info("Send-now mode enabled")

    client = WechatClient(timeout_seconds=settings.request_timeout_seconds)
    try:
        token = _retry_send(
            max_attempts=3,
            wait_seconds=2.0,
            fn=lambda: client.get_access_token(
                app_id=settings.wechat_app_id,
                app_secret=settings.wechat_app_secret,
            ),
        )
        result = _retry_send(
            max_attempts=3,
            wait_seconds=2.0,
            fn=lambda: client.send_template_message(access_token=token, payload=payload),
        )
    except (requests.RequestException, WechatApiError) as exc:
        LOGGER.error("WeChat API call failed: %s", exc)
        return 1
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Unexpected failure: %s", exc)
        return 1

    if not result.ok:
        LOGGER.error("Template message rejected: %s %s", result.errcode, result.errmsg)
        return 1

    LOGGER.info("Template message sent successfully. msgid=%s", result.msgid)
    return 0


if __name__ == "__main__":
    sys.exit(run())
