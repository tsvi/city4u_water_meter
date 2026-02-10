"""Services for the City4U integration."""

import logging
from datetime import datetime

import voluptuous as vol
from homeassistant.components.recorder.models import (
    StatisticData,
    StatisticMeanType,
    StatisticMetaData,
)
from homeassistant.components.recorder.statistics import async_add_external_statistics
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Define service schemas
FORCE_UPDATE_SCHEMA = vol.Schema({})
IMPORT_HISTORICAL_SCHEMA = vol.Schema({})


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up City4U services."""

    async def handle_force_update(_call: ServiceCall) -> None:
        """Handle the force update service call."""
        if DOMAIN not in hass.data:
            _LOGGER.error("City4U integration not set up")
            return

        for entry_id, entry_data in hass.data[DOMAIN].items():
            coordinator = entry_data.get("coordinator")
            if coordinator:
                await coordinator.async_refresh()
                _LOGGER.debug("Forced update for City4U entry %s", entry_id)

    async def handle_import_historical(_call: ServiceCall) -> None:
        """Handle the import historical data service call."""
        if DOMAIN not in hass.data:
            _LOGGER.error("City4U integration not set up")
            return

        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data.get("api")
            if not api:
                continue

            try:
                # Fetch all historical data
                historical_data = await api.fetch_all_historical_data()

                if not historical_data:
                    _LOGGER.warning(
                        "No historical data available for entry %s", entry_id
                    )
                    continue

                # Convert to statistics format
                statistic_id = f"{DOMAIN}:water_consumption_{api.meter_number}"

                # Build statistics data from historical readings
                statistics: list[StatisticData] = []

                for reading in historical_data:
                    reading_time_str = reading.get("readingTime")
                    reading_value = reading.get("totalWaterDataWithMultiplier")

                    if not reading_time_str or reading_value is None:
                        continue

                    try:
                        # Parse reading time (assume Israel timezone)
                        naive_dt = datetime.strptime(
                            reading_time_str, "%Y-%m-%dT%H:%M:%S"
                        )
                        reading_time = dt_util.as_utc(
                            naive_dt.replace(
                                tzinfo=dt_util.get_time_zone("Asia/Jerusalem")
                            )
                        )

                        value = float(reading_value)

                        statistics.append(
                            StatisticData(
                                start=reading_time,
                                state=value,
                                sum=value,
                            )
                        )
                    except (ValueError, TypeError) as err:
                        _LOGGER.warning(
                            "Failed to parse reading: %s, error: %s", reading, err
                        )
                        continue

                if statistics:
                    # Sort by timestamp
                    statistics.sort(key=lambda x: x["start"])

                    metadata = StatisticMetaData(
                        has_mean=False,
                        has_sum=True,
                        mean_type=StatisticMeanType.NONE,
                        name=f"City4U Water Consumption ({api.meter_number})",
                        source=DOMAIN,
                        statistic_id=statistic_id,
                        unit_class=None,
                        unit_of_measurement=UnitOfVolume.CUBIC_METERS,
                    )

                    async_add_external_statistics(hass, metadata, statistics)
                    _LOGGER.info(
                        "Imported %d historical readings for meter %s",
                        len(statistics),
                        api.meter_number,
                    )
                else:
                    _LOGGER.warning(
                        "No valid readings to import for entry %s", entry_id
                    )

            except Exception as err:  # pylint: disable=broad-exception-caught
                _LOGGER.error(
                    "Failed to import historical data for entry %s: %s", entry_id, err
                )

    # Register services
    hass.services.async_register(
        DOMAIN, "force_update", handle_force_update, schema=FORCE_UPDATE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        "import_historical",
        handle_import_historical,
        schema=IMPORT_HISTORICAL_SCHEMA,
    )


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload City4U services."""
    if hass.services.has_service(DOMAIN, "force_update"):
        hass.services.async_remove(DOMAIN, "force_update")
    if hass.services.has_service(DOMAIN, "import_historical"):
        hass.services.async_remove(DOMAIN, "import_historical")
