from __future__ import annotations

import requests


class WeatherProviderError(RuntimeError):
    """Raised when weather provider is unavailable."""


def fetch_openweather_summary(
    api_key: str,
    location: str,
    timeout_seconds: int = 10,
) -> str:
    """Fetch weather summary from QWeather API.

    This function name is kept for backward compatibility.
    Internally it uses QWeather (和风天气) API.

    Args:
        api_key: QWeather API key
        location: City name (e.g., "Beijing", "北京", "Shanghai")
        timeout_seconds: Request timeout in seconds

    Returns:
        Weather summary string in format: "{location} {description}，气温 {temp}°C，体感 {feels_like}°C"
    """
    # Step 1: City lookup to get Location ID
    city_lookup_url = "https://geoapi.qweather.com/v2/city/lookup"
    city_params = {
        "location": location,
        "key": api_key,
    }
    city_response = requests.get(city_lookup_url, params=city_params, timeout=timeout_seconds)
    city_response.raise_for_status()
    city_payload = city_response.json()

    if city_payload.get("code") != "200":
        raise WeatherProviderError(f"City lookup failed: {city_payload.get('location', [])}")

    locations = city_payload.get("location", [])
    if not locations:
        raise WeatherProviderError(f"City not found: {location}")

    location_id = locations[0].get("id")
    location_name = locations[0].get("name", location)

    # Step 2: Get weather data using Location ID
    weather_url = "https://devapi.qweather.com/v7/weather/now"
    weather_params = {
        "location": location_id,
        "key": api_key,
    }
    weather_response = requests.get(weather_url, params=weather_params, timeout=timeout_seconds)
    weather_response.raise_for_status()
    weather_payload = weather_response.json()

    if weather_payload.get("code") != "200":
        raise WeatherProviderError(f"Weather API failed: {weather_payload}")

    now = weather_payload.get("now", {})
    if not now:
        raise WeatherProviderError("No weather data returned")

    temp = now.get("temp")
    feels_like = now.get("feelsLike")
    description = now.get("text", "未知天气")

    if temp is None or feels_like is None:
        raise WeatherProviderError("Missing temperature fields in weather response")

    return f"{location_name} {description}，气温 {temp}°C，体感 {feels_like}°C"
