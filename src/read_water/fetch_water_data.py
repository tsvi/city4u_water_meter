"""Fetch water consumption data from City4U API and save to JSON file."""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import requests
import urllib3

_LOGGER = logging.getLogger(__name__)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- API URLs ---
LOGIN_URL = "https://city4u.co.il/WebApiUsersManagement/v1/UsrManagements/LoginUser"
DATA_URL_TEMPLATE = (
    "https://city4u.co.il/WebApiCity4u/v1/WaterConsumption/ReadingMoneWater/%s/%s"
)
CUSTOMERS_URL = "https://city4u.co.il/WebApi_portal/v1/Customers/Customer/allcustomers"

# Default configuration file location
CONFIG_FILE = os.path.expanduser("~/.config/water_consumption/config.json")


def get_token(username, password, customer_id):
    """Get authentication token from City4U API.

    Args:
        username (str): City4U username
        password (str): City4U password
        customer_id (str): Customer ID number

    Returns:
        str or None: The authentication token if successful, None otherwise
    """
    session = requests.Session()  # Use a simple session for now

    # Use the exact payload format from the browser trace
    payload = {
        "ServiceName": "LoginUser",
        "UserName": username,
        "Password": password,
        "token": "undefined",
        "customerID": customer_id,
        "CustomerSite": customer_id,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        _LOGGER.info("Attempting login with correct form-encoded payload...")
        response = session.post(
            LOGIN_URL, data=payload, headers=headers, verify=False, timeout=30
        )
        _LOGGER.debug("Login response status: %s", response.status_code)
        _LOGGER.debug("Login response headers: %s", dict(response.headers))
        _LOGGER.debug("Login response cookies: %s", dict(response.cookies))

        if response.status_code != 200:
            _LOGGER.error(
                "Login failed with status %s: %s",
                response.status_code,
                response.text[:500],
            )
            return None

        try:
            data = response.json()
            user_token = data.get("UserToken")
            if user_token:
                _LOGGER.info("✓ Successfully extracted UserToken: %s", user_token)
                return user_token

            _LOGGER.error("No UserToken found in response")
            return None

        except json.JSONDecodeError as e:
            _LOGGER.error("Failed to parse login response: %s", e)
            return None

    except requests.RequestException as e:
        _LOGGER.error("Login request failed: %s", e)
        return None


def fetch_water_data(token, username, customer_id, meter_number):
    """Fetch water consumption data from City4U API.

    Args:
        token (str): Authentication token
        username (str): City4U username
        customer_id (str): Customer ID number
        meter_number (str): Water meter number

    Returns:
        dict or None: Water consumption data if successful, None otherwise
    """
    headers = {
        "customerID": customer_id,
        "CustomerSite": customer_id,
        "UserName": username,
        "token": token,
    }

    data_url = DATA_URL_TEMPLATE % (customer_id, meter_number)
    session = requests.Session()  # Use a simple session for now

    try:
        _LOGGER.info("Fetching water consumption data...")
        response = session.get(data_url, headers=headers, verify=False, timeout=30)
        _LOGGER.debug("Data response status: %s", response.status_code)
        _LOGGER.debug("Data response headers: %s", dict(response.headers))

        if response.status_code != 200:
            _LOGGER.error("Data fetch failed with status %s", response.status_code)
            _LOGGER.error("Response: %s...", response.text[:500])
            return None

        try:
            return response.json()
        except json.JSONDecodeError:
            _LOGGER.error("Data response is not JSON")
            _LOGGER.error("Data response text: %s...", response.text[:500])
            return None

    except requests.RequestException as e:
        _LOGGER.error("Data fetch failed: %s", e)
        return None


def save_water_data(data, output_file):
    """Save water consumption data to JSON file with timestamp.

    Args:
        data (dict): Water consumption data to save
        output_file (str): Path to output JSON file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Add timestamp to the data
        output_data = {"timestamp": datetime.now().isoformat(), "data": data}

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        _LOGGER.info("✓ Water consumption data saved to %s", output_file)
        return True
    except (IOError, OSError) as e:
        _LOGGER.error("✗ Failed to save data to file: %s", e)
        return False


def format_hebrew_for_display(text):
    """Format Hebrew text for proper display in terminal environments.

    Args:
        text (str): The Hebrew text to format

    Returns:
        str: Formatted text for terminal display
    """
    if not text or text == "Unknown":
        return text

    # Reverse the string for proper RTL display in terminal
    reversed_text = text[::-1]

    # Apply RTL formatting with Unicode control characters:
    # U+202E (RLO): Right-to-Left Override - forces RTL rendering
    # U+202C (PDF): Pop Directional Formatting - ends the override
    return f"\u202e{reversed_text}\u202c"


def get_customer_list():
    """Fetch the list of customers from the City4U API.

    Returns:
        list or None: List of customers if successful, None otherwise
    """
    try:
        _LOGGER.info("Fetching customer list...")
        response = requests.get(CUSTOMERS_URL, verify=False, timeout=30)

        if response.status_code != 200:
            _LOGGER.error("Customer fetch failed with status %s", response.status_code)
            return None

        try:
            customers = response.json()
            return customers
        except json.JSONDecodeError:
            _LOGGER.error("Customer data response is not valid JSON")
            _LOGGER.error("Response text: %s...", response.text[:500])
            return None

    except requests.RequestException as e:
        _LOGGER.error("Failed to fetch customer list: %s", e)
        return None


def select_customer():
    """Let the user select their customer (city) from the list.

    Returns:
        int or None: Selected customer ID if successful, None otherwise
    """
    customers = get_customer_list()

    if not customers:
        _LOGGER.error("Could not fetch customer list. Setup cannot continue.")
        return None

    print("\nAvailable cities:")
    # Sort by Hebrew name for easier selection
    sorted_customers = sorted(customers, key=lambda x: x.get("CUSTOMER_NAME_HE", ""))

    # Print header with explanation
    print("Num.  City Name")
    print("---------------")

    # Print all cities with their actual City ID, which is the reliable identifier
    for idx, customer in enumerate(sorted_customers, 1):
        customer_id = int(customer.get("CUSTOMER_ID", 0))
        hebrew_name = customer.get("CUSTOMER_NAME_HE", "Unknown")

        # Format Hebrew text for proper display
        hebrew_display = format_hebrew_for_display(hebrew_name)

        # Print a simple numbered list with the customer ID which is the reliable identifier
        print(f"{idx:3d}.  {hebrew_display}")

    while True:
        try:
            selection = int(
                input("\nPlease enter the ID number of your city from the list above: ")
            )
            if 1 <= selection <= len(sorted_customers):
                selected_customer = sorted_customers[selection - 1]
                customer_id = int(selected_customer.get("CUSTOMER_ID", 0))
                hebrew_name = selected_customer.get("CUSTOMER_NAME_HE", "Unknown")

                # Format Hebrew text for proper display in confirmation message
                hebrew_display = format_hebrew_for_display(hebrew_name)

                print(f"\nSelected city ID: {customer_id} ({hebrew_display})")
                return customer_id

            print(f"Please enter a number between 1 and {len(sorted_customers)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nSelection cancelled")
            return None


def create_config_file(config):
    """Create a configuration file with the provided settings.

    Args:
        config (dict): Configuration to save

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        config_dir = os.path.dirname(CONFIG_FILE)
        Path(config_dir).mkdir(parents=True, exist_ok=True)

        # Write the configuration
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        _LOGGER.info("Configuration saved to %s", CONFIG_FILE)
        return True
    except (IOError, OSError) as e:
        _LOGGER.error("Failed to create configuration file: %s", e)
        return False


def setup_config():
    """Walk through the setup process to create a configuration file.

    Returns:
        dict or None: Configuration if successful, None otherwise
    """
    print("\n=== City4U Water Consumption Setup ===")
    print("Let's configure your City4U water consumption account.")

    # Get username and password
    username = input("\nEnter your City4U username: ")
    password = input("Enter your City4U password: ")

    # Get customer ID from list
    print("\nFetching available cities...")
    customer_id = select_customer()

    if not customer_id:
        print("Could not complete setup. Please try again later.")
        return None

    # Ask for meter number or use username as default
    meter_number = input(
        f"\nEnter your meter number (press Enter to use {username} as default): "
    )
    if not meter_number:
        meter_number = username

    # Ask for default output file
    default_output = "water_consumption_data.json"
    output_file = input(
        f"\nEnter path for output file (press Enter to use {default_output} as default): "
    )
    if not output_file:
        output_file = default_output

    # Create configuration
    config = {
        "username": username,
        "password": password,
        "customer_id": customer_id,
        "meter_number": meter_number,
        "output_file": output_file,
    }

    # Save configuration
    if create_config_file(config):
        print(f"\nSetup complete! Configuration saved to {CONFIG_FILE}")
        return config

    print("\nFailed to save configuration. You'll need to provide credentials manually.")
    return None


def load_config():
    """Load configuration from file or run setup if it doesn't exist.

    Returns:
        dict or None: Configuration if successful, None otherwise
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            _LOGGER.info("Configuration loaded from %s", CONFIG_FILE)
            return config
        except (IOError, json.JSONDecodeError) as e:
            _LOGGER.error("Failed to load configuration: %s", e)
            return None

    _LOGGER.info("No configuration file found. Starting setup...")
    return setup_config()


def parse_arguments():
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Fetch water consumption data from City4U API"
    )
    parser.add_argument(
        "--username", help="Your City4U username (overrides config file)"
    )
    parser.add_argument(
        "--password", help="Your City4U password (overrides config file)"
    )
    parser.add_argument(
        "--customer-id", help="Your City4U customer ID (overrides config file)"
    )
    parser.add_argument(
        "--meter-number",
        help="Your meter number (defaults to username if not provided)",
    )
    parser.add_argument(
        "--output",
        help="Output JSON file path (default: water_consumption_data.json or from config)",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run the setup process to create/update configuration",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def main():
    """Main function to fetch and save water consumption data.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    args = parse_arguments()
    exit_code = 1  # Default to error state

    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)

    # Get configuration (from setup or existing file)
    config = setup_config() if args.setup else load_config()
    if not config:
        _LOGGER.error("Failed to load or create configuration")
        return exit_code

    # Command-line arguments override config file
    username = args.username or config.get("username")
    password = args.password or config.get("password")
    customer_id = args.customer_id or config.get("customer_id")
    meter_number = args.meter_number or config.get("meter_number") or username
    output_file = args.output or config.get(
        "output_file", "water_consumption_data.json"
    )

    # Validate required parameters
    if not all([username, password, customer_id]):
        _LOGGER.error("Missing required parameters (username, password, customer_id)")
        return exit_code

    # Authentication and data retrieval process
    try:
        # Get token
        token = get_token(username, password, str(customer_id))
        if not token:
            _LOGGER.error("Failed to obtain authentication token")
            return exit_code

        _LOGGER.info("Successfully obtained token: %s", token)

        # Fetch water data
        data = fetch_water_data(token, username, str(customer_id), meter_number)
        if not data:
            _LOGGER.error("Failed to retrieve water consumption data")
            return exit_code

        _LOGGER.info("Successfully fetched water consumption data")

        # Save data
        if save_water_data(data, output_file):
            exit_code = 0  # Success
        else:
            _LOGGER.error("Failed to save water consumption data")
    except requests.RequestException as e:
        _LOGGER.error("Failed to fetch water data: %s", e)
    return exit_code


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    sys.exit(main())
