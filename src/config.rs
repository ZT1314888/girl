use chrono::NaiveDate;
use serde::Deserialize;
use std::{env, fs, path::PathBuf};
use thiserror::Error;

#[derive(Debug, Clone, Deserialize)]
pub struct Recipient { pub openid: String, pub name: String }
#[derive(Debug, Clone)]
pub struct Settings {
    pub app_id: String, pub app_secret: String, pub morning_template_id: String, pub evening_template_id: String,
    pub recipients: Vec<Recipient>, pub timezone: String, pub weather_enabled: bool, pub qweather_api_key: Option<String>,
    pub qweather_api_host: String, pub weather_location: String, pub anniversary_date: NaiveDate, pub anniversary_name: String, pub timeout_seconds: u64,
    pub data_dir: PathBuf, pub morning_time: (u32, u32), pub evening_time: (u32, u32),
}
#[derive(Debug, Error)]
pub enum ConfigError {
    #[error("missing environment variable: {0}")] Missing(String),
    #[error("invalid configuration: {0}")] Invalid(String),
    #[error("invalid recipients JSON: {0}")] Recipients(#[from] serde_json::Error),
    #[error("invalid date: {0}")] Date(#[from] chrono::ParseError),
}
impl Settings {
    pub fn from_env() -> Result<Self, ConfigError> {
        let weather_enabled = parse_bool("ENABLE_WEATHER", false)?;
        let qweather_api_key = env::var("QWEATHER_API_KEY").ok().filter(|v| !v.trim().is_empty());
        if weather_enabled && qweather_api_key.is_none() { return Err(ConfigError::Invalid("ENABLE_WEATHER=true requires QWEATHER_API_KEY".into())); }
        let recipients: Vec<Recipient> = serde_json::from_str(&required("RECIPIENTS_JSON")?)?;
        if recipients.is_empty() { return Err(ConfigError::Invalid("RECIPIENTS_JSON must not be empty".into())); }
        Ok(Self {
            app_id: required("WECHAT_APP_ID")?, app_secret: required("WECHAT_APP_SECRET")?,
            morning_template_id: required("MORNING_TEMPLATE_ID")?, evening_template_id: required("EVENING_TEMPLATE_ID")?,
            recipients, timezone: env::var("TZ").unwrap_or_else(|_| "Asia/Shanghai".into()), weather_enabled, qweather_api_key,
            qweather_api_host: env::var("QWEATHER_API_HOST").unwrap_or_else(|_| "https://mc7p42xtf5.re.qweatherapi.com".into()),
            weather_location: env::var("WEATHER_LOCATION").unwrap_or_else(|_| "周口".into()),
            anniversary_date: env::var("ANNIVERSARY_DATE").unwrap_or_else(|_| "2024-12-31".into()).parse()?,
            anniversary_name: env::var("ANNIVERSARY_NAME").unwrap_or_else(|_| "相爱".into()),
            timeout_seconds: parse_positive("REQUEST_TIMEOUT_SECONDS", 30)?, data_dir: PathBuf::from(env::var("DATA_DIR").unwrap_or_else(|_| "/data".into())),
            morning_time: parse_time("MORNING_TIME", "08:00")?, evening_time: parse_time("EVENING_TIME", "18:00")?,
        })
    }
}
fn required(name: &str) -> Result<String, ConfigError> { env::var(name).ok().filter(|v| !v.trim().is_empty()).ok_or_else(|| ConfigError::Missing(name.into())) }
fn parse_bool(name: &str, default: bool) -> Result<bool, ConfigError> { match env::var(name).ok().as_deref() { None => Ok(default), Some("1"|"true"|"yes"|"on") => Ok(true), Some("0"|"false"|"no"|"off") => Ok(false), Some(v) => Err(ConfigError::Invalid(format!("{name}={v}"))) } }
fn parse_positive(name: &str, default: u64) -> Result<u64, ConfigError> { let v = env::var(name).ok().map(|x| x.parse::<u64>().map_err(|_| ConfigError::Invalid(format!("{name}={x}")))).transpose()?.unwrap_or(default); if v == 0 { Err(ConfigError::Invalid(format!("{name} must be positive"))) } else { Ok(v) } }
fn parse_time(name: &str, default: &str) -> Result<(u32, u32), ConfigError> { let raw = env::var(name).unwrap_or_else(|_| default.into()); let p: Vec<_> = raw.split(':').collect(); if p.len()!=2 { return Err(ConfigError::Invalid(format!("{name} must be HH:MM"))); } let h=p[0].parse().ok(); let m=p[1].parse().ok(); if h.is_none()||m.is_none()||h.unwrap()>23||m.unwrap()>59 { return Err(ConfigError::Invalid(format!("{name} must be HH:MM"))); } Ok((h.unwrap(),m.unwrap())) }
pub fn ensure_data_dir(path: &PathBuf) -> Result<(), std::io::Error> { fs::create_dir_all(path) }
