# MQTT to Database Bridge

This folder contains the bridge that extracts the data from the MQTT messages and inserts it on the TimescaleDB database.

## ⚙️ Installation

Before running the bridge, make sure you fill in all necessary parameters in the [config.toml](./config.toml) file.
This file contains critical configuration details such as MQTT broker and database connection settings.

The [Docker Compose file](./../server-compose.yaml) automates the building and starting of the bridge client. However, if you prefer to handle it manually, you can use the following commands:

```bash
docker build -t localhost/mqtt_bridge .
docker run --name mqtt_bridge -v ./config.toml:/app/config.toml:ro localhost/mqtt_bridge
```
This will build and run the MQTT bridge.