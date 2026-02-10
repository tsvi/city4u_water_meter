# City4U Water Consumption for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
![GitHub License](https://img.shields.io/github/license/tsvi/city4u_water_meter?style=for-the-badge)
[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

<a href="https://www.buymeacoffee.com/tsvi" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 150px !important;" ></a>

![City4U Logo](logo.png)

A Home Assistant custom integration for fetching water consumption data from the City4U API. Monitor your water usage directly from your Home Assistant dashboard.

City4U is used by many municipalities in Israel to provide residents with access to their water consumption data and billing information.

## Supported Municipalities

This integration currently supports municipalities with verified water consumption data. The integration includes an easy-to-use dropdown selector to choose your municipality during setup.

For the complete list of supported municipalities, see [SUPPORTED_MUNICIPALITIES.md](SUPPORTED_MUNICIPALITIES.md).

**Note:** Not all municipalities that use City4U provide water consumption data through their portal. During setup, the integration will verify that your municipality supports water meter readings. If your municipality is not listed, you can help by running the verification script (see Contributing section below).

## Quick Install

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tsvi&repository=city4u_water_meter&category=integration)

1. Click the button above to add the repository to HACS
2. Install "City4U Water Consumption"
3. Restart Home Assistant
4. Add the integration via **Settings** → **Devices & Services** → **Add Integration** → Search for "City4U"
5. Select your municipality from the dropdown list
6. Enter your City4U credentials (ID number and password)

### Manual Installation

1. Copy the `custom_components/city4u` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Add Integration**
4. Search for "City4U" and follow the setup wizard

## Features

- **Easy Setup**: Interactive config flow with municipality dropdown selector
- **Verified Municipalities**: Growing list of municipalities with confirmed water consumption support
- **Automatic Updates**: Polls for new data every hour
- **Historical Data Import**: Import all available historical data for long-term statistics
- **Hebrew & English Support**: Proper display of municipality names in both languages  
- **Delayed Data Handling**: Correctly timestamps readings based on actual meter reading time
- **Secure Credentials**: All credentials stored securely in Home Assistant

## Configuration

During setup, you'll need to provide:

| Field | Description |
|-------|-------------|
| **Municipality** | Select your municipality from the dropdown list (shows both Hebrew and English names) |
| **Username** | Your City4U username (usually your Israeli ID number / Teudat Zehut) |
| **Password** | Your City4U password (use your permanent password, not a temporary SMS code) |
| **Meter Number** | Your water meter number (optional - defaults to username if not provided) |

The integration will automatically verify that your chosen municipality provides water consumption data and that your credentials are valid.

## Requirements

- Home Assistant 2024.1 or newer
- A City4U account with a municipality that provides water consumption data
- Your Israeli ID number (username)
- Your permanent City4U password (not a temporary SMS code)

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
- **Municipality not listed**: See the Contributing section below to help verify your municipality.

## Alternative: Using Home Assistant REST Sensor

If you prefer not to use this custom integration, you can use [Home Assistant's built-in REST sensor](https://www.home-assistant.io/integrations/sensor.rest/) to fetch water consumption data directly.

Add the following to your `configuration.yaml`:

```yaml
# REST sensor for water consumption data that fetches its own token
sensor:
  - platform: rest
    name: "Water Auth Token"
    unique_id: "water_auth_token"
    value_template: "{{ value_json.UserToken }}"
    resource: https://city4u.co.il/WebApiUsersManagement/v1/UsrManagements/LoginUser
    method: POST
    headers:
      content-type: "application/x-www-form-urlencoded"
    payload: !secret city4u_auth_payload
    scan_interval: 43200 # 12 hours

  # The water consumption sensor using the dynamic token
  - platform: rest
    name: Water Consumption
    unique_id: "city4u-water-consumption"
    resource: !secret city4u_mone_url
    headers:
      customerID: !secret city4u_municipality
      CustomerSite: !secret city4u_municipality
      token: "{{ states('sensor.water_auth_token') }}"
      UserName: !secret city4u_user_name
    value_template: "{{ value_json[-1]['totalWaterDataWithMultiplier'] }}"
    unit_of_measurement: "m³"
    scan_interval: 3600
    json_attributes:
      - readingTime
      - meterNumber
```

You'll need to add the following to your `secrets.yaml`:

```yaml
city4u_auth_payload: "ServiceName=LoginUser&UserName=<ID number>&Password=<password>&token=undefined&customerID=<City ID>&CustomerSite=<City Site>"
city4u_municipality: <City ID>
city4u_user_name: <ID number>
city4u_password: <Password>
city4u_mone_url: https://city4u.co.il/WebApiCity4u/v1/WaterConsumption/ReadingMoneWater/<City ID>/<ID number>
```

**Note:** The `ID Number` is usually your Israeli ID number (Teudat Zehut). The `City ID` and `City Site` are typically the same value (your municipality's customer ID).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Verifying New Municipalities

If your municipality uses City4U but isn't in the verified list, you can help verify it:

```bash
# From the project directory
python3 scripts/update_municipalities.py
```

This script will check all City4U municipalities for water consumption support and update the list automatically. Please submit a PR with the updated files if new municipalities are found!

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
