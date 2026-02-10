"""Config flow for City4U Water Consumption integration."""

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api import City4UApiClient, City4UCredentials
from .const import CONF_CUSTOMER_ID, CONF_METER_NUMBER, CONF_MUNICIPALITY, DOMAIN
from .municipalities import MUNICIPALITIES_SORTED_HE

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    session = async_get_clientsession(hass)

    # Verify that we can log in
    credentials = City4UCredentials(
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
        customer_id=data[CONF_CUSTOMER_ID],
        meter_number=data.get(CONF_METER_NUMBER, data[CONF_USERNAME]),
    )
    api = City4UApiClient(credentials=credentials, session=session)

    try:
        await api.authenticate()
    except aiohttp.ClientResponseError as err:
        _LOGGER.error("Authentication error: %s", err)
        raise InvalidAuth from err
    except aiohttp.ClientError as err:
        _LOGGER.error("Connection error: %s", err)
        raise CannotConnect from err

    # Test data fetching
    try:
        water_data = await api.fetch_water_data()
        if not water_data:
            raise CannotFetchData("No data returned")
    except Exception as err:
        _LOGGER.error("Failed to fetch water data: %s", err)
        raise CannotFetchData from err

    # Return info to be stored in the config entry
    return {
        "title": f"Water Meter {data.get(CONF_METER_NUMBER, data[CONF_USERNAME])}",
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # pylint: disable=abstract-method
    """Handle a config flow for City4U Water Consumption."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._municipality_map: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}

        # Create municipality selector options on first call
        if not self._municipality_map:
            self._municipality_map = {
                str(m.name_he): str(m.customer_id) for m in MUNICIPALITIES_SORTED_HE
            }

        if user_input is not None:
            # Convert municipality selection to customer_id
            if CONF_MUNICIPALITY in user_input:
                municipality_label = user_input[CONF_MUNICIPALITY]
                user_input[CONF_CUSTOMER_ID] = self._municipality_map[
                    municipality_label
                ]
                del user_input[CONF_MUNICIPALITY]

            # Default meter number to username if not provided
            if not user_input.get(CONF_METER_NUMBER):
                user_input[CONF_METER_NUMBER] = user_input[CONF_USERNAME]

            try:
                info = await validate_input(self.hass, user_input)

                # Check if entry already exists with these credentials
                await self.async_set_unique_id(
                    f"{user_input[CONF_CUSTOMER_ID]}_{user_input[CONF_METER_NUMBER]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotFetchData:
                errors["base"] = "cannot_fetch_data"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Create municipality selector options
        municipality_options = list(self._municipality_map.keys())

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_MUNICIPALITY): SelectSelector(
                        SelectSelectorConfig(
                            options=municipality_options,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(CONF_METER_NUMBER): str,
                }
            ),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class CannotFetchData(HomeAssistantError):
    """Error to indicate we cannot fetch data."""
