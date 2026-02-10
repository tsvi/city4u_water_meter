# City4U Water Consumption Integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![codecov][codecov-shield]][codecov]

![City4U Logo](https://city4u.co.il/PortalServicesSite/images/_logos/logo_0.jpg?v=20250126081117)

This custom component integrates City4U water consumption data with Home Assistant, allowing you to monitor your water consumption from your smart home dashboard.

## Installation

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tsvi&repository=city4u_water_meter&category=integration)

1. Click the button above, or manually add this repository to HACS as a custom repository.
2. Search for "City4U" in HACS and install it.
3. Restart Home Assistant.
4. Go to **Settings** → **Devices & Services** → **Add Integration**.
5. Search for "City4U" and follow the setup wizard.

### Manual Installation

1. Copy the `custom_components/city4u` folder to your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings** → **Devices & Services** → **Add Integration**.
4. Search for "City4U" and follow the setup wizard.

## Features

- Easy setup through the Home Assistant UI using config flow
- Secure authentication storage
- Handles delayed data entries properly using the `readingTime` field
- Automatic token refresh when needed
- Provides detailed information about your water consumption
- Import historical data for long-term statistics

## Configuration

During setup, you'll need to provide:

| Field | Description |
|-------|-------------|
| **Username** | Your City4U username (usually your Israeli ID number) |
| **Password** | Your City4U password (use your permanent password, not a temporary SMS code) |
| **Customer ID** | Your City4U customer ID (municipality code) |
| **Meter Number** | Your water meter number (defaults to username if not provided) |

## Sensor Attributes

The sensor provides the following attributes:

| Attribute | Description |
|-----------|-------------|
| `reading_time` | When the reading was taken by the water company |
| `last_polled` | When Home Assistant last fetched data from City4U |

## Services

This integration provides the following services:

### `city4u.force_update`

Force an immediate update of your water consumption data.

### `city4u.import_historical`

Import all available historical water consumption data into Home Assistant's long-term statistics. This allows you to view historical data in the energy dashboard and graphs.

## Troubleshooting

- **Authentication failures**: Ensure you're using your permanent City4U password, not a temporary SMS code.
- **No data available**: Check that your meter number is correct. It might take some time for new readings to appear.
- **Connection errors**: The City4U API might be temporarily unavailable. Try again later.
- **Graph showing wrong times**: The integration uses the `reading_time` from City4U to properly timestamp readings.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/tsvi/city4u_water_meter.svg?style=for-the-badge
[commits]: https://github.com/tsvi/city4u_water_meter/commits/master
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/tsvi/city4u_water_meter.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40tsvi-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/tsvi/city4u_water_meter.svg?style=for-the-badge
[releases]: https://github.com/tsvi/city4u_water_meter/releases
[user_profile]: https://github.com/tsvi
[codecov-shield]: https://img.shields.io/codecov/c/github/tsvi/city4u_water_meter?style=for-the-badge
[codecov]: https://codecov.io/gh/tsvi/city4u_water_meter
