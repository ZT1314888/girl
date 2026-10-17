use crate::{config::Settings,message::Payload};
use reqwest::Client; use serde::Deserialize; use thiserror::Error;
#[derive(Debug,Error)] pub enum WechatError { #[error("http: {0}")] Http(#[from] reqwest::Error), #[error("wechat error {0}: {1}")] Api(i64,String) }
#[derive(Deserialize)] struct TokenResponse { access_token:Option<String>,errcode:Option<i64>,errmsg:Option<String> }
#[derive(Deserialize)] struct SendResponse { errcode:i64,errmsg:String,msgid:Option<i64> }
pub struct WechatClient { client:Client }
impl WechatClient {
    pub fn new(timeout:u64)->Result<Self,reqwest::Error>{Ok(Self{client:Client::builder().timeout(std::time::Duration::from_secs(timeout)).build()?})}
    pub async fn token(&self,s:&Settings)->Result<String,WechatError>{let b:TokenResponse=self.client.get("https://hk.api.weixin.qq.com/cgi-bin/token").query(&[("grant_type","client_credential"),("appid",s.app_id.as_str()),("secret",s.app_secret.as_str())]).send().await?.json().await?; b.access_token.ok_or_else(||WechatError::Api(b.errcode.unwrap_or(-1),b.errmsg.unwrap_or_else(||"unknown error".into())))}
    pub async fn send(&self,token:&str,p:&Payload)->Result<i64,WechatError>{let b:SendResponse=self.client.post("https://hk.api.weixin.qq.com/cgi-bin/message/template/send").query(&[("access_token",token)]).json(p).send().await?.json().await?; if b.errcode!=0{return Err(WechatError::Api(b.errcode,b.errmsg));} Ok(b.msgid.unwrap_or_default())}
}
