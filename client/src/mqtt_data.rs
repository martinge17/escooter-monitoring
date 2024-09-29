use crate::config::CONFIG;
use anyhow::{anyhow, Error, Result};
use paho_mqtt::AsyncClient;
use paho_mqtt::{ConnectOptionsBuilder, CreateOptionsBuilder};
use std::time::Duration;
use tracing::{error, info};

pub struct MqttClient {
    pub client: AsyncClient,
}

impl MqttClient {
    pub async fn new() -> Result<Self> {
        let create_opts = CreateOptionsBuilder::new()
            .server_uri(&CONFIG.mqtt.broker)
            .client_id(&CONFIG.mqtt.client)
            .mqtt_version(5) // Use MQTTv5
            .finalize();

        let mqtt_client = AsyncClient::new(create_opts).unwrap_or_else(|err| {
            panic!("Error creating the MQTT client: {:?}", err);
        });

        let conn_opts = ConnectOptionsBuilder::new_v5()
            .keep_alive_interval(Duration::from_secs(CONFIG.mqtt.keep_alive))
            .automatic_reconnect(
                Duration::from_secs(CONFIG.mqtt.reconnect_min),
                Duration::from_secs(CONFIG.mqtt.reconnect_max),
            )
            .retry_interval(Duration::from_secs(3))
            .clean_start(true)
            .finalize();

        info!("Starting MQTT connection");

        if let Err(e) = mqtt_client.connect(conn_opts).await {
            error!("Unable to connect to MQTT broker: {:?}", e);

            while !mqtt_client.is_connected() {
                info!("Reconnecting!");
                match mqtt_client.reconnect().await {
                    Ok(_) => break,
                    Err(e) => {
                        error!("Unable to connect to MQTT broker: {:?}", e);
                        tokio::time::sleep(Duration::from_secs(3)).await;
                    }
                }
            }
        }

        info!("Connected to MQTT broker!");

        Ok(MqttClient {
            client: mqtt_client,
        })
    }
}
