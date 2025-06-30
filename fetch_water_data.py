"""Fetch water consumption data from City4U API and save to JSON file."""

import argparse
import json
import logging
from datetime import datetime

import requests
import urllib3

_LOGGER = logging.getLogger(__name__)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- API URLs ---
LOGIN_URL = "https://city4u.co.il/WebApiUsersManagement/v1/UsrManagements/LoginUser"
DATA_URL_TEMPLATE = "https://city4u.co.il/WebApiCity4u/v1/WaterConsumption/ReadingMoneWater/{customer_id}/{meter_number}"

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
            _LOGGER.error(f"Login failed with status {response.status_code}: {response.text[:500]}")
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

    data_url = DATA_URL_TEMPLATE.format(customer_id=customer_id, meter_number=meter_number)
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


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch water consumption data from City4U API"
    )
    parser.add_argument(
        "--username", 
        required=True,
        help="Your City4U username"
    )
    parser.add_argument(
        "--password", 
        required=True, 
        help="Your City4U password"
    )
    parser.add_argument(
        "--customer-id", 
        required=True, 
        help="Your City4U customer ID"
    )
    parser.add_argument(
        "--meter-number", 
        help="Your meter number (defaults to same as username if not provided)"
    )
    parser.add_argument(
        "--output", 
        default="water_consumption_data.json", 
        help="Output JSON file path (default: water_consumption_data.json)"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug logging"
    )
    return parser.parse_args()


def main():
    """Main function to fetch and save water consumption data."""
    args = parse_arguments()
    
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)
    
    # If meter_number is not provided, use username as default
    meter_number = args.meter_number if args.meter_number else args.username
    
    # Get token
    token = get_token(args.username, args.password, args.customer_id)
    if not token:
        _LOGGER.error("Failed to obtain authentication token")
        return 1
    
    _LOGGER.info(f"Successfully obtained token: {token}")
    
    try:
        # Fetch water data
        data = fetch_water_data(token, args.username, args.customer_id, meter_number)
        if not data:
            _LOGGER.error("Failed to retrieve water consumption data")
            return 1
        
        _LOGGER.info("Successfully fetched water consumption data")
        
        # Save data
        if not save_water_data(data, args.output):
            _LOGGER.error("Failed to save water consumption data")
            return 1
        
        return 0
    except Exception as e:
        _LOGGER.error(f"Failed to fetch water data: {e}")
        return 1


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    exit(main())