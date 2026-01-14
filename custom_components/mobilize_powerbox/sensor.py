"""Capteurs pour Mobilize PowerBox."""
import logging
from datetime import timedelta
import requests

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfEnergy,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

# Intervalles de mise à jour selon les recommandations HA
SCAN_INTERVAL_REALTIME = timedelta(seconds=10)  # Mesures temps réel (courant, tension, puissance)
SCAN_INTERVAL_CONFIG = timedelta(minutes=5)  # Configuration (changements rares)


async def async_setup_entry(hass, entry, async_add_entities):
    """Configuration des capteurs depuis une config entry."""
    
    # Récupérer les données depuis hass.data
    domain_data = hass.data["mobilize_powerbox"][entry.entry_id]
    coordinator_realtime = domain_data["coordinator_realtime"]
    coordinator_config = domain_data["coordinator_config"]
    device_info = domain_data["device_info"]
    
    sensors = [
        # Mesures en temps réel (10s) - compteur virtuel - charge en cours
        PowerBoxCurrentSensor(coordinator_realtime, device_info),
        PowerBoxVoltageSensor(coordinator_realtime, device_info),
        PowerBoxPowerSensor(coordinator_realtime, device_info),
        PowerBoxSessionEnergySensor(coordinator_realtime, device_info),
        
        # Énergie totale de la borne (10s)
        PowerBoxTotalEnergySensor(coordinator_realtime, device_info),
        
        # Téléinformation Client (TiC) (10s)
        PowerBoxTicCurrentSensor(coordinator_realtime, device_info),
        PowerBoxTicPowerSensor(coordinator_realtime, device_info),
        
        # Configuration (5 minutes) - changements rares
        PowerBoxMaxCurrentSensor(coordinator_config, device_info),
        PowerBoxHouseholdPowerLimitSensor(coordinator_config, device_info),
        PowerBoxDynamicLoadModeSensor(coordinator_config, device_info),
        PowerBoxChargerModeSensor(coordinator_config, device_info),
        PowerBoxCountrySensor(coordinator_config, device_info),
        PowerBoxInstallationTypeSensor(coordinator_config, device_info),
    ]
    
    async_add_entities(sensors, True)


class PowerBoxAPIClient:
    """Client API partagé pour éviter les duplications de tokens."""

    def __init__(self, base_url, username, password, verify_ssl):
        """Initialisation du client API."""
        self.base_url = base_url
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self._token = None

    def _get_auth_token(self):
        """Récupère le token d'authentification."""
        url = f"{self.base_url}/auth"
        payload = {"username": self.username, "password": self.password}
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                headers=headers, 
                verify=self.verify_ssl,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("id_token")
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 503:
                _LOGGER.warning("PowerBox temporairement indisponible (503), réessai plus tard")
                raise UpdateFailed("PowerBox temporairement indisponible") from err
            raise
        except requests.exceptions.RequestException as err:
            _LOGGER.error(f"Erreur lors de l'authentification: {err}")
            raise UpdateFailed(f"Erreur d'authentification: {err}") from err

    def fetch_data(self, endpoint):
        """Récupère les données depuis un endpoint."""
        if not self._token:
            self._token = self._get_auth_token()
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self._token}",
        }
        
        try:
            response = requests.get(url, headers=headers, verify=self.verify_ssl, timeout=10)
            if response.status_code == 401:
                # Token expiré, réessayer avec un nouveau token
                _LOGGER.debug("Token expiré, récupération d'un nouveau token")
                self._token = self._get_auth_token()
                headers["authorization"] = f"Bearer {self._token}"
                response = requests.get(url, headers=headers, verify=self.verify_ssl, timeout=10)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 503:
                _LOGGER.warning(f"PowerBox temporairement indisponible pour {endpoint} (503)")
                raise UpdateFailed("PowerBox temporairement indisponible") from err
            _LOGGER.error(f"Erreur HTTP lors de la récupération de {endpoint}: {err}")
            raise UpdateFailed(f"Erreur HTTP: {err}") from err
        except requests.exceptions.RequestException as err:
            _LOGGER.error(f"Erreur lors de la récupération de {endpoint}: {err}")
            raise UpdateFailed(f"Erreur de connexion: {err}") from err


class PowerBoxRealtimeCoordinator(DataUpdateCoordinator):
    """Coordinateur pour les mesures temps réel (10s)."""

    def __init__(self, hass, api_client):
        """Initialisation du coordinateur temps réel."""
        super().__init__(
            hass,
            _LOGGER,
            name="Mobilize PowerBox Realtime",
            update_interval=SCAN_INTERVAL_REALTIME,
        )
        self.api_client = api_client

    async def _async_update_data(self):
        """Récupère les mesures temps réel."""
        try:
            meters = await self.hass.async_add_executor_job(
                self.api_client.fetch_data, "meters"
            )
            
            # Parser les compteurs pour un accès plus facile
            meters_parsed = {}
            for meter in meters:
                model = meter.get("Model", "")
                values_dict = {}
                for value in meter.get("Values", []):
                    values_dict[value["Name"]] = {
                        "value": value["Value"],
                        "timestamp": value.get("Timestamp", 0)
                    }
                meters_parsed[model] = {
                    "connected": meter.get("Connected") == "true",
                    "id": meter.get("ID"),
                    "manufacturer": meter.get("Manufacturer"),
                    "serial": meter.get("Serial"),
                    "values": values_dict
                }
            
            return {"meters_parsed": meters_parsed}
            
        except Exception as err:
            raise UpdateFailed(f"Erreur lors de la mise à jour des mesures: {err}")


class PowerBoxConfigCoordinator(DataUpdateCoordinator):
    """Coordinateur pour la configuration (5 minutes)."""

    def __init__(self, hass, api_client):
        """Initialisation du coordinateur de configuration."""
        super().__init__(
            hass,
            _LOGGER,
            name="Mobilize PowerBox Config",
            update_interval=SCAN_INTERVAL_CONFIG,
        )
        self.api_client = api_client

    async def _async_update_data(self):
        """Récupère la configuration."""
        try:
            configs_list = await self.hass.async_add_executor_job(
                self.api_client.fetch_data, "configs"
            )
            
            # Transformer la liste en dictionnaire
            configs = {}
            for config in configs_list:
                module = config.get("module_name", "")
                name = config.get("config_name", "")
                key = f"{module}.{name}"
                configs[key] = config
            
            return {"configs": configs}
            
        except Exception as err:
            raise UpdateFailed(f"Erreur lors de la mise à jour de la configuration: {err}")


class PowerBoxSensorBase(CoordinatorEntity, SensorEntity):
    """Classe de base pour les capteurs PowerBox."""

    def __init__(self, coordinator, device_info, sensor_type, name, unit=None, device_class=None, state_class=None):
        """Initialisation du capteur."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = f"PowerBox {name}"
        self._attr_unique_id = f"powerbox_{sensor_type}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_device_info = device_info

    @property
    def available(self):
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success and self.coordinator.data is not None


# ============================================================================
# CAPTEURS TEMPS RÉEL (depuis /meters)
# ============================================================================

class PowerBoxCurrentSensor(PowerBoxSensorBase):
    """Capteur de courant de charge actuel."""

    def __init__(self, coordinator, device_info):
        """Initialisation."""
        super().__init__(
            coordinator,
            device_info,
            "current",
            "Courant",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
        )

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if self.coordinator.data and "meters_parsed" in self.coordinator.data:
            meter = self.coordinator.data["meters_parsed"].get("EVPLCCom-Virtual-Meter", {})
            if meter.get("connected"):
                current_data = meter.get("values", {}).get("Current_mA")
                if current_data:
                    return round(current_data["value"] / 1000, 2)  # mA vers A
        return 0


class PowerBoxVoltageSensor(PowerBoxSensorBase):
    """Capteur de tension."""

    def __init__(self, coordinator, device_info):
        """Initialisation."""
        super().__init__(
            coordinator,
            device_info,
            "voltage",
            "Tension",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
        )

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if self.coordinator.data and "meters_parsed" in self.coordinator.data:
            meter = self.coordinator.data["meters_parsed"].get("EVPLCCom-Virtual-Meter", {})
            if meter.get("connected"):
                voltage_data = meter.get("values", {}).get("Voltage_mV")
                if voltage_data:
                    return round(voltage_data["value"] / 1000, 1)  # mV vers V
        return None


class PowerBoxPowerSensor(PowerBoxSensorBase):
    """Capteur de puissance active."""

    def __init__(self, coordinator, device_info):
        """Initialisation."""
        super().__init__(
            coordinator,
            device_info,
            "power",
            "Puissance",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        )

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if self.coordinator.data and "meters_parsed" in self.coordinator.data:
            meter = self.coordinator.data["meters_parsed"].get("EVPLCCom-Virtual-Meter", {})
            if meter.get("connected"):
                power_data = meter.get("values", {}).get("ActivePower_W")
                if power_data:
                    return round(power_data["value"], 0)
        return 0


class PowerBoxSessionEnergySensor(PowerBoxSensorBase):
    """Capteur d'énergie de la session de charge en cours."""

    def __init__(self, coordinator, device_info):
        """Initialisation."""
        super().__init__(
            coordinator,
            device_info,
            "session_energy",
            "Énergie Session",
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        )

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if self.coordinator.data and "meters_parsed" in self.coordinator.data:
            meter = self.coordinator.data["meters_parsed"].get("EVPLCCom-Virtual-Meter", {})
            if meter.get("connected"):
                energy_data = meter.get("values", {}).get("SessionTotalEnergy_Ws")
                if energy_data:
                    # Ws vers kWh
                    return round(energy_data["value"] / 3600 / 1000, 2)
        return 0


class PowerBoxTotalEnergySensor(PowerBoxSensorBase):
    """Capteur d'énergie totale de la borne (depuis l'installation)."""

    def __init__(self, coordinator, device_info):
        """Initialisation."""
        super().__init__(
            coordinator,
            device_info,
            "total_energy",
            "Énergie Totale",
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        )

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if self.coordinator.data and "meters_parsed" in self.coordinator.data:
            meter = self.coordinator.data["meters_parsed"].get("Power Board Meter", {})
            if meter.get("connected"):
                energy_data = meter.get("values", {}).get("ActiveEnergy_Ws")
                if energy_data:
                    # Ws vers kWh
                    return round(energy_data["value"] / 3600 / 1000, 1)
        return None


class PowerBoxTicCurrentSensor(PowerBoxSensorBase):
    """Capteur de courant TiC (téléinformation client)."""

    def __init__(self, coordinator, device_info):
        """Initialisation."""
        super().__init__(
            coordinator,
            device_info,
            "tic_current",
            "Courant TiC",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
        )

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if self.coordinator.data and "meters_parsed" in self.coordinator.data:
            meter = self.coordinator.data["meters_parsed"].get("TiC", {})
            if meter.get("connected"):
                current_data = meter.get("values", {}).get("Current_PhaseA_mA")
                if current_data:
                    return round(current_data["value"] / 1000, 2)
        return None


class PowerBoxTicPowerSensor(PowerBoxSensorBase):
    """Capteur de puissance apparente TiC."""

    def __init__(self, coordinator, device_info):
        """Initialisation."""
        super().__init__(
            coordinator,
            device_info,
            "tic_power",
            "Puissance TiC",
            "VA",  # Volt-Ampère (puissance apparente)
            SensorDeviceClass.APPARENT_POWER,
            SensorStateClass.MEASUREMENT,
        )

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if self.coordinator.data and "meters_parsed" in self.coordinator.data:
            meter = self.coordinator.data["meters_parsed"].get("TiC", {})
            if meter.get("connected"):
                power_data = meter.get("values", {}).get("ApparentPower_VA")
                if power_data:
                    return round(power_data["value"], 0)
        return None


# ============================================================================
# CAPTEURS DE CONFIGURATION (depuis /configs)
# ============================================================================

class PowerBoxMaxCurrentSensor(PowerBoxSensorBase):
    """Capteur de courant maximum configuré."""

    def __init__(self, coordinator, device_info):
        """Initialisation."""
        super().__init__(
            coordinator,
            device_info,
            "max_current",
            "Courant Maximum",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
        )

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if self.coordinator.data and "configs" in self.coordinator.data:
            config = self.coordinator.data["configs"].get("ChargerApp.ACCharging.maxCurrent_mA")
            if config:
                max_current_ma = int(config.get("config_value", 0))
                return round(max_current_ma / 1000, 2)
        return None


class PowerBoxHouseholdPowerLimitSensor(PowerBoxSensorBase):
    """Capteur de limite de puissance du foyer."""

    def __init__(self, coordinator, device_info):
        """Initialisation."""
        super().__init__(
            coordinator,
            device_info,
            "household_power_limit",
            "Limite Puissance Foyer",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        )

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if self.coordinator.data and "configs" in self.coordinator.data:
            config = self.coordinator.data["configs"].get("ihal.household.PowerLimit_W")
            if config:
                return int(config.get("config_value", 0))
        return None


class PowerBoxDynamicLoadModeSensor(PowerBoxSensorBase):
    """Capteur du mode de gestion dynamique de charge."""

    def __init__(self, coordinator, device_info):
        """Initialisation."""
        super().__init__(
            coordinator,
            device_info,
            "dynamic_load_mode",
            "Mode Gestion Dynamique",
        )

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if self.coordinator.data and "configs" in self.coordinator.data:
            config = self.coordinator.data["configs"].get("DynamicLoadManager.CurrentSet")
            if config:
                return config.get("config_value", "unknown")
        return "unknown"

    @property
    def icon(self):
        """Retourne l'icône du capteur."""
        return "mdi:sync"


class PowerBoxChargerModeSensor(PowerBoxSensorBase):
    """Capteur du mode de charge."""

    def __init__(self, coordinator, device_info):
        """Initialisation."""
        super().__init__(
            coordinator,
            device_info,
            "charger_mode",
            "Mode de Charge",
        )

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if self.coordinator.data and "configs" in self.coordinator.data:
            config = self.coordinator.data["configs"].get("ChargerMode.CurrentSet")
            if config:
                return config.get("config_value", "unknown")
        return "unknown"

    @property
    def icon(self):
        """Retourne l'icône du capteur."""
        return "mdi:ev-station"


class PowerBoxCountrySensor(PowerBoxSensorBase):
    """Capteur du pays configuré."""

    def __init__(self, coordinator, device_info):
        """Initialisation."""
        super().__init__(
            coordinator,
            device_info,
            "country",
            "Pays",
        )

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if self.coordinator.data and "configs" in self.coordinator.data:
            config = self.coordinator.data["configs"].get("product.countryName")
            if config:
                return config.get("config_value", "unknown")
        return "unknown"

    @property
    def icon(self):
        """Retourne l'icône du capteur."""
        return "mdi:flag"


class PowerBoxInstallationTypeSensor(PowerBoxSensorBase):
    """Capteur du type d'installation."""

    def __init__(self, coordinator, device_info):
        """Initialisation."""
        super().__init__(
            coordinator,
            device_info,
            "installation_type",
            "Type d'Installation",
        )

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if self.coordinator.data and "configs" in self.coordinator.data:
            config = self.coordinator.data["configs"].get("product.installationType")
            if config:
                return config.get("config_value", "unknown")
        return "unknown"

    @property
    def icon(self):
        """Retourne l'icône du capteur."""
        return "mdi:home-lightning-bolt"
