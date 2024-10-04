# Server configuration

This directory contains the server components of the e-scooter monitoring platform. The platform is designed to be deployed on a cloud VPS or a local machine using Docker Compose for containerization and orchestration.

By default, the setup uses Docker Volumes (as defined in the Docker Compose file) to store persistent data, such as database records and Grafana configurations. Feel free to customize the Docker Compose file if you prefer to bind local directories to store data or adjust configurations to suit your specific needs.

Each component folder contains a README with more detailed information:

- [Ansible README](./ansible/README.md)
- [API README](./api/README.md)
- [Grafana README](./grafana/README.md)
- [MQTT Bridge README](./mqtt-postgresql-bridge/README.md)
- [TimescaleDB README](./timescaledb/README.md)

## ⚙️ Configuration files overview

The environment and configuration files containing usernames, credentials, and other sensitive information are located in the following paths. **It is critical to modify the default values before deploying to a live environment.**

- The environment files containing the usernames and credentials are located in the following paths, **you should modify the default options**:
    - [grafana.env](./grafana/grafana.env): Contains database credentials for Grafana, GitHub tokens for authentication, and server name settings.
    - [mosquitto.conf](./broker/mosquitto.conf): Mosquitto MQTT broker configuration file.
    - [db.env](./timescaledb/db.env): Contains the usernames and passwords for the different database users (grafana, fastapi, mqtt-bridge).
    - [mqtt-bridge config](./mqtt-postgresql-bridge/config.toml): Contains usernames and passwords for various database users (Grafana, FastAPI, MQTT bridge).
    - [api-config](./api/config.toml): FastAPI server configuration for MQTT broker and database connection parameters.

## 🚨 Security Note 🚨

The default configuration files include **demo credentials** intended for local testing only. **If deploying to a publicly accessible server, it is crucial to:**

1. **Replace the default credentials with strong, secure values.**
2. **Secure Mosquitto with at least a username and password.**

Failing to do so will leave your server vulnerable to attacks, especially if it is exposed to the internet. Your server could be compromised within moments if these precautions are not taken. There are numerous bots that constantly scan the internet for open MQTT brokers and misconfigured servers. Your server could end up in search engines like [Censys](https://search.censys.io/) or [Shodan](https://www.shodan.io/), making it an easy target.

Refer to [this guide](https://github.com/sukesh-ak/setup-mosquitto-with-docker) as an example on how to configure Mosquitto security.


**Recommendation:** For an added layer of security, consider using [Tailscale VPN](https://tailscale.com/) or a similar VPN solution to restrict access to your server. This demo deployment used Tailscale to ensure that only authorized devices could connect, with no open ports exposed to the internet 

## 🚀 Deployment Options

You can deploy this project using one of two methods:

- **Ansible** Playbook (Recommended for fresh setups).
- Raw **Docker Compose** (Manual setup).

### Ansible Automation (Recommended for fresh setups).

This method sets up the entire server on a Hetzner VPS (you can use any other cloud provider or fresh Linux machine) with just a root account. Ansible automates the new user creation, adding an authorized ssh key, installation of Docker, Docker Compose, it copies the repository files and starts the Compose. It is a great option for quick and reliable deployment.

Modify the variables and inventory to your needs.

### Raw Docker Compose (Manual)

If you already have a server with Docker installed, you can just copy the server folder, modify the env and configuration files as necessary and start the Compose with:

```bash
docker compose -f server-compose.yaml up
```