"""The City4U Water Consumption integration."""

import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import City4UApiClient, City4UCredentials
from .const import CONF_CUSTOMER_ID, CONF_METER_NUMBER, DOMAIN, SCAN_INTERVAL
from .services import async_setup_services, async_unload_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

# Integration can only be set up from config entries
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)  # pylint: disable=invalid-name


async def async_setup(hass: HomeAssistant, _config: dict[str, Any]) -> bool:
    """Set up the City4U integration."""
    hass.data.setdefault(DOMAIN, {})
    await async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up City4U from a config entry."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    customer_id = entry.data[CONF_CUSTOMER_ID]
    meter_number = entry.data[CONF_METER_NUMBER]

    session = async_get_clientsession(hass)
    credentials = City4UCredentials(
        username=username,
        password=password,
        customer_id=customer_id,
        meter_number=meter_number,
    )
    api = City4UApiClient(credentials=credentials, session=session)

    try:
        await api.authenticate()
    except aiohttp.ClientResponseError as err:
        if err.status in (401, 403):
            _LOGGER.error("Authentication rejected (status %s): %s", err.status, err)
            raise ConfigEntryAuthFailed("Invalid credentials") from err
        _LOGGER.error("Authentication failed: %s", err)
        raise ConfigEntryNotReady(
            f"Authentication failed (status {err.status}): {err}"
        ) from err
    except aiohttp.ClientError as err:
        _LOGGER.error("Authentication connection error: %s", err)
        raise ConfigEntryNotReady(f"Failed to connect to City4U API: {err}") from err
    except Exception as err:
        _LOGGER.exception("Unknown error occurred during authentication: %s", err)
        raise ConfigEntryNotReady("Failed to connect to City4U API") from err

    async def async_update_data() -> list[dict[str, Any]]:
        """Update data via API."""
        try:
            # Check if token is still valid, re-auth if needed
            if not api.is_token_valid():
                await api.authenticate()

            return await api.fetch_water_data()
        except aiohttp.ClientResponseError as err:
            if err.status in (401, 403):
                raise ConfigEntryAuthFailed(
                    f"Session expired or invalid credentials: {err}"
                ) from err
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching water data: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unknown error occurred: %s", err)
            raise UpdateFailed(f"Error fetching data: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=SCAN_INTERVAL),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

        # If this is the last entry, unload services
        if not hass.data[DOMAIN]:
            await async_unload_services(hass)

    return unload_ok
