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
    "serial",
    "password",
    "simpin",
}


def _serialize_meters(meters_parsed: dict | None) -> dict | None:
    """Serialize meters for diagnostics, redacting serials."""
    if not meters_parsed:
        return None

    result = {}
    for model, meter in meters_parsed.items():
        values = meter.get("values") or {}
        result[model] = {
            "connected": meter.get("connected"),
            "id": meter.get("id"),
            "manufacturer": meter.get("manufacturer"),
            "serial": "**REDACTED**" if meter.get("serial") else None,
            "value_names": sorted(values.keys()),
            "values": {
                name: {
                    "value": data.get("value"),
                    "timestamp": data.get("timestamp"),
                }
                for name, data in values.items()
            },
        }
    return result


def _serialize_configs(configs: dict | None) -> dict | None:
    """Serialize configs as key -> value for easier inspection."""
    if not configs:
        return None

    result = {}
    for key, config in configs.items():
        if isinstance(config, dict):
            result[key] = config.get("config_value")
        else:
            result[key] = config
    return async_redact_data(result, TO_REDACT)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Retourne les informations de diagnostic pour une config entry."""

    domain_data = hass.data[DOMAIN][entry.entry_id]
    coordinator_realtime = domain_data.get("coordinator_realtime") or domain_data.get(
        DATA_COORDINATOR
    )
    coordinator_config = domain_data.get("coordinator_config")

    meters_parsed = None
    if coordinator_realtime and coordinator_realtime.data:
        meters_parsed = coordinator_realtime.data.meters_parsed

    configs = None
    if coordinator_config and coordinator_config.data:
        configs = coordinator_config.data.configs

    diagnostics_data = {
        "entry": {
            "title": entry.title,
            "version": entry.version,
            "domain": entry.domain,
            "unique_id": entry.unique_id,
        },
        "coordinator_realtime": {
            "last_update_success": getattr(
                coordinator_realtime, "last_update_success", None
            ),
            "update_interval": str(getattr(coordinator_realtime, "update_interval", None)),
        },
        "coordinator_config": {
            "last_update_success": getattr(
                coordinator_config, "last_update_success", None
            ),
            "update_interval": str(getattr(coordinator_config, "update_interval", None)),
        },
        "data": {
            "meters": _serialize_meters(meters_parsed),
            "configs": _serialize_configs(configs),
        },
        "config": async_redact_data(dict(entry.data), TO_REDACT),
    }

    return diagnostics_data
