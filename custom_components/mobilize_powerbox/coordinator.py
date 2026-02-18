"""DataUpdateCoordinators pour Mobilize PowerBox."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
import time
import requests

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

# Intervalles de mise à jour selon les recommandations HA
SCAN_INTERVAL_REALTIME = timedelta(seconds=30)  # Mesures temps réel - augmenté pour réduire la charge
SCAN_INTERVAL_CONFIG = timedelta(minutes=10)  # Configuration - augmenté pour stabilité
SCAN_INTERVAL_REALTIME_ERROR = timedelta(minutes=2)  # Intervalle après erreur (backoff)


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
        self._session = None
        self._consecutive_errors = 0
        self._last_error_time = None
    
    def _get_session(self):
        """Récupère ou crée une session HTTP."""
        if self._session is None:
            self._session = requests.Session()
            # Configuration de la session pour éviter les problèmes de connexion
            self._session.headers.update({
                "Connection": "close",  # Évite les problèmes de keep-alive
                "User-Agent": "HomeAssistant/MobilizePowerBox"
            })
        return self._session

    def _get_auth_token(self):
        """Récupère le token d'authentification avec mécanisme de retry."""
        url = f"{self.base_url}/auth"
        payload = {"username": self.username, "password": self.password}
        headers = {"Content-Type": "application/json"}
        
        max_retries = 3
        retry_delay = 3  # Augmenté à 3 secondes
        
        for attempt in range(max_retries):
            try:
                session = self._get_session()
                _LOGGER.debug(f"Tentative d'authentification {attempt + 1}/{max_retries}")
                
                response = session.post(
                    url, 
                    json=payload, 
                    headers=headers, 
                    verify=self.verify_ssl,
                    timeout=20  # Augmenté à 20 secondes pour bornes instables
                )
                response.raise_for_status()
                token = response.json().get("id_token")
                if token:
                    _LOGGER.debug("Authentification réussie")
                    self._consecutive_errors = 0  # Réinitialiser le compteur d'erreurs
                    return token
                else:
                    _LOGGER.error("Pas de token dans la réponse")
                    raise UpdateFailed("Pas de token dans la réponse d'authentification")
                    
            except requests.exceptions.HTTPError as err:
                if err.response and err.response.status_code == 503:
                    _LOGGER.warning("PowerBox temporairement indisponible (503)")
                    self._consecutive_errors += 1
                    raise UpdateFailed("PowerBox temporairement indisponible") from err
                _LOGGER.error(f"Erreur HTTP lors de l'authentification: {err}")
                self._consecutive_errors += 1
                raise UpdateFailed(f"Erreur HTTP: {err}") from err
                
            except (requests.exceptions.ConnectionError, ConnectionResetError, requests.exceptions.Timeout) as err:
                _LOGGER.warning(f"Erreur de connexion (tentative {attempt + 1}/{max_retries}): {err}")
                
                # Réinitialiser la session en cas d'erreur de connexion
                if self._session:
                    try:
                        self._session.close()
                    except Exception:
                        pass
                    self._session = None
                
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)  # Backoff progressif
                    _LOGGER.debug(f"Attente de {wait_time}s avant nouvelle tentative")
                    time.sleep(wait_time)
                    continue
                else:
                    _LOGGER.error(f"Échec de l'authentification après {max_retries} tentatives")
                    self._consecutive_errors += 1
                    self._last_error_time = time.time()
                    raise UpdateFailed(f"PowerBox inaccessible après {max_retries} tentatives: {err}") from err
                    
            except requests.exceptions.RequestException as err:
                _LOGGER.error(f"Erreur lors de l'authentification: {err}")
                self._consecutive_errors += 1
                raise UpdateFailed(f"Erreur d'authentification: {err}") from err

    def fetch_data(self, endpoint: str):
        """Récupère les données depuis un endpoint avec gestion d'erreurs améliorée."""
        if not self._token:
            self._token = self._get_auth_token()
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self._token}",
        }
        
        max_retries = 2
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                session = self._get_session()
                response = session.get(url, headers=headers, verify=self.verify_ssl, timeout=20)
                
                if response.status_code == 401:
                    # Token expiré, réessayer avec un nouveau token
                    _LOGGER.debug("Token expiré, récupération d'un nouveau token")
                    self._token = self._get_auth_token()
                    headers["authorization"] = f"Bearer {self._token}"
                    response = session.get(url, headers=headers, verify=self.verify_ssl, timeout=20)
                
                response.raise_for_status()
                self._consecutive_errors = 0  # Réinitialiser le compteur d'erreurs
                return response.json()
                
            except requests.exceptions.HTTPError as err:
                if err.response and err.response.status_code == 503:
                    _LOGGER.warning(f"PowerBox temporairement indisponible pour {endpoint} (503)")
                    self._consecutive_errors += 1
                    raise UpdateFailed("PowerBox temporairement indisponible") from err
                _LOGGER.error(f"Erreur HTTP lors de la récupération de {endpoint}: {err}")
                self._consecutive_errors += 1
                raise UpdateFailed(f"Erreur HTTP: {err}") from err
                
            except (requests.exceptions.ConnectionError, ConnectionResetError, requests.exceptions.Timeout) as err:
                _LOGGER.warning(f"Erreur de connexion sur {endpoint} (tentative {attempt + 1}/{max_retries}): {err}")
                
                # Réinitialiser la session et le token
                if self._session:
                    try:
                        self._session.close()
                    except Exception:
                        pass
                    self._session = None
                self._token = None
                
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    _LOGGER.debug(f"Attente de {wait_time}s avant nouvelle tentative")
                    time.sleep(wait_time)
                    continue
                else:
                    _LOGGER.error(f"Échec de la récupération de {endpoint} après {max_retries} tentatives")
                    self._consecutive_errors += 1
                    self._last_error_time = time.time()
                    raise UpdateFailed(f"PowerBox inaccessible pour {endpoint} après {max_retries} tentatives") from err
                    
            except requests.exceptions.RequestException as err:
                _LOGGER.error(f"Erreur lors de la récupération de {endpoint}: {err}")
                self._consecutive_errors += 1
                raise UpdateFailed(f"Erreur de connexion: {err}") from err
        
        raise UpdateFailed(f"Échec de la récupération de {endpoint}")
    
    def close(self):
        """Ferme proprement la session HTTP."""
        if self._session:
            try:
                self._session.close()
            except Exception as err:
                _LOGGER.debug(f"Erreur lors de la fermeture de la session: {err}")
            finally:
                self._session = None
        self._token = None
    
    def is_having_issues(self):
        """Vérifie si la PowerBox rencontre des problèmes répétés."""
        return self._consecutive_errors >= 3
    
    def get_consecutive_errors(self):
        """Retourne le nombre d'erreurs consécutives."""
        return self._consecutive_errors


class PowerBoxRealtimeCoordinator(DataUpdateCoordinator):
    """Coordinateur pour les mesures temps réel (10s)."""

    data: PowerBoxData

    def __init__(self, hass: HomeAssistant, api_client: PowerBoxAPIClient) -> None:
        """Initialisation du coordinateur temps réel."""
        self.api_client = api_client
        self._last_successful_data = None
        self._error_count = 0
        
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
        
        # Ajuster l'intervalle si la PowerBox a des problèmes
        error_count = await self.hass.async_add_executor_job(
            self.api_client.get_consecutive_errors
        )
        
        if error_count >= 3:
            # Ralentir les mises à jour en cas de problèmes répétés
            new_interval = SCAN_INTERVAL_REALTIME_ERROR
            if self.update_interval != new_interval:
                _LOGGER.warning(
                    "[Realtime] PowerBox instable (%d erreurs), intervalle augmenté à %s",
                    error_count,
                    new_interval
                )
                self.update_interval = new_interval
        else:
            # Revenir à l'intervalle normal si tout va bien
            if self.update_interval != SCAN_INTERVAL_REALTIME:
                _LOGGER.info("[Realtime] PowerBox stable, intervalle normal rétabli")
                self.update_interval = SCAN_INTERVAL_REALTIME
        
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
            
            # Sauvegarder les données réussies
            result = PowerBoxData(meters_parsed=meters_parsed)
            self._last_successful_data = result
            self._error_count = 0
            
            return result
            
        except UpdateFailed as err:
            self._error_count += 1
            
            # Si on a des données précédentes, on les garde
            if self._last_successful_data:
                _LOGGER.warning(
                    "[Realtime] Erreur de mise à jour (erreur #%d), conservation des dernières valeurs: %s",
                    self._error_count,
                    err
                )
                # Retourner les dernières données connues au lieu de lever une erreur
                return self._last_successful_data
            else:
                _LOGGER.error("[Realtime] Failed to update data (no previous data): %s", err)
                raise
                
        except Exception as err:
            self._error_count += 1
            _LOGGER.error("[Realtime] Unexpected error: %s", err)
            
            # Si on a des données précédentes, on les garde
            if self._last_successful_data:
                return self._last_successful_data
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
        self._last_successful_data = None
        
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
            
            # Sauvegarder les données réussies
            result = PowerBoxData(meters_parsed={}, configs=configs)
            self._last_successful_data = result
            
            return result
            
        except UpdateFailed as err:
            # La configuration change rarement, on peut garder les anciennes valeurs
            if self._last_successful_data:
                _LOGGER.warning(
                    "[Config] Erreur de mise à jour, conservation de la dernière configuration: %s",
                    err
                )
                return self._last_successful_data
            else:
                _LOGGER.error("[Config] Failed to update configuration (no previous data): %s", err)
                raise
                
        except Exception as err:
            if self._last_successful_data:
                _LOGGER.warning("[Config] Unexpected error, keeping previous config: %s", err)
                return self._last_successful_data
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
