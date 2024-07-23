use anyhow::Result;
use lazy_static::lazy_static;
use serde::Deserialize;
use std::fs;
use std::path::Path;
use toml;

/**
Load configuration from file
 */

#[derive(Debug, Deserialize)]
pub struct Mqtt {
    pub broker: String,
    pub client: String,
    pub topic: String,
}

#[derive(Debug, Deserialize)]
pub struct Scooter {
    pub mac: String,
    pub token_file_path: String,
}

#[derive(Debug, Deserialize)]
pub struct Serial {
    pub serial_port: String,
    pub baudrate: i32,
}

#[derive(Debug, Deserialize)]
pub struct Config {
    pub mqtt: Mqtt,
    pub scooter: Scooter,
    pub serial: Serial,
}

//While LazyLock is in alpha, I will use the deprecated but functional lazy_static crate https://github.com/rust-lang-nursery/lazy-static.rs

impl Config {
    pub fn load_config(file_path: &str) -> Result<Self> {
        // Read config file
        let config_string = fs::read_to_string(Path::new(file_path)).unwrap_or_else(|_| {
            panic!(
                "Configuration file not found!: Expected '{}' file.",
                file_path
            )
        });

        let config: Config = toml::from_str(&config_string)?;

        Ok(config)
    }
}

lazy_static! {
    pub static ref CONFIG: Config = Config::load_config("martinete.toml").unwrap();
}