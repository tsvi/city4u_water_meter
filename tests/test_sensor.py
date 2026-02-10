"""Test City4U sensor component."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfVolume

from custom_components.city4u.const import DOMAIN
from custom_components.city4u.sensor import City4UWaterConsumptionSensor

from .conftest import SAMPLE_READING_ALL_FIELDS, SAMPLE_WATER_DATA


def test_sensor_name(sensor: City4UWaterConsumptionSensor) -> None:
    """Test sensor name."""
    assert sensor.name == "Water Consumption"


def test_sensor_unique_id(sensor: City4UWaterConsumptionSensor) -> None:
    """Test sensor unique ID."""
    assert sensor.unique_id == "city4u_123456_test_meter"


def test_sensor_device_class(sensor: City4UWaterConsumptionSensor) -> None:
    """Test sensor device class."""
    assert sensor.device_class == SensorDeviceClass.WATER


def test_sensor_state_class(sensor: City4UWaterConsumptionSensor) -> None:
    """Test sensor state class."""
    assert sensor.state_class == SensorStateClass.TOTAL_INCREASING


def test_sensor_unit_of_measurement(sensor: City4UWaterConsumptionSensor) -> None:
    """Test sensor unit of measurement."""
    assert sensor.native_unit_of_measurement == UnitOfVolume.CUBIC_METERS


def test_device_info(sensor: City4UWaterConsumptionSensor) -> None:
    """Test device info includes correct identifiers."""
    device_info = sensor.device_info
    assert device_info is not None
    assert device_info["name"] == "Water Meter test_meter"
    assert device_info["manufacturer"] == "City4U"
    assert any(DOMAIN in str(identifier) for identifier in device_info["identifiers"])


@pytest.mark.parametrize(
    ("data", "expected_value"),
    [
        (SAMPLE_WATER_DATA["valid_single"], 123.45),
        (SAMPLE_WATER_DATA["valid_multiple"], 120.0),
        (SAMPLE_WATER_DATA["invalid_value"], None),
        (SAMPLE_WATER_DATA["empty"], None),
        (SAMPLE_WATER_DATA["none"], None),
    ],
    ids=[
        "valid_single_reading",
        "valid_multiple_readings_uses_last",
        "invalid_value_returns_none",
        "empty_data_returns_none",
        "none_data_returns_none",
    ],
)
def test_native_value(
    sensor: City4UWaterConsumptionSensor,
    mock_coordinator: MagicMock,
    data: list[dict[str, Any]] | None,
    expected_value: float | None,
) -> None:
    """Test native value with various data states."""
    mock_coordinator.data = data
    assert sensor.native_value == expected_value


def test_reading_time_in_attributes(sensor: City4UWaterConsumptionSensor) -> None:
    """Test reading_time is in attributes."""
    _ = sensor.native_value
    attributes = sensor.extra_state_attributes
    assert "reading_time" in attributes


def test_additional_fields_included(sensor: City4UWaterConsumptionSensor) -> None:
    """Test additional fields are included in attributes."""
    _ = sensor.native_value
    attributes = sensor.extra_state_attributes
    assert attributes["additionalField"] == "test_value"


@pytest.mark.parametrize(
    "excluded_field",
    [
        "MeterNumber",
        "ExternalWaterCardId",
        "SiteExternalReferenceId",
        "totalWaterDataWithMultiplier",
        "readingTime",
    ],
    ids=[
        "MeterNumber_excluded",
        "ExternalWaterCardId_excluded",
        "SiteExternalReferenceId_excluded",
        "totalWaterDataWithMultiplier_excluded",
        "readingTime_excluded",
    ],
)
def test_excluded_attributes(
    sensor: City4UWaterConsumptionSensor,
    mock_coordinator: MagicMock,
    excluded_field: str,
) -> None:
    """Test that specific fields are excluded from attributes."""
    mock_coordinator.data = [SAMPLE_READING_ALL_FIELDS]
    _ = sensor.native_value
    attributes = sensor.extra_state_attributes
    assert excluded_field not in attributes


def test_valid_fields_included(
    sensor: City4UWaterConsumptionSensor,
    mock_coordinator: MagicMock,
) -> None:
    """Test that valid fields are included in attributes."""
    mock_coordinator.data = [
        {
            "totalWaterDataWithMultiplier": "123.45",
            "readingTime": "2025-01-01T12:00:00",
            "validField": "should_be_included",
            "anotherField": "also_included",
        }
    ]
    _ = sensor.native_value
    attributes = sensor.extra_state_attributes
    assert attributes["validField"] == "should_be_included"
    assert attributes["anotherField"] == "also_included"


def test_last_reset_returns_reading_time(sensor: City4UWaterConsumptionSensor) -> None:
    """Test that last_reset returns the reading time."""
    _ = sensor.native_value
    assert sensor.last_reset is not None


def test_last_reset_none_without_data(
    sensor: City4UWaterConsumptionSensor,
    mock_coordinator: MagicMock,
) -> None:
    """Test last_reset is None when no data available."""
    mock_coordinator.data = None
    _ = sensor.native_value
    assert sensor.last_reset is None
