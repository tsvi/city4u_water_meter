"""Test handling of delayed data entries in City4U integration."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from custom_components.city4u.sensor import City4UWaterConsumptionSensor


@pytest.mark.parametrize(
    ("data", "expected_value", "description"),
    [
        (None, None, "no data initially"),
        (
            [
                {
                    "totalWaterDataWithMultiplier": "100.0",
                    "readingTime": "2025-01-01T12:00:00",
                }
            ],
            100.0,
            "single entry",
        ),
        (
            [
                {
                    "totalWaterDataWithMultiplier": "100.0",
                    "readingTime": "2025-01-01T12:00:00",
                },
                {
                    "totalWaterDataWithMultiplier": "90.0",
                    "readingTime": "2025-01-01T10:00:00",
                },
                {
                    "totalWaterDataWithMultiplier": "120.0",
                    "readingTime": "2025-01-02T12:00:00",
                },
            ],
            120.0,
            "multiple entries with backdated - uses last entry",
        ),
    ],
    ids=["no_data", "single_entry", "multiple_with_backdated"],
)
def test_delayed_data_values(
    delayed_data_sensor: City4UWaterConsumptionSensor,
    mock_coordinator: MagicMock,
    data: list[dict[str, Any]] | None,
    expected_value: float | None,
    description: str,
) -> None:
    """Test sensor handles delayed data entries correctly."""
    mock_coordinator.data = data
    assert delayed_data_sensor.native_value == expected_value, description


@pytest.mark.parametrize(
    "invalid_reading_time",
    [
        "Invalid Date Format",
        "",
        "not-a-date",
        "2025/01/01",  # Wrong format
    ],
    ids=["garbage_string", "empty_string", "not_a_date", "wrong_format"],
)
def test_invalid_reading_time(
    delayed_data_sensor: City4UWaterConsumptionSensor,
    mock_coordinator: MagicMock,
    invalid_reading_time: str,
) -> None:
    """Test handling of invalid reading time formats."""
    mock_coordinator.data = [
        {
            "totalWaterDataWithMultiplier": "100.0",
            "readingTime": invalid_reading_time,
            "validField": "test_value",
        }
    ]

    # Value should still be parsed
    assert delayed_data_sensor.native_value == 100.0
    attributes = delayed_data_sensor.extra_state_attributes
    # reading_time should not be in attributes if invalid
    assert "reading_time" not in attributes
    # Other valid fields should still be included
    assert attributes["validField"] == "test_value"


@pytest.mark.parametrize(
    ("readings", "expected_value", "expected_type"),
    [
        (
            [
                {
                    "totalWaterDataWithMultiplier": "100.0",
                    "readingTime": "2025-01-01T12:00:00",
                    "readingType": "Regular",
                },
                {
                    "totalWaterDataWithMultiplier": "110.0",
                    "readingTime": "2025-01-01T12:00:00",
                    "readingType": "Adjustment",
                },
            ],
            110.0,
            "Adjustment",
        ),
        (
            [
                {
                    "totalWaterDataWithMultiplier": "50.0",
                    "readingTime": "2025-01-01T12:00:00",
                    "readingType": "Estimated",
                },
                {
                    "totalWaterDataWithMultiplier": "55.0",
                    "readingTime": "2025-01-01T12:00:00",
                    "readingType": "Actual",
                },
            ],
            55.0,
            "Actual",
        ),
    ],
    ids=["regular_then_adjustment", "estimated_then_actual"],
)
def test_same_timestamp_uses_last(
    delayed_data_sensor: City4UWaterConsumptionSensor,
    mock_coordinator: MagicMock,
    readings: list[dict[str, Any]],
    expected_value: float,
    expected_type: str,
) -> None:
    """Test that last entry is used when timestamps are identical."""
    mock_coordinator.data = readings

    assert delayed_data_sensor.native_value == expected_value
    attributes = delayed_data_sensor.extra_state_attributes
    assert attributes["readingType"] == expected_type


def test_reading_time_in_attributes_after_update(
    delayed_data_sensor: City4UWaterConsumptionSensor,
    mock_coordinator: MagicMock,
) -> None:
    """Test that reading_time appears in attributes after valid data."""
    # Start with no data
    mock_coordinator.data = None
    assert delayed_data_sensor.native_value is None

    # Update with valid data
    mock_coordinator.data = [
        {
            "totalWaterDataWithMultiplier": "100.0",
            "readingTime": "2025-01-01T12:00:00",
        }
    ]

    assert delayed_data_sensor.native_value == 100.0
    attributes = delayed_data_sensor.extra_state_attributes
    assert "reading_time" in attributes
