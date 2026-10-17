use chrono::NaiveDate;
use rusqlite::{params, Connection};
use std::path::Path;
use thiserror::Error;
#[derive(Debug, Error)] pub enum StateError { #[error("sqlite: {0}")] Sql(#[from] rusqlite::Error) }
pub struct State { conn: Connection }
impl State {
    pub fn open(path: &Path) -> Result<Self, StateError> { let conn=Connection::open(path)?; conn.execute_batch("CREATE TABLE IF NOT EXISTS deliveries (day TEXT NOT NULL, slot TEXT NOT NULL, openid TEXT NOT NULL, status TEXT NOT NULL, updated_at TEXT NOT NULL, PRIMARY KEY(day,slot,openid));")?; Ok(Self{conn}) }
    pub fn claim(&self, day:NaiveDate,slot:&str,openid:&str)->Result<bool,StateError>{ let n=self.conn.execute("INSERT OR IGNORE INTO deliveries(day,slot,openid,status,updated_at) VALUES(?1,?2,?3,'attempted',datetime('now'))",params![day.to_string(),slot,openid])?; Ok(n==1) }
    pub fn finish(&self,day:NaiveDate,slot:&str,openid:&str,status:&str)->Result<(),StateError>{ self.conn.execute("UPDATE deliveries SET status=?1,updated_at=datetime('now') WHERE day=?2 AND slot=?3 AND openid=?4",params![status,day.to_string(),slot,openid])?; Ok(()) }
}
