--- TODO: END !!!!!!!!!!!! This are the basic queries, later create more advanced representations.

--- Live speed (temporal independent)

SELECT speed_kmh FROM general_info WHERE time >= NOW() - INTERVAL '10 seconds' ORDER BY time DESC LIMIT 1

--- Speed Hist

SELECT time,speed_kmh from general_info WHERE $__timeFilter(time)

--- Current trip distance

SELECT trip_distance_m FROM general_info WHERE time >= NOW() - INTERVAL '10 seconds' ORDER BY time DESC LIMIT 1

--- Current Uptime

SELECT uptime_sec FROM general_info WHERE time >= NOW() - INTERVAL '10 seconds' ORDER BY time DESC LIMIT 1

-- Odometer (total distance)

SELECT total_distance_m FROM general_info ORDER BY time DESC LIMIT 1

-- Esti distance left

SELECT est_distance_left_km FROM general_info ORDER BY time DESC LIMIT 1

-- Frame temperature

SELECT frame_temp FROM general_info WHERE time >= NOW() - INTERVAL '10 seconds' ORDER BY time DESC LIMIT 1

--- frame temp Hist

SELECT time,frame_temp from general_info WHERE $__timeFilter(time)

----------- BATTERY ----------

-- Latest battery capacity

SELECT capacity FROM battery_info ORDER BY time DESC LIMIT 1

--Battery capacity hist

SELECT time,capacity from battery_info WHERE $__timeFilter(time)

-- Latest battery percent

SELECT capacity FROM battery_info ORDER BY time DESC LIMIT 1

-- Battery Percent Histo
SELECT time,percent from battery_info WHERE $__timeFilter(time)

-- Live battery voltage

SELECT voltage FROM battery_info WHERE time >= NOW() - INTERVAL '10 seconds' ORDER BY time DESC LIMIT 1

-- Battery Voltage Histo
SELECT time,voltage from battery_info WHERE $__timeFilter(time)


-- Live battery current

SELECT current FROM battery_info WHERE time >= NOW() - INTERVAL '10 seconds' ORDER BY time DESC LIMIT 1

-- Battery Voltage Histo
SELECT time,current from battery_info WHERE $__timeFilter(time)


-- Live battery power output current

SELECT power FROM battery_info WHERE time >= NOW() - INTERVAL '10 seconds' ORDER BY time DESC LIMIT 1

-- Battery Power output Histo
SELECT time,power from battery_info WHERE $__timeFilter(time)

-- Live battery temp1

SELECT temp1 FROM battery_info WHERE time >= NOW() - INTERVAL '10 seconds' ORDER BY time DESC LIMIT 1

-- Battery temp1 Histo
SELECT time,temp1 from battery_info WHERE $__timeFilter(time)

-- Live battery temp2

SELECT temp2 FROM battery_info WHERE time >= NOW() - INTERVAL '10 seconds' ORDER BY time DESC LIMIT 1

-- Battery temp2 Histo
SELECT time,temp2 from battery_info WHERE $__timeFilter(time)

---- LOCATION -----

SELECT time,ST_X(ST_AsEWKT(location)) AS longitude,
       ST_Y(ST_AsEWKT(location)) AS latitude
FROM location_info
WHERE (ST_X(ST_AsEWKT(location)) <> 0) AND (ST_Y(ST_AsEWKT(location)) <> 0)

-- Live altitude

SELECT altitude FROM location_info WHERE time >= NOW() - INTERVAL '10 seconds' ORDER BY time DESC LIMIT 1

-- Altitude Histo
SELECT time,altitude from location_info WHERE $__timeFilter(time)

-- Live gps speed

SELECT gps_speed FROM location_info WHERE time >= NOW() - INTERVAL '10 seconds' ORDER BY time DESC LIMIT 1

-- gps_speed Histo
SELECT time,gps_speed from location_info WHERE $__timeFilter(time)
