/*
   This file contains the main activity of the program.
   - It loads all the configuration parameters from the config file. => Config is loaded in config.rs file.
   - It connects to the scooter
   - It connects to the MQTT broker
   - It pull data from the scooter and sends it via MQTT to the server

*/
use anyhow::{anyhow, Result};
use btleplug::api::BDAddr;
use btleplug::platform::Peripheral;

use m365::config::CONFIG;
use m365::gps_location::enable_gps;
use m365::telemetry::Telemetry;
use m365::{AuthToken, ConnectionHelper, LoginRequest, MiSession, MqttClient, ScooterScanner};
use std::path::Path;
use std::process::exit;
use std::thread::sleep;
use std::time::Duration;
use tokio::fs::File;
use tokio::io::AsyncReadExt;
use tracing::{error, info, Level};
use tracing_subscriber;
use tracing_subscriber::fmt::format::FmtSpan;

/**
 Provided a path it loads the contents of the MI token file necessary to connect to the scooter
*/
async fn load_token() -> Result<AuthToken> {
    let path = Path::new(&CONFIG.scooter.token_file_path);
    tracing::debug!("Opening token: {:?}", path);

    let mut f = File::open(path).await?;
    let mut buffer: AuthToken = [0; 12];

    f.read(&mut buffer).await?;

    Ok(buffer)
}

async fn load_mac() -> Result<BDAddr> {
    let mac = BDAddr::from_str_no_delim(&CONFIG.scooter.mac.trim()).expect("Invalid mac address");

    Ok(mac)
}

async fn relink_scooter(
    connection: ConnectionHelper,
    device: &Peripheral,
    token: &AuthToken,
    mi_session: MiSession,
) -> Result<MiSession> {
    loop {
        info!("Establishing connection with the scooter");

        match connection.connect().await {
            Ok(true) => {}
            Ok(false) => {
                info!("Already connected!");
                return Ok(mi_session);
            }
            Err(e) => {
                info!("Can't reach the scooter! Is it powered on? Relaunching the program....");
                return Err(anyhow!("Can't reach the scooter! Is it power on?: {}", e));
            }
        }

        info!("Connection established. Now trying to log in");

        //Once connected, login into the scooter (key exchange, read more in the protocol documentation)
        let mut request = match LoginRequest::new(&device, &token).await {
            Ok(req) => req,
            Err(e) => {
                error!("Failed to create login request: {}", e);
                tokio::time::sleep(Duration::from_secs(2)).await;
                continue; //Try again at next iteration
            }
        };

        //Start the session
        match request.start().await {
            Ok(se) => return Ok(se),
            Err(e) => {
                error!("Failed to start session: {}", e);
                tokio::time::sleep(Duration::from_secs(2)).await;
                continue;
            }
        };
    }
}

async fn link_scooter(
    connection: ConnectionHelper,
    device: &Peripheral,
    token: &AuthToken,
) -> Result<MiSession> {
    loop {
        info!("Establishing connection with the scooter");
        match connection.reconnect().await {
            Ok(_) => {}
            Err(..) => {
                info!("Can't reach the scooter! Is it powered on? Relaunching the program....");
                return Err(anyhow!("Can't reach the scooter! Is it power on?"));
            }
        };

        info!("Connection established. Now trying to log in");
        //Once connected, login into the scooter (key exchange, read more in the protocol documentation)
        let mut request = match LoginRequest::new(&device, &token).await {
            Ok(req) => req,
            Err(e) => {
                error!("Failed to create login request: {}", e);
                tokio::time::sleep(Duration::from_secs(2)).await;
                continue; //Try again at next iteration
            }
        };

        //Start the session
        match request.start().await {
            Ok(se) => return Ok(se),
            Err(e) => {
                error!("Failed to start session: {}", e);
                tokio::time::sleep(Duration::from_secs(2)).await;
                continue;
            }
        };
    }
}

#[tokio::main(flavor = "multi_thread")]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_max_level(Level::INFO) //DEBUG
        .with_span_events(FmtSpan::CLOSE)
        .init();

    //Load token
    let token = load_token().await?;
    //Load MAC
    let mac = load_mac().await?;

    info!("Searching scooter with address: {}", mac);

    //Search for scooter with the MAC address provided
    let mut scanner = ScooterScanner::new().await?; //TODO TIMEOUT?
    let scooter = scanner.wait_for(&mac).await?;
    let device = scanner.peripheral(&scooter).await?;

    //Connect with the scooter
    let mut connection = ConnectionHelper::new(&device);

    //This inside function
    let mut session = match link_scooter(connection, &device, &token).await {
        Ok(ses) => ses,
        Err(e) => {
            error!("{}", e);
            exit(1);
        }
    };

    //Once we establish an encrypted connection with the scooter, continue the flow by connecting to the MQTT broker

    //Call MQTT
    let mqtt_client = MqttClient::new().await?;

    //Open Serial connection
    let mut port = serialport::new(&CONFIG.serial.serial_port, CONFIG.serial.baudrate)
        .timeout(Duration::from_millis(10))
        .open()
        .expect("Failed to open port");

    //Enable GPS
    enable_gps(&mut *port).expect("Can't enable GPS");

    loop {
        let data = match Telemetry::pull_scooter(&mut session, &mut *port).await {
            Ok(data) => data,
            Err(e) => {
                error!("Error pulling data from scooter: {}", e);
                connection = ConnectionHelper::new(&device);
                session = match relink_scooter(connection, &device, &token, session).await {
                    Ok(ses) => ses,
                    Err(..) => {
                        exit(1);
                    }
                };
                continue; //Try to pull data again on next iteration
            }
        };

        let json_payload = serde_json::to_string(&data)?;

        info!("Publishing message: {}", json_payload);
        //We use QOS_0 since it is high-frequency and less important data, then it is acceptable to miss a few updates.
        let msg = paho_mqtt::Message::new(&CONFIG.mqtt.topic, json_payload, paho_mqtt::QOS_0);

        if let Err(e) = mqtt_client.client.publish(msg).await {
            error!("Failed to send MQTT message: {:?}", e);
        }

        tokio::time::sleep(Duration::from_secs(CONFIG.mqtt.send_interval)).await;
    }
}
