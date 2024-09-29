# FastAPI server

This folder contains the FastAPI server, which integrates [FastAPI](https://fastapi.tiangolo.com/) and [SQLAlchemy](https://www.sqlalchemy.org/). The server serves two primary purposes:

1. **Data Access:** Provides an additional method to access data(battery, location and general info), enabling integrations with services like [Home Assistant](https://www.home-assistant.io/).

2. **Relay Control:** Allows control of the scooter's relay through the `set_power` method.

## ⚙️ Installation

Before running the server, make sure you fill in all necessary parameters in the [config.toml](./config.toml) file.
This file contains critical configuration details such as MQTT broker and database connection settings.

The [Docker Compose file](./../server-compose.yaml) automates the building and starting of the API server. However, if you prefer to handle it manually, you can use the following commands:

```bash
docker build -t localhost/scooter_api .
docker run --name scooter_api -p 80:80 -v ./config.toml:/app/config.toml:ro localhost/scooter_api
```
This will build and run the FastAPI server.

## 🚀 Features

- **Interactive OpenAPI Documentation:** After launching the container, visit `localhost/docs` to explore and test all available methods via the interactive API documentation.

- **Bruno API Client Integration:**
    - The API was tested using the [Bruno API Client](https://github.com/usebruno/bruno). To run the tests:
        1. Open the [bruno-test folder](./bruno-test) in the Bruno client.
        2. Set the `host` environment variable (to `localhost` if running locally)
        3. Start testing the API methods directly from Bruno!

    - 1. Provide with an aditional method of consuming the data (per example creating an integration with [Home Assistant](https://www.home-assistant.io/))(Battery Data, Location Data, General Data)
    - 2. Been able to control the ralay of the scooter (using the `set_power` method).

## 🚨 Security Note 🚨

This API was built as a prototype and **does not currently include any security features or authentication mechanisms**. **It should not be exposed to the internet in its current state**. Doing so would be a significant security risk.

### Recommendations for securing the API:

1. Implement native authentication and authorization in FastAPI.

2. Use an [API Gateway](https://github.com/Kong/kong) to add security layers such as rate limiting, token validation, etc.

In the future I may secure the API. For now, the safest approach is to use a VPN, ensuring that the API is only accessible to trusted clients.

## ⚠️ Concurrency Issue

The current implementation uses a global variable `mqtt_response` to store the relay state between API calls. This approach may cause concurrency issues under certain conditions, especially if multiple clients interact with the API simultaneously.

However, given that this API is primarily designed for **single-user access**, it's unlikely you'll encounter this issue during regular use (I did not experience any issues during real-world testing).

That said, this is a known limitation, and **improving the handling of state to avoid concurrency problems** is an area for future development.
