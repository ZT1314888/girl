use crate::config::Settings;
use serde::Deserialize;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum WeatherError {
    #[error("request failed: {0}")]
    Http(#[from] reqwest::Error),
    #[error("QWeather returned code {0}")]
    Api(String),
    #[error("QWeather returned no daily forecast")]
    Empty,
}

#[derive(Deserialize)]
struct Forecast {
    code: String,
    daily: Option<Vec<Day>>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct Day {
    text_day: String,
    temp_min: String,
    temp_max: String,
    wind_dir_day: Option<String>,
    wind_scale_day: Option<String>,
}

pub async fn fetch(settings: &Settings) -> Result<String, WeatherError> {
    let location = location_id(&settings.weather_location);
    let url = format!("{}/v7/weather/3d", settings.qweather_api_host.trim_end_matches('/'));
    let response = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(settings.timeout_seconds))
        .build()?
        .get(url)
        .query(&[("location", location)])
        .header("X-QW-Api-Key", settings.qweather_api_key.as_deref().unwrap_or_default())
        .send()
        .await?
        .error_for_status()?
        .json::<Forecast>()
        .await?;
    format_forecast(&settings.weather_location, response)
}

fn location_id(location: &str) -> &str {
    match location {
        "北京" | "Beijing" | "beijing" => "101010100",
        "上海" | "Shanghai" | "shanghai" => "101020100",
        "广州" | "Guangzhou" | "guangzhou" => "101280101",
        "深圳" | "Shenzhen" | "shenzhen" => "101280601",
        "周口" | "Zhoukou" | "zhoukou" => "101181401",
        "郑州" | "Zhengzhou" | "zhengzhou" => "101180101",
        other => other,
    }
}

fn format_forecast(location: &str, forecast: Forecast) -> Result<String, WeatherError> {
    if forecast.code != "200" {
        return Err(WeatherError::Api(forecast.code));
    }
    let day = forecast.daily.as_deref().and_then(|days| days.first()).ok_or(WeatherError::Empty)?;
    let wind = match day.wind_dir_day.as_deref() {
        Some(direction) if !direction.is_empty() => format!("，{}{}级", direction, day.wind_scale_day.as_deref().unwrap_or("")),
        _ => String::new(),
    };
    Ok(format!("{} {}，气温 {}~{}°C{}", location, day.text_day, day.temp_min, day.temp_max, wind))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn uses_legacy_city_ids_and_format() {
        assert_eq!(location_id("Beijing"), "101010100");
        assert_eq!(location_id("周口"), "101181401");
        let forecast: Forecast = serde_json::from_str(r#"{"code":"200","daily":[{"textDay":"晴","tempMin":"5","tempMax":"15","windDirDay":"东北风","windScaleDay":"3-4"}]}"#).unwrap();
        assert_eq!(format_forecast("周口", forecast).unwrap(), "周口 晴，气温 5~15°C，东北风3-4级");
    }

    #[test]
    fn api_error_is_visible() {
        let forecast: Forecast = serde_json::from_str(r#"{"code":"401"}"#).unwrap();
        assert!(matches!(format_forecast("北京", forecast), Err(WeatherError::Api(code)) if code == "401"));
    }
}
