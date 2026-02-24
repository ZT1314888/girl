from __future__ import annotations

import requests


class WeatherProviderError(RuntimeError):
    """Raised when weather provider is unavailable."""


def fetch_openweather_summary(
    api_key: str,
    location: str,
    timeout_seconds: int = 10,
) -> str:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric",
        "lang": "zh_cn",
    }
    response = requests.get(url, params=params, timeout=timeout_seconds)
    response.raise_for_status()
    payload = response.json()

    weather_items = payload.get("weather", [])
    if not weather_items:
        raise WeatherProviderError("No weather details returned")
    description = weather_items[0].get("description", "未知天气")

    main = payload.get("main", {})
    temp = main.get("temp")
    feels_like = main.get("feels_like")
    if temp is None or feels_like is None:
        raise WeatherProviderError("Missing temperature fields in weather response")

    return f"{location} {description}，气温 {temp:.1f}°C，体感 {feels_like:.1f}°C"
