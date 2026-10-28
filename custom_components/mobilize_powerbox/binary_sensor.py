"""Capteurs binaires pour Mobilize PowerBox (état de la borne et du branchement)."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PowerBoxStatusCoordinator

_LOGGER = logging.getLogger(__name__)

# États du pilote IEC 61851 : A = rien, B = véhicule connecté, C/D = en charge
PILOT_VEHICLE_CONNECTED = ("B", "C", "D")
PILOT_CHARGING = ("C", "D")


@dataclass(frozen=True, kw_only=True)
class PowerBoxBinarySensorDescription(BinarySensorEntityDescription):
    """Description d'un capteur binaire PowerBox."""

    is_on_fn: Callable[[PowerBoxStatusCoordinator], bool | None]
    icon_on: str | None = None
    icon_off: str | None = None


def _cable_plugged(coordinator: PowerBoxStatusCoordinator) -> bool | None:
    state = coordinator.get_socket_value("CableState")
    return None if state is None else state == "Plugged"


def _vehicle_connected(coordinator: PowerBoxStatusCoordinator) -> bool | None:
    pilot = coordinator.get_charging_module_value("basic", "CP") or coordinator.get_socket_value("state")
    return None if pilot is None else pilot in PILOT_VEHICLE_CONNECTED


def _socket_locked(coordinator: PowerBoxStatusCoordinator) -> bool | None:
    state = coordinator.get_socket_value("SocketLock")
    return None if state is None else state == "Locked"


def _charging(coordinator: PowerBoxStatusCoordinator) -> bool | None:
    state = coordinator.get_socket_value("ChargingState")
    pilot = coordinator.get_charging_module_value("basic", "CP")
    if state is None and pilot is None:
        return None
    return state == "Charging" or pilot in PILOT_CHARGING


BINARY_SENSORS: tuple[PowerBoxBinarySensorDescription, ...] = (
    PowerBoxBinarySensorDescription(
        key="cable_plugged",
        name="PowerBox Câble Branché",
        device_class=BinarySensorDeviceClass.PLUG,
        is_on_fn=_cable_plugged,
    ),
    PowerBoxBinarySensorDescription(
        key="vehicle_connected",
        name="PowerBox Véhicule Connecté",
        device_class=BinarySensorDeviceClass.PLUG,
        icon_on="mdi:car-electric",
        icon_off="mdi:car-off",
        is_on_fn=_vehicle_connected,
    ),
    PowerBoxBinarySensorDescription(
        key="charging",
        name="PowerBox En Charge",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        is_on_fn=_charging,
    ),
    # Pas de device_class LOCK : sa sémantique est inversée (on = déverrouillé)
    PowerBoxBinarySensorDescription(
        key="socket_locked",
        name="PowerBox Prise Verrouillée",
        icon_on="mdi:lock",
        icon_off="mdi:lock-open-variant",
        is_on_fn=_socket_locked,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Configuration des capteurs binaires depuis une config entry."""
    domain_data = hass.data[DOMAIN][entry.entry_id]
    coordinator_status: PowerBoxStatusCoordinator = domain_data["coordinator_status"]
    device_info = domain_data["device_info"]

    async_add_entities(
        PowerBoxStatusBinarySensor(coordinator_status, device_info, description)
        for description in BINARY_SENSORS
    )


class PowerBoxStatusBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Capteur binaire alimenté par /status/chargingmodule et /status/custominfo."""

    entity_description: PowerBoxBinarySensorDescription

    def __init__(
        self,
        coordinator: PowerBoxStatusCoordinator,
        device_info,
        description: PowerBoxBinarySensorDescription,
    ):
        """Initialisation."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = description.name
        self._attr_unique_id = f"powerbox_{description.key}"
        self._attr_device_info = device_info
        self._update_from_coordinator()

    def _update_from_coordinator(self) -> None:
        self._attr_is_on = self.entity_description.is_on_fn(self.coordinator)
        if self.entity_description.icon_on:
            self._attr_icon = (
                self.entity_description.icon_on
                if self._attr_is_on
                else self.entity_description.icon_off
            )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Mise à jour du capteur avec les données du coordinateur."""
        self._update_from_coordinator()
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success
