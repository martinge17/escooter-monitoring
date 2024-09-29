# Grafana

This folder contains the Grafana configuration files.

## ⚙️ Configuration and Installation

- By default, Grafana uses **GitHub authentication**. To switch to local authentication, edit the [grafana.ini](./grafana.ini) file:
```
[auth]
disable_login = false
disable_login_form = false

[auth.basic]
enabled = true

# Also, comment out the github configuration 
```

- Before running the service, **make sure you fill in the required parameters in the [grafana.env](./grafana.env) file**.
This file contains important details like Github tokens for authentication and the database connection settings.

### Dashboard and Datasources Configuration

**⚠️ Important:** You need to update the API endpoint (used to obtain the relay status) used in the dashboard to reflect your server's API.

- Replace all instances of `ubuntu-4gb-fsn1-1` with your actual server name in the [dashboard file](./dashboards/martinete_08.json). This is used by Grafana (actually is your browser that does the petition) when you click on the relay button to send the command to the Raspberry.

- If you change the container name of the API in the Docker Compose file, replace all `http://scooter_api` entries in the dashboard with the new endpoint.


### Provisioning

Grafana automatically provisions the dashboard and datasources when the container starts, which makes them [immutable in the WebUI](https://grafana.com/docs/grafana/latest/administration/provisioning/#dashboards). If you make changes in the WebUI, they won’t persist after a refresh.

To persist changes:
- Click the **Save** button in Grafana.
- Copy the JSON configuration.
- Paste it into the [dashboard file](./dashboards/martinete_08.json).

Do the same to change the `datasources` config, usint the [datasources config file](./datasources/datasource.yaml).

### GitHub Authentication (Optional)

If you decide to use [Github authentication](https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-authentication/github/), follow these steps:

1. Create a new [Github application](https://github.com/settings/applications/new)

2. Set the callback URL to `http://<my_grafana_server_name_or_ip>:<grafana_server_port>/login/github`.

    Ensure that the callback URL is the complete HTTP address that you use to access Grafana via your browser, but with the appended path of `/login/github`.

3. Finish by clicking Register application.

4. Fill in the `GH_ID` and `GH_SECRET` values on [grafana.env](grafana.env) with the client ID and secret. Also, add your Github username to `GH_ADMIN_USERNAME`, it will be the only user allowed to login into the Grafana instance.

