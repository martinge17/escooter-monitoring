CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;



--- Create general info table ---
CREATE TABLE general_info (
    time timestamptz NOT NULL, --- Timestamp
    speed_kmh DECIMAL(4,2) NOT NULL CHECK (speed_kmh >= 0), --- Speed km/h max: 99.99
    trip_distance_m INTEGER NOT NULL CHECK (trip_distance_m >= 0), --- Current trip distance (meters)
    uptime_sec INTEGER NOT NULL CHECK (uptime_sec >= 0), --- Current uptime (seconds)
    total_distance_m INTEGER NOT NULL CHECK (total_distance_m >= 0), --- Lifetime distance (meters)
    est_distance_left_km DECIMAL(5,2) NOT NULL CHECK (est_distance_left_km >= 0),--- Estimated trip distance (kilometers)
    frame_temp DECIMAL(4,2) NOT NULL CHECK (frame_temp >= 0) -- Frame temperature in celsius
);

SELECT create_hypertable('general_info',by_range('time'));

-- Add comments to general_info columns
COMMENT ON TABLE general_info IS 'Table storing scooter metrics';
COMMENT ON COLUMN general_info.speed_kmh IS 'Speed of the scooter in km/h';
COMMENT ON COLUMN general_info.total_distance_m IS 'Total distance covered by the scooter in m';
COMMENT ON COLUMN general_info.trip_distance_m IS 'Distance covered during the current trip in m';
COMMENT ON COLUMN general_info.uptime_sec IS 'Uptime of the scooter in seconds';
COMMENT ON COLUMN general_info.est_distance_left_km IS 'Estimated distance left in km';
COMMENT ON COLUMN general_info.frame_temp IS 'Frame temperature in Celsius';



--- Create battery info table ---
CREATE TABLE battery_info (
    time timestamptz NOT NULL, --- Timestamp
    capacity SMALLINT NOT NULL CHECK (capacity >=  0), --- Remaining mAh capacity
    percent SMALLINT NOT NULL CONSTRAINT valid_percentage CHECK (percent <=  100),
    voltage DECIMAL(4,2) NOT NULL CHECK (voltage >= 0), --- Voltage for all cells unified (Volts)
    current DECIMAL(5,3) NOT NULL, --- in Amps current going through battery --BEFORE 5,4
    power DECIMAL(5,2) GENERATED ALWAYS AS (voltage * current) STORED, --- Calculated power delivered by battery (Watts)
    temp1 SMALLINT NOT NULL CHECK (temp1 >=  0), --- TODO: PROVISIONAL
    temp2 SMALLINT NOT NULL CHECK (temp2 >=  0) --- TODO: PROVISIONAL
    --- TODO: METER JSON CON VOLTS DAS CELDAS??????????
);

SELECT create_hypertable('battery_info',by_range('time'));

-- Add comments to battery_info columns
COMMENT ON TABLE battery_info IS 'Table storing battery metrics';
COMMENT ON COLUMN battery_info.capacity IS 'Battery capacity in mAh';
COMMENT ON COLUMN battery_info.percent IS 'Battery charge percentage';
COMMENT ON COLUMN battery_info.current IS 'current going through battery in Amps';
COMMENT ON COLUMN battery_info.voltage IS 'Battery voltage in Volts';
COMMENT ON COLUMN battery_info.power IS 'Calculated power delivered by battery Watts';
COMMENT ON COLUMN battery_info.temp1 IS 'Temperature sensor 1 reading in Celsius';
COMMENT ON COLUMN battery_info.temp2 IS 'Temperature sensor 2 reading in Celsius';

--- Create location info table ---
CREATE TABLE location_info (
    time timestamptz NOT NULL, --- Timestamp
    location geography(POINT,4326) NOT NULL, --- LON/LAT in PostGIS format
    altitude DECIMAL(6,2) NOT NULL, --Elevation above sea level in meters
    gps_speed DECIMAL(4,2) NOT NULL CHECK (gps_speed >= 0) -- GPS Measured Speed KM/h
);

SELECT create_hypertable('location_info',by_range('time'));

-- Add comments to location_info columns
COMMENT ON TABLE location_info IS 'Table storing GPS metrics';
COMMENT ON COLUMN location_info.location IS 'Longitude Latitude in DD';
COMMENT ON COLUMN location_info.altitude IS 'Altitude in meters';
COMMENT ON COLUMN location_info.gps_speed IS 'GPS speed in km/h';


--- Create read-only user for Grafana ---
CREATE USER grafana WITH PASSWORD 'changeme'; --TODO!!!!! NOTE THIS ON README
GRANT CONNECT ON DATABASE scooter_data TO grafana;
GRANT USAGE ON SCHEMA public TO grafana;
GRANT SELECT ON general_info TO grafana;
GRANT SELECT ON battery_info TO grafana;
GRANT SELECT ON location_info TO grafana;
