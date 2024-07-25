use crate::config::CONFIG;
use anyhow::{anyhow, Error, Result};
use paho_mqtt::AsyncClient;
use paho_mqtt::{ConnectOptionsBuilder, CreateOptionsBuilder};
use serde::Deserialize;
use std::time::Duration;
use tracing::error;

pub struct MqttClient {
    pub client: AsyncClient,
}

impl MqttClient {
    pub async fn new() -> Result<Self> {
        let create_opts = CreateOptionsBuilder::new()
            .server_uri(&CONFIG.mqtt.broker)
            .client_id(&CONFIG.mqtt.client)
            .finalize();

        let mqtt_client = AsyncClient::new(create_opts).unwrap_or_else(|err| {
            panic!("Error creating the MQTT client: {:?}", err);
        });

        let conn_opts = ConnectOptionsBuilder::new()
            .keep_alive_interval(Duration::from_secs(20))
            .clean_session(true)
            .finalize();

        tracing::info!("Starting MQTT connection");

        if let Err(e) = mqtt_client.connect(conn_opts).await {
            error!("Unable to connect to MQTT broker: {:?}", e);
            return Err(anyhow!("Unable to connect to MQTT broker: {:?}", e));
        }

        tracing::info!("Connected to MQTT broker!");

        Ok(MqttClient {
            client: mqtt_client,
        })
    }
}
