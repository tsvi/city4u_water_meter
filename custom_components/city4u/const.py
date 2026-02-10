"""Constants for the City4U Water Consumption integration."""

# Domain
DOMAIN = "city4u"

# Configuration and options
CONF_CUSTOMER_ID = "customer_id"
CONF_METER_NUMBER = "meter_number"
CONF_MUNICIPALITY = "municipality"

# API URLs
LOGIN_URL = "https://city4u.co.il/WebApiUsersManagement/v1/UsrManagements/LoginUser"
DATA_URL_TEMPLATE = (
    "https://city4u.co.il/WebApiCity4u/v1/WaterConsumption/ReadingMoneWater/%s/%s"
)
CUSTOMERS_URL = "https://city4u.co.il/WebApi_portal/v1/Customers/Customer/allcustomers"

# Default values
DEFAULT_NAME = "City4U Water Consumption"
SCAN_INTERVAL = 3600  # 1 hour
TOKEN_EXPIRATION_MINUTES = 720  # 12 hours

# Icons
ICON = "mdi:water"

# Unit of measurement
UNIT_OF_MEASUREMENT = "m³"

# Reading attributes
ATTR_READING_TIME = "reading_time"
ATTR_LAST_POLLED = "last_polled"

# Attributes to exclude from extra_state_attributes (lowercase for case-insensitive matching)
# These are either shown as state, as custom attributes, or in device info
EXCLUDED_ATTRIBUTES_LOWER = {
    # Water data value (already shown as state)
    "totalwaterdatawithmultiplier",
    # Reading time (shown separately as reading_time attribute)
    "readingtime",
    # Device identifiers (shown in device info)
    "meternumber",
    "externalwatercardid",
    "siteexternalreferenceid",  # Used for configuration_url
}
