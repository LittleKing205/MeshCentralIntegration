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

NODE_ID_IDENTIFIER_PREFIX = "node_id:"

SIGNAL_CREATE_BINARY_SENSOR = "meshcentral_create_binary_sensor"
SIGNAL_UPDATE_BINARY_SENSOR = "meshcentral_update_binary_sensor"
SIGNAL_REMOVE_BINARY_SENSOR = "meshcentral_remove_binary_sensor"
SIGNAL_CREATE_BATTERY_SENSOR = "meshcentral_create_battery_sensor"
SIGNAL_UPDATE_BATTERY_SENSOR = "meshcentral_update_battery_sensor"
SIGNAL_REMOVE_BATTERY_SENSOR = "meshcentral_remove_battery_sensor"

# Node info sensors (Last Boot, Users Count, IP)
SIGNAL_CREATE_LAST_BOOT_SENSOR = "meshcentral_create_last_boot_sensor"
SIGNAL_UPDATE_LAST_BOOT_SENSOR = "meshcentral_update_last_boot_sensor"
SIGNAL_REMOVE_LAST_BOOT_SENSOR = "meshcentral_remove_last_boot_sensor"
SIGNAL_CREATE_LOGGED_IN_USERS_SENSOR = "meshcentral_create_logged_in_users_sensor"
SIGNAL_UPDATE_LOGGED_IN_USERS_SENSOR = "meshcentral_update_logged_in_users_sensor"
SIGNAL_REMOVE_LOGGED_IN_USERS_SENSOR = "meshcentral_remove_logged_in_users_sensor"
SIGNAL_CREATE_IP_SENSOR = "meshcentral_create_ip_sensor"
SIGNAL_UPDATE_IP_SENSOR = "meshcentral_update_ip_sensor"
SIGNAL_REMOVE_IP_SENSOR = "meshcentral_remove_ip_sensor"

# Node security binary sensors (Battery Charging, WSC, Defender)
SIGNAL_CREATE_BATTERY_CHARGING_BINARY_SENSOR = "meshcentral_create_battery_charging_binary_sensor"
SIGNAL_UPDATE_BATTERY_CHARGING_BINARY_SENSOR = "meshcentral_update_battery_charging_binary_sensor"
SIGNAL_REMOVE_BATTERY_CHARGING_BINARY_SENSOR = "meshcentral_remove_battery_charging_binary_sensor"
SIGNAL_CREATE_WSC_BINARY_SENSORS = "meshcentral_create_wsc_binary_sensors"
SIGNAL_UPDATE_WSC_BINARY_SENSORS = "meshcentral_update_wsc_binary_sensors"
SIGNAL_REMOVE_WSC_BINARY_SENSORS = "meshcentral_remove_wsc_binary_sensors"
SIGNAL_CREATE_DEFENDER_RTP_BINARY_SENSOR = "meshcentral_create_defender_rtp_binary_sensor"
SIGNAL_UPDATE_DEFENDER_RTP_BINARY_SENSOR = "meshcentral_update_defender_rtp_binary_sensor"
SIGNAL_REMOVE_DEFENDER_RTP_BINARY_SENSOR = "meshcentral_remove_defender_rtp_binary_sensor"
