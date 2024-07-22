use std::time::Duration;
use std::io::{self, Write, Read};
use std::thread::sleep;
use serialport::SerialPort;
use tracing::{debug, info};
use serde::Serialize;
// Use https://crates.io/crates/serialport
use anyhow::{anyhow, Result, Error};
use regex::Regex;

//TODO: Read this parameters from configuration file!
const PORT: &str = "/dev/ttyUSB2";
const BAUDRATE: u32 = 115200;
const TIMEOUT: u32 = 1;

/**
* get_gps_coordinates returns a string with the required coordinates every X seconds, that will be coordinated with the main function
 that request data from the scooter. So when we send data to the MQTT broker we also send the latest GPS position.
*
*/
const LATITUDE: i8 = 1;
const LONGITUDE: i8 = 2;

#[derive(Debug, Serialize)]
pub struct GPSInfo { //From left to right are ① Latitude, ② Longitude, ③ Date, ④ Time, ⑤ Altitude, ⑥ Speed and ⑦ Navigation Angle.

    pub latitude: f64,
    pub longitude: f64,
    pub altitude: f32,
    pub gps_speed: f32,
}

impl GPSInfo {

    pub fn parse(input: &str) -> Result<GPSInfo> {
        // Remove the "AT+CGPSINFO\r\r\n+CGPSINFO: " prefix and the trailing comma
        let data = input.trim_start_matches("AT+CGPSINFO\r\r\n+CGPSINFO: ");


        //Find the last comma and everything that follows
        let re = Regex::new(r",[^,]*$").unwrap();

        let cleaned = re.replace(data,"").to_string();

        //Split by comma
        let parts: Vec<&str> = cleaned.split(',').collect();

        debug!("{:?}",parts);

        // Extract data from fields
        let latitude = dms_to_decimal(parts[0],parts[1].chars().next().unwrap(),LATITUDE)?;
        let longitude = dms_to_decimal(parts[2],parts[3].chars().next().unwrap(),LONGITUDE)?;
        let altitude = parts[6].parse::<f32>().unwrap();
        let speed_gps = parts[7].parse::<f32>().unwrap();

        // Validate coordinates (-90 <= lat <= 90 -180 <= lon <= 180)
        if !Self::validate_coordinates(latitude,longitude){
            return Ok(Self::null_island())
        }

        // Create and return the GPSInfo struct

        Ok(GPSInfo {
            latitude,
            longitude,
            altitude,
            gps_speed: speed_gps,
        })

    }

    // Validate coordinates (-90 <= lat <= 90 -180 <= lon <= 180)
    fn validate_coordinates(lat: f64, lon: f64) -> bool {
        lat >= -90.0 && lat <= 90.0 && lon >= -180.0 && lon <= 180.0
    }

    // Returns 0 0 (Null Island) usefull when the GPS is deactivated or there is some error. https://en.wikipedia.org/wiki/Null_Island
    pub fn null_island() -> GPSInfo {

        GPSInfo {
            latitude: 0.0,
            longitude: 0.0,
            altitude: 0.0,
            gps_speed: 0.0,
        }
    }
}

// Data comes in NMEA format https://www.gpsworld.com/what-exactly-is-gps-nmea-data/
fn dms_to_decimal(degrees_minutes: &str, direction: char, axis: i8) -> Result<f64> {

    /*
    +CGPSINFO: 4319.736021,N,00824.498574,W,150724,162016.0,176.0,0.0,

    Format: DDMM.MMMMM for latitude
            DDDMM.MMMMM for longitude
    DD -> degrees
    MM -> Minutes
     */

    let (degrees, minutes_idx) = match axis {
        LATITUDE => (degrees_minutes[0..2].parse::<f64>().unwrap(),2),
        LONGITUDE => (degrees_minutes[0..3].parse::<f64>().unwrap(),3),
        _ => return Err(anyhow!("Invalid axis: only LATITUDE and LONGITUDE are compatible!"))
    };


    let minutes= degrees_minutes[minutes_idx..].parse::<f64>().unwrap();

    let mut decimal_degress = degrees + (minutes / 60.0);

    if direction == 'S' || direction == 'W' {
        decimal_degress = -decimal_degress;
    }

    Ok(decimal_degress)
}

fn send_at(port: &mut dyn SerialPort, command: &str, back: &str, timeout: Duration) -> Result<String> {
    port.write_all((command.to_string() + "\r\n").as_bytes())?;

    sleep(timeout);

    let mut buffer: Vec<u8> = vec![0; 1024];
    let mut rec_buff = String::new();

    if port.bytes_to_read()? > 0 {
        sleep(Duration::from_millis(10));
        let bytes_read = port.read(&mut buffer)?;
        rec_buff.push_str(&String::from_utf8_lossy(&buffer[..bytes_read]));
    }

    if rec_buff.contains(back) {
        Ok(rec_buff)
    } else {
        Ok("NO MATCH".to_string())
    }
}

fn get_gps_position(port: &mut dyn SerialPort) -> Result<GPSInfo> {
    debug!("Start GPS session...");

    let response = send_at(port, "AT+CGPSINFO", "+CGPSINFO: ", Duration::from_secs(1))?;
    return if response != "NO MATCH" {
        if response.contains(",,,,,,,") { //Instead of stopping return Null Island
            info!("GPS not ready or error");
            Ok(GPSInfo::null_island())
        } else {
            Ok(GPSInfo::parse(&response)?)
        }
    } else {
        Err(anyhow!("Command output mismatch GPS!"))
    }
}

fn gps_status(port: &mut dyn SerialPort) -> Result<bool> {

    let response = send_at(port, "AT+CGPS?", "+CGPS: ", Duration::from_secs(1)).unwrap();

    // Parse response. Format is +CGPS: 1,1   or +CGPS: 0,1
    if response != "NO MATCH" && response.contains("+CGPS: 1,1") {
        info!("Enabled!");
        return Ok(true)
    }

    Err(anyhow!("Can´t get GPS status!"))
}

fn enable_gps(port: &mut dyn SerialPort) -> Result<bool> {

    let response = send_at(port, "AT+CGPS?", "+CGPS: ", Duration::from_secs(1))?;

    // Parse response. Format is +CGPS: 1,1   or +CGPS: 0,1
    if response != "NO MATCH" && response.contains("+CGPS: 1,1") {
        debug!("GPS already enabled!  -> Reactivating GPS!");
        send_at(port, "AT+CGPS=0", "OK", Duration::from_secs(1)).expect("Can't disable GPS");
        sleep(Duration::from_millis(500));
    }

    debug!("Enabling GPS...");

    send_at(port, "AT+CGPS=1", "OK", Duration::from_secs(1))?;

    return Ok(true)
}


