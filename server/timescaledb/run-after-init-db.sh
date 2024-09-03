#!/bin/bash

set -e


PGPASSWORD=${POSTGRES_PASSWORD} psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER bridge WITH PASSWORD '${BRIDGE_PASSWD}';
    CREATE USER grafana WITH PASSWORD '${GRAFANA_PASSWD}';
    CREATE USER api WITH PASSWORD '${API_PASSWD}';

    --- Create write-only user for MQTT Bridge ---
    GRANT CONNECT ON DATABASE scooter_data TO bridge;
    GRANT USAGE ON SCHEMA public TO bridge;
    GRANT INSERT ON general_info TO bridge;
    GRANT INSERT ON battery_info TO bridge;
    GRANT INSERT ON location_info TO bridge;

    --- Create read-only user for Grafana ---
    GRANT CONNECT ON DATABASE scooter_data TO grafana;
    GRANT USAGE ON SCHEMA public TO grafana;
    GRANT SELECT ON general_info TO grafana;
    GRANT SELECT ON battery_info TO grafana;
    GRANT SELECT ON location_info TO grafana;

    --- Create read-only user for API ---
    GRANT CONNECT ON DATABASE scooter_data TO api;
    GRANT USAGE ON SCHEMA public TO api;
    GRANT SELECT ON general_info TO api;
    GRANT SELECT ON battery_info TO api;
    GRANT SELECT ON location_info TO api;

EOSQL
