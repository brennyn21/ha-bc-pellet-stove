"""Constants for the BC Pellet Stove integration."""

DOMAIN = "bc_pellet_stove"

CONF_NAME = "name"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_DEVICE_ID = "device_id"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_NAME = "Pellet Stove"
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = 10

MODES = ["manual", "temp", "thermostat", "weekly"]

MODE_TO_ENDPOINT = {
    "manual": "/mode/manual",
    "temp": "/mode/temp",
    "thermostat": "/mode/thermostat",
    "weekly": "/mode/weekly",
}

TEMP_RANGE_F = (50, 85)
TEMP_RANGE_C = (10, 29)
BAND_RANGE = (0, 40)
