"""Capteurs pour Mobilize PowerBox."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfEnergy,
    UnitOfReactivePower,
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
    
    # Créer les capteurs temps réel
    realtime_sensors = [
        PowerBoxCurrentSensor(coordinator_realtime, device_info),
        PowerBoxVoltageSensor(coordinator_realtime, device_info),
        PowerBoxPowerSensor(coordinator_realtime, device_info),
        PowerBoxSessionEnergySensor(coordinator_realtime, device_info),
        PowerBoxTotalEnergySensor(coordinator_realtime, device_info),
        PowerBoxTicCurrentSensor(coordinator_realtime, device_info),
        PowerBoxTicPowerSensor(coordinator_realtime, device_info),
        PowerBoxReactivePowerSensor(coordinator_realtime, device_info),
        PowerBoxApparentPowerSensor(coordinator_realtime, device_info),
        PowerBoxPowerFactorSensor(coordinator_realtime, device_info),
        PowerBoxInjectedEnergySensor(coordinator_realtime, device_info),
    ]
    
    # Créer les capteurs de configuration
    config_sensors = [
        PowerBoxMaxCurrentSensor(coordinator_config, device_info),
        PowerBoxHouseholdPowerLimitSensor(coordinator_config, device_info),
        PowerBoxDynamicLoadModeSensor(coordinator_config, device_info),
        PowerBoxChargerModeSensor(coordinator_config, device_info),
        PowerBoxCountrySensor(coordinator_config, device_info),
        PowerBoxInstallationTypeSensor(coordinator_config, device_info),
        PowerBoxV2GContractSensor(coordinator_config, device_info),
        PowerBoxGridProfileSensor(coordinator_config, device_info),
        PowerBoxEmergencyStopSensor(coordinator_config, device_info),
        PowerBoxGridTopologySensor(coordinator_config, device_info),
        PowerBoxDesignPowerSensor(coordinator_config, device_info),
        PowerBoxOfflineCurrentLimitSensor(coordinator_config, device_info),
        PowerBoxPhaseImbalanceSensor(coordinator_config, device_info),
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


# ============================================================================
# CAPTEURS TEMPS RÉEL ADDITIONNELS (Power Board Meter)
# ============================================================================

class PowerBoxReactivePowerSensor(CoordinatorEntity, SensorEntity):
    """Capteur de puissance réactive réseau."""

    def __init__(self, coordinator: PowerBoxRealtimeCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Puissance Réactive"
        self._attr_unique_id = "powerbox_reactive_power"
        self._attr_native_unit_of_measurement = UnitOfReactivePower.VOLT_AMPERE_REACTIVE
        self._attr_device_class = SensorDeviceClass.REACTIVE_POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_meter_value("Power Board Meter", "ReactivePower_var")
        if value is not None:
            self._attr_native_value = round(value, 0)
        else:
            self._attr_native_value = None
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxApparentPowerSensor(CoordinatorEntity, SensorEntity):
    """Capteur de puissance apparente réseau (Power Board)."""

    def __init__(self, coordinator: PowerBoxRealtimeCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Puissance Apparente Réseau"
        self._attr_unique_id = "powerbox_apparent_power_grid"
        self._attr_native_unit_of_measurement = "VA"
        self._attr_device_class = SensorDeviceClass.APPARENT_POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_meter_value("Power Board Meter", "ApparentPower_VA")
        if value is not None:
            self._attr_native_value = round(value, 0)
        else:
            self._attr_native_value = None
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxPowerFactorSensor(CoordinatorEntity, SensorEntity):
    """Capteur de facteur de puissance réseau (API en milli-unités)."""

    def __init__(self, coordinator: PowerBoxRealtimeCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Facteur de Puissance"
        self._attr_unique_id = "powerbox_power_factor"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = SensorDeviceClass.POWER_FACTOR
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_meter_value("Power Board Meter", "PowerFactor")
        if value is not None:
            self._attr_native_value = round(value / 1000, 3)
        else:
            self._attr_native_value = None
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxInjectedEnergySensor(CoordinatorEntity, SensorEntity):
    """Capteur d'énergie injectée au réseau (V2G / surplus)."""

    def __init__(self, coordinator: PowerBoxRealtimeCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Énergie Injectée Totale"
        self._attr_unique_id = "powerbox_injected_energy"
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_meter_value("Power Board Meter", "ActiveEnergyNegative_Ws")
        if value is not None:
            self._attr_native_value = round(value / 3600 / 1000, 1)
        else:
            self._attr_native_value = None
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


# ============================================================================
# CAPTEURS DE CONFIGURATION ADDITIONNELS
# ============================================================================

class PowerBoxV2GContractSensor(CoordinatorEntity, SensorEntity):
    """Capteur de l'état du contrat V2G."""

    def __init__(self, coordinator: PowerBoxConfigCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Contrat V2G"
        self._attr_unique_id = "powerbox_v2g_contract"
        self._attr_icon = "mdi:car-electric"
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_config_value("V2GContracts.CurrentSet")
        self._attr_native_value = value if value else "unknown"
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxGridProfileSensor(CoordinatorEntity, SensorEntity):
    """Capteur du profil réseau sélectionné."""

    def __init__(self, coordinator: PowerBoxConfigCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Profil Réseau"
        self._attr_unique_id = "powerbox_grid_profile"
        self._attr_icon = "mdi:transmission-tower"
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_config_value("GridCodesProfile.SelectedProfile")
        self._attr_native_value = value if value else "unknown"
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxEmergencyStopSensor(CoordinatorEntity, SensorEntity):
    """Capteur de l'état de l'arrêt d'urgence."""

    def __init__(self, coordinator: PowerBoxConfigCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Arrêt d'Urgence"
        self._attr_unique_id = "powerbox_emergency_stop"
        self._attr_icon = "mdi:alert-octagon"
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_config_value("ihal.EmergencyStop.reaction")
        self._attr_native_value = value if value else "unknown"
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxGridTopologySensor(CoordinatorEntity, SensorEntity):
    """Capteur de la topologie réseau (mono/tri)."""

    def __init__(self, coordinator: PowerBoxConfigCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Topologie Réseau"
        self._attr_unique_id = "powerbox_grid_topology"
        self._attr_icon = "mdi:sine-wave"
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_config_value("GridCodes.GridTopology")
        self._attr_native_value = value if value else "unknown"
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxDesignPowerSensor(CoordinatorEntity, SensorEntity):
    """Capteur de la puissance active de conception."""

    def __init__(self, coordinator: PowerBoxConfigCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Puissance de Conception"
        self._attr_unique_id = "powerbox_design_power"
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_config_value("GridCodes.DesignActivePower_W")
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


class PowerBoxOfflineCurrentLimitSensor(CoordinatorEntity, SensorEntity):
    """Capteur de la limite de courant hors ligne."""

    def __init__(self, coordinator: PowerBoxConfigCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Courant Max Hors Ligne"
        self._attr_unique_id = "powerbox_offline_current_limit"
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        value = self.coordinator.get_config_value(
            "EnergyManager.EnergyMgr.ocpp.offlineCurrentLimit_mA"
        )
        if value:
            try:
                self._attr_native_value = round(int(value) / 1000, 2)
            except (ValueError, TypeError):
                self._attr_native_value = None
        else:
            self._attr_native_value = None
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success


class PowerBoxPhaseImbalanceSensor(CoordinatorEntity, SensorEntity):
    """Capteur de l'état de la limitation de déséquilibre de phases."""

    def __init__(self, coordinator: PowerBoxConfigCoordinator, device_info):
        """Initialisation."""
        super().__init__(coordinator)
        self._attr_name = "PowerBox Déséquilibre de Phases"
        self._attr_unique_id = "powerbox_phase_imbalance"
        self._attr_icon = "mdi:scale-balance"
        self._attr_device_info = device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        enabled = self.coordinator.get_config_value("EnergyManager.imbalance.enabled")
        value = self.coordinator.get_config_value("EnergyManager.imbalance.value")
        if enabled is None:
            self._attr_native_value = "unknown"
        elif str(enabled).lower() == "true":
            self._attr_native_value = value if value is not None else "enabled"
        else:
            self._attr_native_value = "Off"
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success
