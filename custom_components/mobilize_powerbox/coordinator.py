"""DataUpdateCoordinators pour Mobilize PowerBox."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
import requests

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

# Intervalles de mise à jour selon les recommandations HA
SCAN_INTERVAL_REALTIME = timedelta(seconds=10)  # Mesures temps réel
SCAN_INTERVAL_CONFIG = timedelta(minutes=5)  # Configuration


@dataclass
class PowerBoxData:
    """Class to hold PowerBox data."""

    meters_parsed: dict
    configs: dict | None = None


class PowerBoxAPIClient:
    """Client API pour la PowerBox."""

    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool):
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
            if err.response and err.response.status_code == 503:
                _LOGGER.warning("PowerBox temporairement indisponible (503)")
                raise UpdateFailed("PowerBox temporairement indisponible") from err
            raise
        except requests.exceptions.RequestException as err:
            _LOGGER.error(f"Erreur lors de l'authentification: {err}")
            raise UpdateFailed(f"Erreur d'authentification: {err}") from err

    def fetch_data(self, endpoint: str):
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
            if err.response and err.response.status_code == 503:
                _LOGGER.warning(f"PowerBox temporairement indisponible pour {endpoint} (503)")
                raise UpdateFailed("PowerBox temporairement indisponible") from err
            _LOGGER.error(f"Erreur HTTP lors de la récupération de {endpoint}: {err}")
            raise UpdateFailed(f"Erreur HTTP: {err}") from err
        except requests.exceptions.RequestException as err:
            _LOGGER.error(f"Erreur lors de la récupération de {endpoint}: {err}")
            raise UpdateFailed(f"Erreur de connexion: {err}") from err


class PowerBoxRealtimeCoordinator(DataUpdateCoordinator):
    """Coordinateur pour les mesures temps réel (10s)."""

    data: PowerBoxData

    def __init__(self, hass: HomeAssistant, api_client: PowerBoxAPIClient) -> None:
        """Initialisation du coordinateur temps réel."""
        self.api_client = api_client
        
        # Initialiser DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name="Mobilize PowerBox Realtime",
            update_method=self.async_update_data,
            update_interval=SCAN_INTERVAL_REALTIME,
        )

    async def async_update_data(self) -> PowerBoxData:
        """Récupère les mesures temps réel."""
        _LOGGER.debug("[Realtime] Starting data update")
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
            
            _LOGGER.debug("[Realtime] Successfully fetched data for %d meters", len(meters_parsed))
            return PowerBoxData(meters_parsed=meters_parsed)
            
        except Exception as err:
            _LOGGER.error("[Realtime] Failed to update data: %s", err)
            raise UpdateFailed(f"Erreur lors de la mise à jour des mesures: {err}") from err

    def get_meter_value(self, meter_model: str, value_name: str):
        """Récupère une valeur spécifique d'un compteur."""
        if not self.data or not self.data.meters_parsed:
            return None
        
        meter = self.data.meters_parsed.get(meter_model)
        if not meter or not meter.get("connected"):
            return None
        
        value_data = meter.get("values", {}).get(value_name)
        if value_data:
            return value_data.get("value")
        return None


class PowerBoxConfigCoordinator(DataUpdateCoordinator):
    """Coordinateur pour la configuration (5 minutes)."""

    data: PowerBoxData

    def __init__(self, hass: HomeAssistant, api_client: PowerBoxAPIClient) -> None:
        """Initialisation du coordinateur de configuration."""
        self.api_client = api_client
        
        # Initialiser DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name="Mobilize PowerBox Config",
            update_method=self.async_update_data,
            update_interval=SCAN_INTERVAL_CONFIG,
        )

    async def async_update_data(self) -> PowerBoxData:
        """Récupère la configuration."""
        _LOGGER.debug("[Config] Starting configuration update")
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
            
            _LOGGER.debug("[Config] Successfully fetched %d configuration parameters", len(configs))
            return PowerBoxData(meters_parsed={}, configs=configs)
            
        except Exception as err:
            _LOGGER.error("[Config] Failed to update configuration: %s", err)
            raise UpdateFailed(f"Erreur lors de la mise à jour de la configuration: {err}") from err

    def get_config_value(self, config_key: str):
        """Récupère une valeur de configuration."""
        if not self.data or not self.data.configs:
            return None
        
        config = self.data.configs.get(config_key)
        if config:
            return config.get("config_value")
        return None
