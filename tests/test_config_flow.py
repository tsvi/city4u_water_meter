"""Test the City4U config flow."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.city4u.config_flow import CannotConnect, InvalidAuth
from custom_components.city4u.const import (
    CONF_CUSTOMER_ID,
    CONF_METER_NUMBER,
    CONF_MUNICIPALITY,
    DOMAIN,
)

# Test input data
VALID_USER_INPUT = {
    CONF_USERNAME: "test_user",
    CONF_PASSWORD: "test_password",
    CONF_MUNICIPALITY: "onecity",
    CONF_METER_NUMBER: "test_meter",
}


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_user_form_shown(hass: HomeAssistant) -> None:
    """Test we get the user form when no input is provided."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"


@pytest.mark.usefixtures("mock_validate_input", "enable_custom_integrations")
async def test_create_entry_success(hass: HomeAssistant) -> None:
    """Test we create an entry with valid input."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=VALID_USER_INPUT,
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Water Meter test_meter"
    # Municipality should be converted to customer_id in stored data
    assert result["data"][CONF_CUSTOMER_ID] == "999999"
    assert result["data"][CONF_USERNAME] == "test_user"
    assert result["data"][CONF_PASSWORD] == "test_password"
    assert result["data"][CONF_METER_NUMBER] == "test_meter"
    assert CONF_MUNICIPALITY not in result["data"]


@pytest.mark.parametrize(
    ("exception", "expected_error"),
    [
        (CannotConnect, "cannot_connect"),
        (InvalidAuth, "invalid_auth"),
        (Exception("Unexpected"), "unknown"),
    ],
    ids=["cannot_connect", "invalid_auth", "unknown_error"],
)
@pytest.mark.usefixtures("enable_custom_integrations")
async def test_config_flow_errors(
    hass: HomeAssistant,
    mock_validate_input: AsyncMock,
    exception: Exception,
    expected_error: str,
) -> None:
    """Test we handle various errors correctly."""
    mock_validate_input.side_effect = exception

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=VALID_USER_INPUT,
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": expected_error}


@pytest.mark.usefixtures("mock_validate_input", "enable_custom_integrations")
async def test_meter_number_defaults_to_username(hass: HomeAssistant) -> None:
    """Test meter number defaults to username when empty."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    test_data = {
        CONF_USERNAME: "test_user",
        CONF_PASSWORD: "test_password",
        CONF_MUNICIPALITY: "onecity",
        CONF_METER_NUMBER: "",
    }

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=test_data,
    )

    assert result["data"][CONF_METER_NUMBER] == "test_user"
