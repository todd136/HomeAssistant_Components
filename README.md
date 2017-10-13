# HomeAssistant_Components
components for homeassistant

configuration variables
-----------------------
```
- api_key (Required): The API key for Weather China. See below for details.
- area (Required): The location code for the observe data to request from Weather China. See below for details.
- monitored_conditions  array (Required): Conditions to display in the frontend. The following conditions can be monitored.
      - observeTime: 	 Observation time
      - weather:         Current weather (Not supplied by weather china yet in observation data)
      - temperature:     Current temperature in Celsius
      - windSpeed:       Current wind speed in level, where the wind is coming from in degrees
      - windDirection:   Current wind direction, with nature text description
      - humidity:        Current humidity in %
      - rain_trace:      Current rain today in mm
      - pressure:        Current sea-level air pressure in millibars.
```
All the conditions listed above will be updated every 10 minutes.

full configuration as below
---------------------------
```
  - platform: weather
    api_key:   observe api_key for weather china
    area:      location code of china from weather china
    monitored_conditions:
      - observationTime
      - weather
      - temperature
      - windSpeed
      - windDirection
      - humidity
      - rain_trace
      - pressure
```

method to obtain a api_key and the area code
--------------------------
Obtain a Weather China API key [here].

[here]: http://www.weatherdt.com/productsimple.html