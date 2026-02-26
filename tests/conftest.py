"""Fixtures for City4U tests.

Pylint warnings disabled for this file:
- redefined-outer-name: Pytest fixtures intentionally shadow outer names
- unused-argument: Fixtures used for dependency injection appear unused
"""
# pylint: disable=redefined-outer-name,unused-argument

import json
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.city4u.api import City4UApiClient, City4UCredentials
from custom_components.city4u.const import CONF_CUSTOMER_ID, CONF_METER_NUMBER, DOMAIN
from custom_components.city4u.sensor import City4UWaterConsumptionSensor


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Create a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id="city4u_123456_test_meter",
        data={
            CONF_USERNAME: "test_user",
            CONF_PASSWORD: "test_password",
            CONF_CUSTOMER_ID: "123456",
            CONF_METER_NUMBER: "test_meter",
        },
        entry_id="test_entry_id",
    )


@pytest.fixture
def mock_api() -> MagicMock:
    """Create a mock API client."""
    api = MagicMock()
    api.authenticate = AsyncMock()
    api.fetch_water_data = AsyncMock(
        return_value=[
            {
                "totalWaterDataWithMultiplier": 123.45,
                "readingTime": "2025-01-01T12:00:00",
                "MeterNumber": "test_meter",
                "ExternalWaterCardId": "12345",
                "SiteExternalReferenceId": "67890",
            }
        ]
    )
    api.fetch_all_historical_data = AsyncMock(return_value=[])
    api.is_token_valid = MagicMock(return_value=True)
    api.meter_number = "test_meter"
    api.customer_id = "123456"
    return api


@pytest.fixture
def mock_coordinator(mock_api: MagicMock) -> MagicMock:
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = [
        {
            "totalWaterDataWithMultiplier": "123.45",
            "readingTime": "2025-01-01T12:00:00",
            "MeterNumber": "test_meter",
            "ExternalWaterCardId": "12345",
            "SiteExternalReferenceId": "67890",
            "additionalField": "test_value",
        }
    ]
    coordinator.async_config_entry_first_refresh = AsyncMock()
    coordinator.async_request_refresh = AsyncMock()
    coordinator.last_update_success = True
    return coordinator


@pytest.fixture
def mock_session() -> MagicMock:
    """Create a mock aiohttp ClientSession."""
    session = MagicMock()
    return session


@pytest.fixture
def bypass_setup_fixture() -> Generator[None, None, None]:
    """Bypass the actual setup."""
    with patch(
        "custom_components.city4u.async_get_clientsession",
        return_value=MagicMock(),
    ):
        yield


# Sample data fixtures for parametrized tests
SAMPLE_WATER_DATA = {
    "valid_single": [
        {
            "totalWaterDataWithMultiplier": 123.45,
            "readingTime": "2025-01-01T12:00:00",
            "MeterNumber": "test_meter",
        }
    ],
    "valid_multiple": [
        {
            "totalWaterDataWithMultiplier": 100.0,
            "readingTime": "2025-01-01T10:00:00",
        },
        {
            "totalWaterDataWithMultiplier": 110.0,
            "readingTime": "2025-01-01T11:00:00",
        },
        {
            "totalWaterDataWithMultiplier": 120.0,
            "readingTime": "2025-01-01T12:00:00",
        },
    ],
    "invalid_value": [
        {
            "totalWaterDataWithMultiplier": "invalid",
            "readingTime": "2025-01-01T12:00:00",
        }
    ],
    "empty": [],
    "none": None,
}

# Sample reading with all standard fields for attribute testing
SAMPLE_READING_ALL_FIELDS = {
    "totalWaterDataWithMultiplier": "123.45",
    "readingTime": "2025-01-01T12:00:00",
    "MeterNumber": "test_meter",
    "ExternalWaterCardId": "12345",
    "SiteExternalReferenceId": "67890",
    "validField": "should_be_included",
}


# Fixtures moved from individual test files


@pytest.fixture
def sensor(
    mock_coordinator: MagicMock, mock_api: MagicMock
) -> City4UWaterConsumptionSensor:
    """Create a City4U sensor."""
    return City4UWaterConsumptionSensor(
        coordinator=mock_coordinator,
        api=mock_api,
    )


@pytest.fixture
def delayed_data_sensor(
    mock_coordinator: MagicMock, mock_api: MagicMock
) -> City4UWaterConsumptionSensor:
    """Create a City4U sensor for delayed data tests."""
    mock_coordinator.data = None  # Start with no data
    return City4UWaterConsumptionSensor(
        coordinator=mock_coordinator,
        api=mock_api,
    )


@pytest.fixture
def city4u_client(mock_session: MagicMock) -> City4UApiClient:
    """Create a City4U API client for testing."""
    credentials = City4UCredentials(
        username="test_user",
        password="test_password",
        customer_id="123456",
        meter_number="test_meter",
    )
    return City4UApiClient(credentials=credentials, session=mock_session)


@pytest.fixture
def mock_validate_input() -> Generator[AsyncMock, None, None]:
    """Mock the validate_input function."""
    with patch(
        "custom_components.city4u.config_flow.validate_input",
        new_callable=AsyncMock,
        return_value={"title": "Water Meter test_meter"},
    ) as mock:
        yield mock


def create_mock_response(
    status: int,
    json_data: dict[str, Any] | list[dict[str, Any]] | None = None,
    text: str = "",
) -> MagicMock:
    """Create a mock aiohttp response with proper async methods."""
    mock_response = MagicMock()
    mock_response.status = status
    # If json_data is provided, serialize it to text so response.text() returns valid JSON
    response_text = json.dumps(json_data) if json_data is not None else text
    mock_response.json = AsyncMock(return_value=json_data)
    mock_response.text = AsyncMock(return_value=response_text)
    return mock_response
