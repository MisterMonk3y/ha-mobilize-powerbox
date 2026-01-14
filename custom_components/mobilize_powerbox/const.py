"""Constantes pour l'intégration Mobilize PowerBox."""

# Domaine de l'intégration
DOMAIN = "mobilize_powerbox"

# Nom de l'intégration
INTEGRATION_NAME = "Mobilize PowerBox"
INTEGRATION_MANUFACTURER = "Mobilize"
INTEGRATION_MODEL = "PowerBox"

# Configuration
CONF_VERIFY_SSL = "verify_ssl"

# Valeurs par défaut
DEFAULT_NAME = "PowerBox"
DEFAULT_USERNAME = "installer"
DEFAULT_VERIFY_SSL = False
DEFAULT_SCAN_INTERVAL_REALTIME = 10  # secondes - mesures temps réel
DEFAULT_SCAN_INTERVAL_CONFIG = 300  # secondes (5 min) - configuration

# Endpoints API
ENDPOINT_AUTH = "auth"
ENDPOINT_METERS = "meters"
ENDPOINT_CONFIGS = "configs"
ENDPOINT_CONFIGS_MODULES = "configs/modules"
ENDPOINT_TOKENS = "tokens"

# Clés de données
DATA_COORDINATOR = "coordinator"
DATA_DEVICE_INFO = "device_info"
DATA_UNDO_UPDATE_LISTENER = "undo_update_listener"

# Attributs des capteurs
ATTR_LAST_UPDATE = "last_update"
ATTR_SOURCE = "source"
ATTR_METER_ID = "meter_id"

# IDs des compteurs (meters)
METER_VIRTUAL = 0  # Mesures en temps réel de la charge en cours
METER_POWER_BOARD = 1  # Énergie totale de la borne
METER_TIC_LINKY = 2  # Téléinformation Client (Linky)

# Noms des modules de configuration
MODULE_CHARGE_POINT = "ChargePoint"
MODULE_COUNTRY = "Country"
MODULE_INSTALLATION = "Installation"
MODULE_DYNAMIC_LOAD = "DynamicLoad"
MODULE_HOUSEHOLD = "Household"

# Configuration des paramètres
PARAM_MAX_CURRENT = "MaxCurrent"
PARAM_HOUSEHOLD_POWER_LIMIT = "HouseholdPowerLimit"
PARAM_DYNAMIC_LOAD_MANAGEMENT_MODE = "DynamicLoadManagementMode"
PARAM_CHARGER_MODE = "ChargerMode"
PARAM_COUNTRY_CODE = "CountryCode"
PARAM_INSTALLATION_TYPE = "InstallationType"

# Modes de charge
CHARGE_MODE_UNLOCKED = "Unlocked"
CHARGE_MODE_ALWAYS = "Always"

# Modes de gestion dynamique de charge
DYNAMIC_LOAD_MODE_DISABLED = "Disabled"
DYNAMIC_LOAD_MODE_POWER = "Power"
DYNAMIC_LOAD_MODE_CURRENT = "Current"

# Types d'installation
INSTALLATION_TYPE_SINGLE = "Single"
INSTALLATION_TYPE_THREE = "Three"

# Unités de mesure personnalisées
UNIT_VOLT_AMPERE = "VA"  # Volt-Ampère (puissance apparente)

# Icônes
ICON_CURRENT = "mdi:current-ac"
ICON_VOLTAGE = "mdi:lightning-bolt"
ICON_POWER = "mdi:flash"
ICON_ENERGY = "mdi:lightning-bolt-circle"
ICON_ENERGY_TOTAL = "mdi:counter"
ICON_CHARGER = "mdi:ev-station"
ICON_CONFIG = "mdi:cog"
ICON_COUNTRY = "mdi:earth"
ICON_INSTALLATION = "mdi:home-lightning-bolt"

# Noms des capteurs (pour les traductions)
SENSOR_CURRENT = "current"
SENSOR_VOLTAGE = "voltage"
SENSOR_POWER = "power"
SENSOR_SESSION_ENERGY = "session_energy"
SENSOR_TOTAL_ENERGY = "total_energy"
SENSOR_TIC_CURRENT = "tic_current"
SENSOR_TIC_POWER = "tic_power"
SENSOR_MAX_CURRENT = "max_current"
SENSOR_HOUSEHOLD_POWER_LIMIT = "household_power_limit"
SENSOR_DYNAMIC_LOAD_MODE = "dynamic_load_mode"
SENSOR_CHARGER_MODE = "charger_mode"
SENSOR_COUNTRY = "country"
SENSOR_INSTALLATION_TYPE = "installation_type"

# Messages d'erreur
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_INVALID_AUTH = "invalid_auth"
ERROR_TIMEOUT = "timeout"
ERROR_UNKNOWN = "unknown"

# Timeouts (en secondes)
TIMEOUT_AUTH = 10
TIMEOUT_API = 10

# Retry
MAX_RETRIES = 3
RETRY_DELAY = 5  # secondes
