from __future__ import annotations

import requests


class WeatherProviderError(RuntimeError):
    """Raised when weather provider is unavailable."""


# City name to Location ID mapping for common Chinese cities
CITY_LOCATION_MAP: dict[str, str] = {
    # Beijing
    "北京": "101010100", "Beijing": "101010100", "beijing": "101010100",
    # Shanghai
    "上海": "101020100", "Shanghai": "101020100", "shanghai": "101020100",
    # Guangzhou
    "广州": "101280101", "Guangzhou": "101280101", "guangzhou": "101280101",
    # Shenzhen
    "深圳": "101280601", "Shenzhen": "101280601", "shenzhen": "101280601",
    # Zhoukou
    "周口": "101181401", "Zhoukou": "101181401", "zhoukou": "101181401",
    # Zhengzhou
    "郑州": "101180101", "Zhengzhou": "101180101", "zhengzhou": "101180101",
    # You can add more cities as needed
}


def fetch_openweather_summary(
    api_key: str,
    location: str,
    timeout_seconds: int = 10,
) -> str:
    """Fetch daily weather forecast from QWeather API.

    This function name is kept for backward compatibility.
    Internally it uses QWeather (和风天气) daily weather forecast API.
    Uses custom API Host for authentication.

    Args:
        api_key: QWeather API key
        location: City name (e.g., "Beijing", "北京", "Shanghai") or LocationID (e.g., "101010100")
        timeout_seconds: Request timeout in seconds

    Returns:
        Weather summary string in format: "{location} {description}，气温 {temp_min}~{temp_max}°C，{wind}"
    """
    # Custom API Host for QWeather
    api_host = "https://mc7p42xtf5.re.qweatherapi.com"

    # Map city name to location ID
    location_id = CITY_LOCATION_MAP.get(location, location)
    display_name = location

    # Get daily weather forecast (3 days) directly
    weather_url = f"{api_host}/v7/weather/3d"
    weather_params = {
        "location": location_id,
    }
    headers = {
        "X-QW-Api-Key": api_key,
        "Accept-Encoding": "gzip, deflate"
    }
    weather_response = requests.get(weather_url, params=weather_params, headers=headers, timeout=timeout_seconds, proxies={"http": None, "https": None})
    weather_response.raise_for_status()
    weather_payload = weather_response.json()

    if weather_payload.get("code") != "200":
        raise WeatherProviderError(f"Weather API failed: {weather_payload}")

    daily = weather_payload.get("daily", [])
    if not daily:
        raise WeatherProviderError("No weather data returned")

    # Get today's forecast (first item)
    today = daily[0]
    text_day = today.get("textDay", "未知天气")
    temp_min = today.get("tempMin")
    temp_max = today.get("tempMax")
    wind_dir_day = today.get("windDirDay", "")
    wind_scale_day = today.get("windScaleDay", "")

    if temp_min is None or temp_max is None:
        raise WeatherProviderError("Missing temperature fields in weather response")

    # Format: 周口 晴，气温 5~15°C，东北风3-2级
    wind_info = f"，{wind_dir_day}{wind_scale_day}级" if wind_dir_day else ""
    return f"{display_name} {text_day}，气温 {temp_min}~{temp_max}°C{wind_info}"
