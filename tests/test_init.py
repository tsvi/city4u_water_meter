"""Test City4U integration setup."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.city4u.const import DOMAIN


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_setup_entry_success(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api: MagicMock,
) -> None:
    """Test successful entry setup."""
    mock_config_entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.city4u.async_get_clientsession",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.city4u.City4UApiClient",
            return_value=mock_api,
        ),
        patch(
            "custom_components.city4u.DataUpdateCoordinator"
        ) as mock_coordinator_class,
    ):
        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator.data = mock_api.fetch_water_data.return_value
        mock_coordinator_class.return_value = mock_coordinator

        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state is ConfigEntryState.LOADED
        mock_api.authenticate.assert_called_once()
        assert mock_config_entry.entry_id in hass.data[DOMAIN]


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_unload_entry_success(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api: MagicMock,
) -> None:
    """Test successful entry unload."""
    mock_config_entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.city4u.async_get_clientsession",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.city4u.City4UApiClient",
            return_value=mock_api,
        ),
        patch(
            "custom_components.city4u.DataUpdateCoordinator"
        ) as mock_coordinator_class,
    ):
        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator.data = mock_api.fetch_water_data.return_value
        mock_coordinator_class.return_value = mock_coordinator

        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state == ConfigEntryState.LOADED

        await hass.config_entries.async_unload(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state == ConfigEntryState.NOT_LOADED
        assert mock_config_entry.entry_id not in hass.data[DOMAIN]
