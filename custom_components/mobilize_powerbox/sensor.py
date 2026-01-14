"""Capteurs pour Mobilize PowerBox."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfEnergy,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import PowerBoxRealtimeCoordinator, PowerBoxConfigCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Configuration des capteurs depuis une config entry."""
    
    # Récupérer les coordinateurs depuis hass.data
    domain_data = hass.data[DOMAIN][entry.entry_id]
    coordinator_realtime: PowerBoxRealtimeCoordinator = domain_data["coordinator_realtime"]
    coordinator_config: PowerBoxConfigCoordinator = domain_data["coordinator_config"]
    device_info = domain_data["device_info"]
    
    # Créer les capteurs temps réel (10s)
    realtime_sensors = [
        PowerBoxCurrentSensor(coordinator_realtime, device_info),
        PowerBoxVoltageSensor(coordinator_realtime, device_info),
        PowerBoxPowerSensor(coordinator_realtime, device_info),
        PowerBoxSessionEnergySensor(coordinator_realtime, device_info),
        PowerBoxTotalEnergySensor(coordinator_realtime, device_info),
        PowerBoxTicCurrentSensor(coordinator_realtime, device_info),
        PowerBoxTicPowerSensor(coordinator_realtime, device_info),
    ]
    
    # Créer les capteurs de configuration (5min)
    config_sensors = [
        PowerBoxMaxCurrentSensor(coordinator_config, device_info),
        PowerBoxHouseholdPowerLimitSensor(coordinator_config, device_info),
        PowerBoxDynamicLoadModeSensor(coordinator_config, device_info),
        PowerBoxChargerModeSensor(coordinator_config, device_info),
        PowerBoxCountrySensor(coordinator_config, device_info),
        PowerBoxInstallationTypeSensor(coordinator_config, device_info),
    ]
    
    async_add_entities(realtime_sensors + config_sensors, True)


# ============================================================================
# CAPTEURS TEMPS RÉEL (depuis /meters) - Coordinateur 10s
# ============================================================================

class PowerBoxCurrentSensor(CoordinatorEntity, SensorEntity):
    """Capteur de courant de charge actuel."""

    def __init__(self, coordinator: PowerBoxRealtimeCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Courant"
        self._attr_unique_id = f"powerbox_current"
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_meter_value("EVPLCCom-Virtual-Meter", "Current_mA")
        if value is not None:
            self._attr_native_value = round(value / 1000, 2)  # mA vers A
        else:
            self._attr_native_value = 0
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxVoltageSensor(CoordinatorEntity, SensorEntity):
    """Capteur de tension."""

    def __init__(self, coordinator: PowerBoxRealtimeCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Tension"
        self._attr_unique_id = f"powerbox_voltage"
        self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
        self._attr_device_class = SensorDeviceClass.VOLTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_meter_value("EVPLCCom-Virtual-Meter", "Voltage_mV")
        if value is not None:
            self._attr_native_value = round(value / 1000, 1)  # mV vers V
        else:
            self._attr_native_value = None
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxPowerSensor(CoordinatorEntity, SensorEntity):
    """Capteur de puissance active."""

    def __init__(self, coordinator: PowerBoxRealtimeCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Puissance"
        self._attr_unique_id = f"powerbox_power"
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_meter_value("EVPLCCom-Virtual-Meter", "ActivePower_W")
        if value is not None:
            self._attr_native_value = round(value, 0)
        else:
            self._attr_native_value = 0
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxSessionEnergySensor(CoordinatorEntity, SensorEntity):
    """Capteur d'énergie de la session de charge en cours."""

    def __init__(self, coordinator: PowerBoxRealtimeCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Énergie Session"
        self._attr_unique_id = f"powerbox_session_energy"
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_meter_value("EVPLCCom-Virtual-Meter", "SessionTotalEnergy_Ws")
        if value is not None:
            self._attr_native_value = round(value / 3600 / 1000, 2)  # Ws vers kWh
        else:
            self._attr_native_value = 0
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxTotalEnergySensor(CoordinatorEntity, SensorEntity):
    """Capteur d'énergie totale de la borne (depuis l'installation)."""

    def __init__(self, coordinator: PowerBoxRealtimeCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Énergie Totale"
        self._attr_unique_id = f"powerbox_total_energy"
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_meter_value("Power Board Meter", "ActiveEnergy_Ws")
        if value is not None:
            self._attr_native_value = round(value / 3600 / 1000, 1)  # Ws vers kWh
        else:
            self._attr_native_value = None
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxTicCurrentSensor(CoordinatorEntity, SensorEntity):
    """Capteur de courant TiC (téléinformation client)."""

    def __init__(self, coordinator: PowerBoxRealtimeCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Courant TiC"
        self._attr_unique_id = f"powerbox_tic_current"
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_meter_value("TiC", "Current_PhaseA_mA")
        if value is not None:
            self._attr_native_value = round(value / 1000, 2)  # mA vers A
        else:
            self._attr_native_value = None
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxTicPowerSensor(CoordinatorEntity, SensorEntity):
    """Capteur de puissance apparente TiC."""

    def __init__(self, coordinator: PowerBoxRealtimeCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Puissance TiC"
        self._attr_unique_id = f"powerbox_tic_power"
        self._attr_native_unit_of_measurement = "VA"  # Volt-Ampère
        self._attr_device_class = SensorDeviceClass.APPARENT_POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_meter_value("TiC", "ApparentPower_VA")
        if value is not None:
            self._attr_native_value = round(value, 0)
        else:
            self._attr_native_value = None
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


# ============================================================================
# CAPTEURS DE CONFIGURATION (depuis /configs) - Coordinateur 5min
# ============================================================================

class PowerBoxMaxCurrentSensor(CoordinatorEntity, SensorEntity):
    """Capteur de courant maximum configuré."""

    def __init__(self, coordinator: PowerBoxConfigCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Courant Maximum"
        self._attr_unique_id = f"powerbox_max_current"
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_config_value("ChargerApp.ACCharging.maxCurrent_mA")
        if value:
            try:
                self._attr_native_value = round(int(value) / 1000, 2)  # mA vers A
            except (ValueError, TypeError):
                self._attr_native_value = None
        else:
            self._attr_native_value = None
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxHouseholdPowerLimitSensor(CoordinatorEntity, SensorEntity):
    """Capteur de limite de puissance du foyer."""

    def __init__(self, coordinator: PowerBoxConfigCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Limite Puissance Foyer"
        self._attr_unique_id = f"powerbox_household_power_limit"
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_config_value("ihal.household.PowerLimit_W")
        if value:
            try:
                self._attr_native_value = int(value)
            except (ValueError, TypeError):
                self._attr_native_value = None
        else:
            self._attr_native_value = None
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxDynamicLoadModeSensor(CoordinatorEntity, SensorEntity):
    """Capteur du mode de gestion dynamique de charge."""

    def __init__(self, coordinator: PowerBoxConfigCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Mode Gestion Dynamique"
        self._attr_unique_id = f"powerbox_dynamic_load_mode"
        self._attr_icon = "mdi:sync"
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_config_value("DynamicLoadManager.CurrentSet")
        self._attr_native_value = value if value else "unknown"
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxChargerModeSensor(CoordinatorEntity, SensorEntity):
    """Capteur du mode de charge."""

    def __init__(self, coordinator: PowerBoxConfigCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Mode de Charge"
        self._attr_unique_id = f"powerbox_charger_mode"
        self._attr_icon = "mdi:ev-station"
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_config_value("ChargerMode.CurrentSet")
        self._attr_native_value = value if value else "unknown"
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxCountrySensor(CoordinatorEntity, SensorEntity):
    """Capteur du pays configuré."""

    def __init__(self, coordinator: PowerBoxConfigCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Pays"
        self._attr_unique_id = f"powerbox_country"
        self._attr_icon = "mdi:flag"
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_config_value("product.countryName")
        self._attr_native_value = value if value else "unknown"
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxInstallationTypeSensor(CoordinatorEntity, SensorEntity):
    """Capteur du type d'installation."""

    def __init__(self, coordinator: PowerBoxConfigCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Type d'Installation"
        self._attr_unique_id = f"powerbox_installation_type"
        self._attr_icon = "mdi:home-lightning-bolt"
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_config_value("product.installationType")
        self._attr_native_value = value if value else "unknown"
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success
