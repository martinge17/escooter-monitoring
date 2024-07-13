use std::time::Duration;
use std::io::{self, Write, Read};
use std::thread::sleep;
use serialport::SerialPort;
//use tracing::info;
use tracing::{debug, info};
use io::Error;
use serde::Serialize;
// Use https://crates.io/crates/serialport

const PORT: &str = "/dev/ttyUSB2";
const BAUDRATE: u32 = 115200;
const TIMEOUT: u32 = 1;

//TODO: SOLVE, when this function is called, it should

/**
* get_gps_coordinates returns a string with the required coordinates every X seconds, that will be coordinated with the main function
 that request data from the scooter. So when we send data to the MQTT broker we also send the latest GPS position.
*
*/

#[derive(Debug, Serialize)]
pub struct GPSInfo { //From left to right are ① Latitude, ② Longitude, ③ Date, ④ Time, ⑤ Altitude, ⑥ Speed and ⑦ Navigation Angle.
    /**
     * Charge left in scooter, in Milliamps (mA)
     */
    pub latitude: String,
    pub longitude: String,
    pub date: u32,
    pub time: f32,
    pub altitude: f32,
    pub speed: f32,
    pub nav_angle: f32
}
// TODO: COORDINATES FORMAT -> We want to use Decimal Degrees not DMS
// TODO: PARSE RESPONSE STRING INTO COORDINATES STRUCT

fn send_at(port: &mut dyn SerialPort, command: &str, back: &str, timeout: Duration) -> Result<String, Error> {
    port.write_all((command.to_string() + "\r\n").as_bytes())?;
    println!("Sent command: {}", command);

    sleep(timeout);

    let mut buffer: Vec<u8> = vec![0; 1024];
    let mut rec_buff = String::new();

    if port.bytes_to_read()? > 0 {
        sleep(Duration::from_millis(10));
        let bytes_read = port.read(&mut buffer)?;
        rec_buff.push_str(&String::from_utf8_lossy(&buffer[..bytes_read]));
    }

    if rec_buff.contains(back) {
        //println!("{}", rec_buff);
        Ok(rec_buff)
    } else {
        //println!("{} ERROR", command);
        //println!("{} back:\t{}", command, rec_buff);
        Ok("NO MATCH".to_string())
    }
}

fn get_gps_position(port: &mut dyn SerialPort) -> Result<(), Error> {
    println!("Start GPS session...");

    //send_at(port, "AT+CGPS=0", "OK", Duration::from_secs(1))?;
    //send_at(port, "AT+CGPS=1", "OK", Duration::from_secs(1))?;
    //sleep(Duration::from_secs(2));

    let mut rec_null = true;
    //TODO: ONE QUERY ONLY
    //TODO: Create struct for storing Coordinates date and parse to that structure
    while rec_null {
        let response = send_at(port, "AT+CGPSINFO", "+CGPSINFO: ", Duration::from_secs(1))?;
        if response != "NO MATCH" {
            if response.contains(",,,,,,,") { //Instead of stopping, TODO: Return Null Island coordinates
                info!("GPS not ready or error");
                //sleep(Duration::from_secs(1));
            } else {
                println!("GPS Data: {}", response);
            }
        } else {
            println!("NOT MATCHED");
            //send_at(port, "AT+CGPS=0", "OK", Duration::from_secs(1))?;
            return Ok(());
        }
        sleep(Duration::from_millis(1000));
    }

    Ok(())
}

fn gps_status() -> Result<bool,Error> {
    let mut port = serialport::new(PORT, BAUDRATE)
        .timeout(Duration::from_millis(10))
        .open()
        .expect("Failed to open port");

    let response = send_at(&mut *port, "AT+CGPS?", "+CGPS: ", Duration::from_secs(1))?;

    // Parse response. Format is +CGPS: 1,1   or +CGPS: 0,1
    if response != "NO MATCH" && response.contains("+CGPS: 1,1") {
        print!("Enabled!");
        return Ok(true)
    }

    Ok(false)
}
//TODO: OPTION true or ERROR?????????
fn enable_gps() -> Result<bool,Error> {
    let mut port = serialport::new(PORT, BAUDRATE)
        .timeout(Duration::from_millis(10))
        .open()
        .expect("Failed to open port");

    let response = send_at(&mut *port, "AT+CGPS?", "+CGPS: ", Duration::from_secs(1))?;

    // Parse response. Format is +CGPS: 1,1   or +CGPS: 0,1
    if response != "NO MATCH" && response.contains("+CGPS: 1,1") {
        debug!("GPS already enabled!");
        return Ok(true)
    }

    debug!("Enabling GPS...");

    let response = send_at(&mut *port, "AT+CGPS=1", "OK", Duration::from_secs(1))?;

    // Parse response. Format is +CGPS: 1,1   or +CGPS: 0,1
    if response != "NO MATCH" && response.contains("+CGPS: 1,1") {
        print!("Enabled!");
        sleep(Duration::from_secs(2)); //GIVE TIME TO ENABLE GPS
        return Ok(true)
    }

    Ok(false) //TODO: Convert to error
}


fn main() {

    /*if let Err(e) = get_gps_position(&mut *port) {
        eprintln!("Failed to get GPS position: {}", e);
    }
    */

    //print!("{}", send_at(&mut *port, "AT+CGPS=1", "OK", Duration::from_secs(1)).unwrap());

    let a = enable_gps().unwrap();

    if !a { println!("NOT")}

}

