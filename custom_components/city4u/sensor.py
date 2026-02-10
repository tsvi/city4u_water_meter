"""Sensor platform for City4U water consumption integration."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util import dt as dt_util

from .api import City4UApiClient
from .const import (
    ATTR_LAST_POLLED,
    ATTR_READING_TIME,
    DOMAIN,
    EXCLUDED_ATTRIBUTES_LOWER,
    ICON,
)
from .municipalities import get_municipality_by_id

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up City4U sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]

    async_add_entities(
        [
            City4UWaterConsumptionSensor(
                coordinator=coordinator,
                api=api,
            )
        ]
    )


class City4UWaterConsumptionSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a City4U water consumption sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_icon = ICON

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        api: City4UApiClient,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._api = api
        self._last_reading_time: datetime | None = None
        self._last_polled: datetime | None = None

        # Entity properties
        meter_number = api.meter_number
        customer_id = api.customer_id
        self._attr_unique_id = f"{DOMAIN}_{customer_id}_{meter_number}"
        self._attr_name = "Water Consumption"

        # Extract device identifiers from initial data
        api_meter_number = None
        property_id = None  # ExternalWaterCardId (זיהוי נכס)
        site_id = None  # SiteExternalReferenceId (municipality portal ID)

        if coordinator.data and isinstance(coordinator.data, list) and coordinator.data:
            first_reading = coordinator.data[0]
            api_meter_number = first_reading.get("MeterNumber") or first_reading.get(
                "meterNumber"
            )
            property_id = first_reading.get("ExternalWaterCardId") or first_reading.get(
                "externalWaterCardId"
            )
            site_id = first_reading.get("SiteExternalReferenceId") or first_reading.get(
                "siteExternalReferenceId"
            )

        # Build identifiers set - primary identifier plus property ID if available
        identifiers: set[tuple[str, str]] = {(DOMAIN, f"{customer_id}_{meter_number}")}
        if property_id:
            identifiers.add((DOMAIN, f"property_{property_id}"))

        # Build configuration URL - use municipality portal if site ID available
        if site_id:
            config_url = f"https://city4u.co.il/PortalServicesSite/_portal/{site_id}"
        else:
            config_url = "https://city4u.co.il"

        # Get municipality information
        municipality = get_municipality_by_id(int(customer_id))
        municipality_name = municipality.name_he if municipality else "Unknown"

        # Build device info with identifiers from API
        self._attr_device_info = DeviceInfo(
            identifiers=identifiers,
            name=f"Water Meter {meter_number} - {municipality_name}",
            manufacturer="City4U",
            model=f"{municipality_name} (ID: {customer_id})",
            configuration_url=config_url,
            serial_number=str(api_meter_number) if api_meter_number else None,
        )

    def _parse_reading_time(self, reading_time_str: str) -> datetime | None:
        """Parse reading time string to datetime with timezone."""
        if not reading_time_str:
            return None
        try:
            # Parse the date format from City4U API (assume Israel timezone)
            naive_dt = datetime.strptime(reading_time_str, "%Y-%m-%dT%H:%M:%S")
            # Assume Israel timezone for readings
            return dt_util.as_utc(
                naive_dt.replace(tzinfo=dt_util.get_time_zone("Asia/Jerusalem"))
            )
        except ValueError:
            _LOGGER.warning("Failed to parse reading time: %s", reading_time_str)
            return None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._last_polled = dt_util.utcnow()
        super()._handle_coordinator_update()

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        # The data is a list of readings, with the latest one at the end
        try:
            if isinstance(self.coordinator.data, list) and self.coordinator.data:
                latest_reading = self.coordinator.data[-1]
                reading_value = latest_reading.get("totalWaterDataWithMultiplier")

                # Parse reading time
                reading_time_str = latest_reading.get("readingTime")
                if reading_time_str:
                    self._last_reading_time = self._parse_reading_time(reading_time_str)

                if reading_value is not None:
                    try:
                        return float(reading_value)
                    except (ValueError, TypeError):
                        _LOGGER.warning(
                            "Invalid water reading value: %s", reading_value
                        )

            return None
        except (KeyError, IndexError) as err:
            _LOGGER.error("Error extracting water data: %s", err)
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attributes: dict[str, Any] = {}

        # Add reading time if available
        if self._last_reading_time:
            attributes[ATTR_READING_TIME] = self._last_reading_time.isoformat()

        # Add last polled time
        if self._last_polled:
            attributes[ATTR_LAST_POLLED] = self._last_polled.isoformat()

        # Add other attributes from the data if available (excluding unwanted ones)
        if (
            self.coordinator.data
            and isinstance(self.coordinator.data, list)
            and self.coordinator.data
        ):
            latest_reading = self.coordinator.data[-1]

            # Add additional attributes that might be useful (case-insensitive filtering)
            for key, value in latest_reading.items():
                if key.lower() not in EXCLUDED_ATTRIBUTES_LOWER:
                    attributes[key] = value

        return attributes
