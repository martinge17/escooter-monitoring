/*
   This file contains the main activity of the program.
   - It loads all the configuration parameters from the config file. => Config is loaded in config.rs file.
   - It connects to the scooter
   - It connects to the MQTT broker
   - It pull data from the scooter and sends it via MQTT to the server

*/
use anyhow::Result;
use btleplug::api::BDAddr;
use m365::config::CONFIG;
use m365::gps_location::enable_gps;
use m365::telemetry::Telemetry;
use m365::{AuthToken, ConnectionHelper, LoginRequest, MqttClient, ScooterScanner};
use std::path::Path;
use std::time::Duration;
use tokio::fs::File;
use tokio::io::AsyncReadExt;
use tracing::{info, Level};
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

#[tokio::main(flavor = "multi_thread")]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_max_level(Level::INFO)
        .with_span_events(FmtSpan::CLOSE)
        .init();

    //Load token
    let token = load_token().await?;
    //Load MAC
    let mac = load_mac().await?;

    info!("Searching scooter with address: {}", mac);

    //Search for scooter with the MAC address provided
    let mut scanner = ScooterScanner::new().await?;
    let scooter = scanner.wait_for(&mac).await?;
    let device = scanner.peripheral(&scooter).await?;

    //Connect with the scooter
    let connection = ConnectionHelper::new(&device);
    connection.reconnect().await?; //TODO: TEMPORALLY RETRY TO INFINITE (12 hours) REWORK FROM HERE THIS ON SECOND ITERATION TO IMPLEMENT THE BACKOFF

    //Once connected, login into the scooter (key exchange, read more in the protocol documentation)
    let mut request = LoginRequest::new(&device, &token).await?;
    let mut session = request.start().await?;

    //Once we establish an encrypted connection with the scooter, continue the flow by connecting to the MQTT broker

    //Call MQTT
    let mqtt_client = MqttClient::new().await?;
    //TODO: LOOP FOR MQTT CONNECTION

    //Open Serial connection
    let mut port = serialport::new(&CONFIG.serial.serial_port, CONFIG.serial.baudrate)
        .timeout(Duration::from_millis(10))
        .open()
        .expect("Failed to open port");

    //Enable GPS
    enable_gps(&mut *port).expect("Can't enable GPS");

    //TODO: Call loop to pull data from the scooter and send it
    loop {
        //TODO: RECONNECT TO SCOOTER IF FAILED
        let data = Telemetry::pull_scooter(&mut session, &mut *port).await?;
        let json_payload = serde_json::to_string(&data)?;

        info!("Publishing message: {}", json_payload);
        //We use QOS_0 since it is high-frequency and less important data, then it is acceptable to miss a few updates.
        let msg = paho_mqtt::Message::new(&CONFIG.mqtt.topic, json_payload, paho_mqtt::QOS_0);
        //TODO: REWORK!!! INSTEAD OF EXIT IT SHOULD KEEP RETR

        if let Err(e) = mqtt_client.client.publish(msg).await {
            tracing::error!("Failed to send MQTT message: {:?}", e);
            //TODO: CHECK IF THERE IS CONNECTION WITH THE BROKER !!!! IF NOT THEN RECONNECT
        }

        tokio::time::sleep(Duration::from_secs(CONFIG.mqtt.send_interval)).await;
    }
}
