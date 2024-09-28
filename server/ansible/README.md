# Ansible Server Setup Playbook

This Ansible playbook automates the server setup by performing the following tasks:

- Creating a new user for the deployment.
- Adding an SSH key to the created user for secure access.
- Installing Docker and Docker Compose.
- Copying necessary files to the server.
- Deploying the E-Scooter Monitoring Stack via Docker Compose.

## How to Run the Playbook

1. **Prepare the Inventory and Variables:**
   - Fill in the required server details in the [inventory](inventory) file.
   - Update the necessary values in [vars.yaml](vars/vars.yaml) with the server-specific configuration.

2. **Configure Environment Files:**
   Ensure that the following configuration files are filled out:
   - [API Configuration](../api/config.toml)
   - [Grafana Environment](../grafana/grafana.env)
   - [MQTT-PostgreSQL Bridge Configuration](../mqtt-postgresql-bridge/config.toml)
   - [TimescaleDB Configuration](../timescaledb/db.env)

3. **Run the Playbook:**
   Execute the playbook using the following command:

   ```bash
   ansible-playbook -i inventory playbook.yaml
   ```