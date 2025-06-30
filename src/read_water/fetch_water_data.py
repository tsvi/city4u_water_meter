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
DATA_URL_TEMPLATE = "https://city4u.co.il/WebApiCity4u/v1/WaterConsumption/ReadingMoneWater/{customer_id}/{meter_number}"
CUSTOMERS_URL = "https://city4u.co.il/WebApi_portal/v1/Customers/Customer/allcustomers"

# Default configuration file location
CONFIG_FILE = os.path.expanduser("~/.config/water_consumption/config.json")


# --- LOGIN FUNCTION ---
def get_token(username, password, customer_id):
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
        _LOGGER.debug(f"Login response status: {response.status_code}")
        _LOGGER.debug(f"Login response headers: {dict(response.headers)}")
        _LOGGER.debug(f"Login response cookies: {dict(response.cookies)}")
        if response.status_code == 200:
            try:
                data = response.json()
                user_token = data.get("UserToken")
                if user_token:
                    _LOGGER.info(f"✓ Successfully extracted UserToken: {user_token}")
                    return user_token
                else:
                    _LOGGER.error("No UserToken found in response")
            except Exception as e:
                _LOGGER.error(f"Failed to parse login response: {e}")
        else:
            _LOGGER.error(
                f"Login failed with status {response.status_code}: {response.text[:500]}"
            )
    except Exception as e:
        _LOGGER.error(f"Login request failed: {e}")

    return None


# --- DATA FETCH FUNCTION ---
def fetch_water_data(token, username, customer_id, meter_number):
    headers = {
        "customerID": customer_id,
        "CustomerSite": customer_id,
        "UserName": username,
        "token": token,
    }

    data_url = DATA_URL_TEMPLATE.format(
        customer_id=customer_id, meter_number=meter_number
    )
    session = requests.Session()  # Use a simple session for now

    try:
        _LOGGER.info("Fetching water consumption data...")
        response = session.get(data_url, headers=headers, verify=False, timeout=30)
        _LOGGER.debug(f"Data response status: {response.status_code}")
        _LOGGER.debug(f"Data response headers: {dict(response.headers)}")

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                _LOGGER.error("Data response is not JSON")
                _LOGGER.error(f"Data response text: {response.text[:500]}...")
                return None
        else:
            _LOGGER.error(f"Data fetch failed with status {response.status_code}")
            _LOGGER.error(f"Response: {response.text[:500]}...")
            return None
    except Exception as e:
        _LOGGER.error(f"Data fetch failed: {e}")
        return None


# --- SAVE DATA FUNCTION ---
def save_water_data(data, output_file):
    """Save water consumption data to JSON file with timestamp"""
    try:
        # Add timestamp to the data
        output_data = {"timestamp": datetime.now().isoformat(), "data": data}

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        _LOGGER.info(f"✓ Water consumption data saved to {output_file}")
        return True
    except Exception as e:
        _LOGGER.error(f"✗ Failed to save data to file: {e}")
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
    """Fetch the list of customers from the City4U API."""
    try:
        _LOGGER.info("Fetching customer list...")
        response = requests.get(CUSTOMERS_URL, verify=False, timeout=30)

        if response.status_code == 200:
            try:
                customers = response.json()
                return customers
            except json.JSONDecodeError:
                _LOGGER.error("Customer data response is not valid JSON")
                _LOGGER.error(f"Response text: {response.text[:500]}...")
                return None
        else:
            _LOGGER.error(f"Customer fetch failed with status {response.status_code}")
            return None
    except Exception as e:
        _LOGGER.error(f"Failed to fetch customer list: {e}")
        return None


def select_customer():
    """Let the user select their customer (city) from the list."""
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
            else:
                print(f"Please enter a number between 1 and {len(sorted_customers)}")
        except ValueError:
            print("Please enter a valid number")
        except Exception as e:
            _LOGGER.error(f"Error during customer selection: {e}")
            return None


def create_config_file(config):
    """Create a configuration file with the provided settings."""
    try:
        # Create directory if it doesn't exist
        config_dir = os.path.dirname(CONFIG_FILE)
        Path(config_dir).mkdir(parents=True, exist_ok=True)

        # Write the configuration
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        _LOGGER.info(f"Configuration saved to {CONFIG_FILE}")
        return True
    except Exception as e:
        _LOGGER.error(f"Failed to create configuration file: {e}")
        return False


def setup_config():
    """Walk through the setup process to create a configuration file."""
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
    else:
        print(
            "\nFailed to save configuration. You'll need to provide credentials manually."
        )
        return None


def load_config():
    """Load configuration from file or run setup if it doesn't exist."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            _LOGGER.info(f"Configuration loaded from {CONFIG_FILE}")
            return config
        except Exception as e:
            _LOGGER.error(f"Failed to load configuration: {e}")
            return None
    else:
        _LOGGER.info("No configuration file found. Starting setup...")
        return setup_config()


def parse_arguments():
    """Parse command line arguments."""
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
    """Main function to fetch and save water consumption data."""
    args = parse_arguments()

    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)

    # If setup flag is provided, run setup regardless of existing config
    if args.setup:
        config = setup_config()
        if not config:
            return 1
    else:
        # Load configuration or run setup if not found
        config = load_config()
        if not config:
            _LOGGER.error("Failed to load or create configuration")
            return 1

    # Command-line arguments override config file
    username = args.username or config.get("username")
    password = args.password or config.get("password")
    customer_id = args.customer_id or config.get("customer_id")
    meter_number = args.meter_number or config.get("meter_number") or username
    output_file = args.output or config.get(
        "output_file", "water_consumption_data.json"
    )

    if not all([username, password, customer_id]):
        _LOGGER.error("Missing required parameters (username, password, customer_id)")
        return 1

    # Get token
    token = get_token(username, password, str(customer_id))
    if not token:
        _LOGGER.error("Failed to obtain authentication token")
        return 1

    _LOGGER.info(f"Successfully obtained token: {token}")

    try:
        # Fetch water data
        data = fetch_water_data(token, username, str(customer_id), meter_number)
        if not data:
            _LOGGER.error("Failed to retrieve water consumption data")
            return 1

        _LOGGER.info("Successfully fetched water consumption data")

        # Save data
        if not save_water_data(data, output_file):
            _LOGGER.error("Failed to save water consumption data")
            return 1

        return 0
    except Exception as e:
        _LOGGER.error(f"Failed to fetch water data: {e}")
        return 1


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    sys.exit(main())
