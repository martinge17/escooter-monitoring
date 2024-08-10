--- TODO: END !!!!!!!!!!!! This are the basic queries, later create more advanced representations.

--- Live speed (temporal independent)

SELECT speed_kmh FROM general_info WHERE time >= NOW() - INTERVAL '10 seconds' ORDER BY time DESC LIMIT 1

--- Speed Hist

SELECT time,speed_kmh from general_info WHERE $__timeFilter(time)

--- Current trip distance

SELECT trip_distance_m FROM general_info WHERE time >= NOW() - INTERVAL '10 seconds' ORDER BY time DESC LIMIT 1

--- Current Uptime

SELECT uptime_sec FROM general_info WHERE time >= NOW() - INTERVAL '10 seconds' ORDER BY time DESC LIMIT 1

-- Odometer

SELECT total_distance_m FROM general_info ORDER BY time DESC LIMIT 1

-- Esti distance left

SELECT est_distance_left_km FROM general_info ORDER BY time DESC LIMIT 1





----------- BATTERY ----------

-- Latest battery capacity

SELECT capacity FROM battery_info ORDER BY time DESC LIMIT 1

-- Latest battery percent

SELECT capacity FROM battery_info ORDER BY time DESC LIMIT 1

-- Battery Histo
SELECT time,percent from battery_info WHERE $__timeFilter(time)


---- LOCATION -----

SELECT time,ST_X(ST_AsEWKT(location)) AS longitude,
       ST_Y(ST_AsEWKT(location)) AS latitude
FROM location_info
WHERE (ST_X(ST_AsEWKT(location)) <> 0) AND (ST_Y(ST_AsEWKT(location)) <> 0)
