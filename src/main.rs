mod app;
mod config;
mod message;
mod state;
mod weather;
mod wechat;

use clap::{Parser, Subcommand};
use config::Settings;
use tracing_subscriber::EnvFilter;

#[derive(Parser)]
struct Cli { #[command(subcommand)] command: Option<Command> }
#[derive(Subcommand)]
enum Command { Preview { slot: String }, SendNow { slot: String } }

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenvy::dotenv().ok();
    tracing_subscriber::fmt().with_env_filter(EnvFilter::from_default_env()).init();
    let command = Cli::parse().command;
    if command.is_none() {
        app::run_service(Settings::from_env()?).await?;
        return Ok(());
    }
    let settings = Settings::from_env()?;
    match command.unwrap() {
        Command::Preview { slot } => app::preview(&settings, checked_slot(&slot)?)?,
        Command::SendNow { slot } => app::send_once(&settings, checked_slot(&slot)?).await?,
    }
    Ok(())
}

fn checked_slot(slot: &str) -> Result<&str, Box<dyn std::error::Error>> {
    match slot { "morning" | "evening" => Ok(slot), _ => Err("slot must be morning or evening".into()) }
}
