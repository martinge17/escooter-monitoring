use std::time::Duration;

use anyhow::Result;
use chrono::Local;
use serde::{Deserialize, Serialize};
use serialport::SerialPort;

use crate::gps_location::GPSInfo;
use crate::session::BatteryInfo;
use crate::MiSession;

#[derive(Debug, Serialize, Deserialize)]
pub struct Telemetry {
    pub timestamp: String,

    /**
     * Speed in kilometers per hour. Obtained by scooter
     */
    pub speed_kmh: f32,

    /**
     * Distance (meters) since first boot of scooter.
     */
    pub total_distance_m: u32,
    /**
     * Distance (meters). Current trip distance
     */
    pub trip_distance_m: i16,
    pub uptime: Duration,

    pub battery_info: BatteryInfo,

    pub gpsinfo: GPSInfo,
}

impl Telemetry {
    pub async fn pull_scooter(session: &mut MiSession, port: &mut dyn SerialPort) -> Result<Self> {
        //Pull the necessary data
        let motorinfo = session.motor_info().await?;

        let battery_info = session.battery_info().await?;

        //Pull GPS data
        let gps = GPSInfo::get_gps_position(port)?;

        let time = Local::now().to_rfc3339();

        let telemetry: Telemetry = Telemetry {
            timestamp: time,
            speed_kmh: motorinfo.speed_kmh,
            total_distance_m: motorinfo.total_distance_m,
            trip_distance_m: motorinfo.trip_distance_m,
            uptime: motorinfo.uptime,
            battery_info,
            gpsinfo: gps,
        };

        Ok(telemetry)
    }
}
