"""Intégration Mobilize PowerBox pour Home Assistant."""
from __future__ import annotations

import logging
import requests

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    DATA_COORDINATOR,
    DATA_DEVICE_INFO,
    DATA_UNDO_UPDATE_LISTENER,
    CONF_VERIFY_SSL,
    INTEGRATION_MANUFACTURER,
    INTEGRATION_MODEL,
)
from .sensor import PowerBoxAPIClient, PowerBoxRealtimeCoordinator, PowerBoxConfigCoordinator

# Désactiver les avertissements SSL
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mobilize PowerBox from a config entry."""
    
    # Récupérer la configuration
    host = entry.data[CONF_HOST]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    verify_ssl = entry.data.get(CONF_VERIFY_SSL, False)
    name = entry.data.get(CONF_NAME, "PowerBox Verso")
    
    base_url = f"https://{host}/v1.0"
    
    _LOGGER.info("Configuration de Mobilize PowerBox: %s", host)
    
    # Créer le client API partagé
    api_client = PowerBoxAPIClient(base_url, username, password, verify_ssl)
    
    # Créer les coordinateurs (temps réel + configuration)
    coordinator_realtime = PowerBoxRealtimeCoordinator(hass, api_client)
    coordinator_config = PowerBoxConfigCoordinator(hass, api_client)
    
    # Faire les premières mises à jour
    await coordinator_realtime.async_config_entry_first_refresh()
    await coordinator_config.async_config_entry_first_refresh()
    
    # Informations sur l'appareil
    device_info = DeviceInfo(
        identifiers={(DOMAIN, host)},
        name=name,
        manufacturer=INTEGRATION_MANUFACTURER,
        model=INTEGRATION_MODEL,
        sw_version="1.0.0",
        configuration_url=f"https://{host}",
    )
    
    # Stocker les données
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator_realtime,  # Pour compatibilité
        "coordinator_realtime": coordinator_realtime,
        "coordinator_config": coordinator_config,
        DATA_DEVICE_INFO: device_info,
    }
    
    # Charger les plateformes
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Écouter les mises à jour d'options
    undo_listener = entry.add_update_listener(async_reload_entry)
    hass.data[DOMAIN][entry.entry_id][DATA_UNDO_UPDATE_LISTENER] = undo_listener
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Supprimer le listener
    undo_listener = hass.data[DOMAIN][entry.entry_id].get(DATA_UNDO_UPDATE_LISTENER)
    if undo_listener:
        undo_listener()
    
    # Décharger les plateformes
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
