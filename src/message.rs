use chrono::{Datelike, NaiveDate};
use serde::Serialize;
use crate::config::{Recipient, Settings};

#[derive(Debug, Serialize)] pub struct Payload { pub touser: String, pub template_id: String, pub data: serde_json::Map<String, serde_json::Value> }
pub fn build(settings: &Settings, recipient: &Recipient, slot: &str, date: NaiveDate, weather: Option<&str>) -> Payload {
    let title = if slot == "morning" { "早安提醒" } else { "晚安提醒" };
    let weekday = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"][date.weekday().num_days_from_monday() as usize];
    let days = (date - settings.anniversary_date).num_days().max(0);
    let anniversary = format!("和{}{}已经{}天", recipient.name, settings.anniversary_name, days);
    let mut data = serde_json::Map::new();
    let put = |map: &mut serde_json::Map<String, serde_json::Value>, key: &str, value: String| { map.insert(key.into(), serde_json::json!({"value": value})); };
    put(&mut data, "first", format!("来自{}的{}", recipient.name, title));
    put(&mut data, "keyword1", date.format("%Y-%m-%d").to_string());
    put(&mut data, "keyword2", weekday.into());
    put(&mut data, "keyword3", weather.unwrap_or("天气信息暂不可用").into());
    put(&mut data, "keyword4", anniversary.clone());
    put(&mut data, "remark", format!("好好吃饭,好好睡觉,好好去爱你的{}", recipient.name));
    // Keep aliases for older test-account templates that use custom names.
    put(&mut data, "date", date.format("%Y-%m-%d").to_string());
    put(&mut data, "weekday", weekday.into());
    put(&mut data, "weather", weather.unwrap_or("天气信息暂不可用").into());
    put(&mut data, "anniversary", anniversary);
    put(&mut data, "name", recipient.name.clone());
    let template_id = if slot == "morning" { &settings.morning_template_id } else { &settings.evening_template_id };
    Payload { touser: recipient.openid.clone(), template_id: template_id.clone(), data }
}

#[cfg(test)]
mod tests { use super::*; use crate::config::Settings; use std::path::PathBuf;
    #[test] fn builds_personalized_payload() { let s=Settings { app_id:"a".into(),app_secret:"b".into(),morning_template_id:"m".into(),evening_template_id:"e".into(),recipients:vec![],timezone:"Asia/Shanghai".into(),weather_enabled:false,qweather_api_key:None,qweather_api_host:"https://example.com".into(),weather_location:"周口".into(),anniversary_date:"2024-12-31".parse().unwrap(),anniversary_name:"相爱".into(),timeout_seconds:10,data_dir:PathBuf::new(),morning_time:(8,0),evening_time:(18,0) }; let r=Recipient{openid:"id".into(),name:"昊琨".into()}; let start=build(&s,&r,"morning","2024-12-31".parse().unwrap(),None); assert_eq!(start.data["keyword4"]["value"],"和昊琨相爱已经0天"); let p=build(&s,&r,"morning","2025-01-01".parse().unwrap(),None); assert_eq!(p.data["first"]["value"],"来自昊琨的早安提醒"); assert_eq!(p.data["keyword4"]["value"],"和昊琨相爱已经1天"); assert_eq!(p.data["remark"]["value"],"好好吃饭,好好睡觉,好好去爱你的昊琨"); }
}
