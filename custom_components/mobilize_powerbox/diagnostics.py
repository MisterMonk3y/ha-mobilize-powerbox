"""Diagnostics support for Mobilize PowerBox."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN, DATA_COORDINATOR

# Informations sensibles à masquer
TO_REDACT = {
    CONF_PASSWORD,
    CONF_USERNAME,
    "id_token",
    "token",
    "serial_number",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Retourne les informations de diagnostic pour une config entry."""
    
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    
    # Collecter les données de diagnostic
    diagnostics_data = {
        "entry": {
            "title": entry.title,
            "version": entry.version,
            "domain": entry.domain,
            "unique_id": entry.unique_id,
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_update_time": coordinator.last_update_success_time.isoformat() 
                if coordinator.last_update_success_time else None,
            "update_interval": str(coordinator.update_interval),
        },
        "data": {
            "meters": coordinator.data.get("meters", {}) if coordinator.data else None,
            "configs": coordinator.data.get("configs", {}) if coordinator.data else None,
        },
        "config": async_redact_data(entry.data, TO_REDACT),
    }
    
    return diagnostics_data
