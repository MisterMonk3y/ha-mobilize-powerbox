"""Config flow for Mobilize PowerBox integration."""
from __future__ import annotations

import logging
import voluptuous as vol
import requests
from urllib3.exceptions import InsecureRequestWarning

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_NAME
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    DOMAIN,
    CONF_VERIFY_SSL,
    DEFAULT_NAME,
    DEFAULT_USERNAME,
    DEFAULT_VERIFY_SSL,
    ERROR_CANNOT_CONNECT,
    ERROR_INVALID_AUTH,
    ERROR_TIMEOUT,
    ERROR_UNKNOWN,
    TIMEOUT_AUTH,
)

# Désactiver les avertissements SSL pour certificats auto-signés
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

_LOGGER = logging.getLogger(__name__)


async def validate_connection(hass: HomeAssistant, host: str, username: str, password: str, verify_ssl: bool):
    """Valide la connexion à la PowerBox."""
    
    def _test_connection():
        """Test de connexion (exécuté dans un executor)."""
        url = f"https://{host}/v1.0/auth"
        payload = {"username": username, "password": password}
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                headers=headers, 
                verify=verify_ssl,
                timeout=TIMEOUT_AUTH
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id_token" in data:
                    return True, None, None
                return False, ERROR_UNKNOWN, "Token not found in response"
            elif response.status_code == 401:
                return False, ERROR_INVALID_AUTH, "Invalid credentials"
            else:
                return False, ERROR_UNKNOWN, f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, ERROR_TIMEOUT, "Connection timeout"
        except requests.exceptions.ConnectionError:
            return False, ERROR_CANNOT_CONNECT, "Cannot connect to PowerBox"
        except Exception as e:
            _LOGGER.exception("Unexpected error during connection test")
            return False, ERROR_UNKNOWN, str(e)
    
    # Exécuter le test dans un executor pour ne pas bloquer l'event loop
    success, error_code, message = await hass.async_add_executor_job(_test_connection)
    
    if not success:
        raise CannotConnect(error_code, message)
    
    return True


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
    
    def __init__(self, error_code: str, message: str):
        """Initialize the exception."""
        self.error_code = error_code
        self.message = message
        super().__init__(message)


class PowerBoxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mobilize PowerBox Verso."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Valider la connexion
            try:
                await validate_connection(
                    self.hass,
                    user_input[CONF_HOST],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)
                )
                
                # Créer un identifiant unique basé sur l'host
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                
                # Créer l'entrée de configuration
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    data=user_input
                )
                
            except CannotConnect as err:
                errors["base"] = err.error_code
                _LOGGER.error("Cannot connect to PowerBox: %s", err.message)
            except Exception as err:
                errors["base"] = ERROR_UNKNOWN
                _LOGGER.exception("Unexpected exception during configuration")

        # Afficher le formulaire
        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_USERNAME, default=DEFAULT_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "host_example": "192.168.0.40",
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        # HA renseigne lui-même self.config_entry (2024.11+)
        return PowerBoxOptionsFlow()


class PowerBoxOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for PowerBox."""

    async def async_step_init(self, user_input=None):
        """Modifie les identifiants de connexion."""
        errors = {}
        data = self.config_entry.data

        if user_input is not None:
            # Mot de passe laissé vide : on garde l'actuel
            if not user_input.get(CONF_PASSWORD):
                user_input[CONF_PASSWORD] = data[CONF_PASSWORD]
            try:
                await validate_connection(
                    self.hass,
                    data[CONF_HOST],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_VERIFY_SSL],
                )
                # Le setup lit entry.data : on y écrit les nouveaux identifiants,
                # l'update listener recharge ensuite l'intégration
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data={**data, **user_input}
                )
                return self.async_create_entry(title="", data={})

            except CannotConnect as err:
                errors["base"] = err.error_code
                _LOGGER.error("Cannot connect to PowerBox: %s", err.message)
            except Exception:
                errors["base"] = ERROR_UNKNOWN
                _LOGGER.exception("Unexpected exception during options update")

        options_schema = vol.Schema({
            vol.Required(
                CONF_USERNAME,
                default=data.get(CONF_USERNAME, DEFAULT_USERNAME)
            ): str,
            vol.Optional(CONF_PASSWORD): TextSelector(
                TextSelectorConfig(type=TextSelectorType.PASSWORD)
            ),
            vol.Optional(
                CONF_VERIFY_SSL,
                default=data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)
            ): bool,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
        )
