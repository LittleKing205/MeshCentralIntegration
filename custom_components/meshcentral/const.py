DOMAIN = "meshcentral"

CONF_SSL = "ssl"
CONF_URL = "url"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

DEFAULT_SSL = True
DEFAULT_URL = "localhost:5222"
DEFAULT_USERNAME = "admin"
RECONNECT_DELAY_SECONDS = 5

PLATFORMS = ["binary_sensor", "sensor"]

DATA_CLIENT = "client"
DATA_REGISTERED_BATTERY_DEVICES = "registered_battery_devices"

SIGNAL_CREATE_BINARY_SENSOR = "meshcentral_create_binary_sensor"
SIGNAL_UPDATE_BINARY_SENSOR = "meshcentral_update_binary_sensor"
SIGNAL_CREATE_BATTERY_SENSOR = "meshcentral_create_battery_sensor"
SIGNAL_UPDATE_BATTERY_SENSOR = "meshcentral_update_battery_sensor"
