"""City4U API client."""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from .const import DATA_URL_TEMPLATE, LOGIN_URL, TOKEN_EXPIRATION_MINUTES

_LOGGER = logging.getLogger(__name__)


@dataclass
class City4UCredentials:
    """Credentials for City4U API."""

    username: str
    password: str
    customer_id: str
    meter_number: str


class City4UApiClient:
    """City4U API client."""

    def __init__(
        self,
        credentials: City4UCredentials,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the API client."""
        self._credentials = credentials
        self._session = session
        self._token: str | None = None
        self._token_expires_at: datetime | None = None
        self._last_poll_time: datetime | None = None

    @property
    def last_poll_time(self) -> datetime | None:
        """Return the last time data was polled."""
        return self._last_poll_time

    @property
    def meter_number(self) -> str:
        """Return the meter number."""
        return self._credentials.meter_number

    @property
    def customer_id(self) -> str:
        """Return the customer ID."""
        return str(self._credentials.customer_id)

    @property
    def token(self) -> str | None:
        """Return the current token (for testing)."""
        return self._token

    @property
    def token_expires_at(self) -> datetime | None:
        """Return when the token expires (for testing)."""
        return self._token_expires_at

    def set_token(self, token: str | None, expires_at: datetime | None = None) -> None:
        """Set the token (for testing)."""
        self._token = token
        self._token_expires_at = expires_at

    def is_token_valid(self) -> bool:
        """Check if the current token is valid."""
        if not self._token or not self._token_expires_at:
            return False

        # Consider the token invalid if it will expire in the next 5 minutes
        now = datetime.now()
        return self._token_expires_at > now + timedelta(minutes=5)

    async def _parse_json_response(
        self,
        response: aiohttp.ClientResponse,
        context: str,
    ) -> Any:
        """Read a response, enforce HTTP 200, and return parsed JSON.

        Raises aiohttp.ClientResponseError with a descriptive message on any
        failure so callers don't need to repeat this boilerplate.
        """
        text = await response.text()

        if response.status != 200:
            _LOGGER.error(
                "%s failed with status %s: %s",
                context,
                response.status,
                text[:500],
            )
            raise aiohttp.ClientResponseError(
                response.request_info,
                response.history,
                status=response.status,
                message=f"{context} failed: {text[:100]}...",
            )

        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError) as json_err:
            _LOGGER.error(
                "%s response is not valid JSON (got %s). Response body: %s",
                context,
                response.content_type,
                text[:500],
            )
            raise aiohttp.ClientResponseError(
                response.request_info,
                response.history,
                status=response.status,
                message=(
                    f"{context} returned non-JSON response ({response.content_type})"
                ),
            ) from json_err

    async def authenticate(self) -> None:
        """Authenticate with City4U API."""
        # Use the exact payload format from the browser trace
        payload = {
            "ServiceName": "LoginUser",
            "UserName": self._credentials.username,
            "Password": self._credentials.password,
            "token": "undefined",
            "customerID": str(self._credentials.customer_id),
            "CustomerSite": str(self._credentials.customer_id),
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            _LOGGER.debug("Authenticating with City4U API...")
            async with self._session.post(
                LOGIN_URL,
                data=payload,
                headers=headers,
                ssl=False,  # Disable SSL verification as in original code
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                data = await self._parse_json_response(response, "Authentication")
                user_token = data.get("UserToken")
                if not user_token:
                    _LOGGER.error("No UserToken found in response")
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message="No UserToken found in response",
                    )

                self._token = user_token
                # Set token expiration (default to 12 hours)
                self._token_expires_at = datetime.now() + timedelta(
                    minutes=TOKEN_EXPIRATION_MINUTES
                )
                _LOGGER.debug(
                    "Successfully obtained token, expires at %s", self._token_expires_at
                )

        except aiohttp.ClientError as err:
            _LOGGER.error("Error during authentication: %s", err)
            raise

    async def fetch_water_data(self) -> list[dict[str, Any]]:
        """Fetch water consumption data from City4U API."""
        if not self._token:
            await self.authenticate()

        customer_id = str(self._credentials.customer_id)
        if not self._token:
            raise aiohttp.ClientError("No authentication token available")
        headers: dict[str, str] = {
            "customerID": customer_id,
            "CustomerSite": customer_id,
            "UserName": self._credentials.username,
            "token": self._token,
        }

        data_url = DATA_URL_TEMPLATE % (customer_id, self._credentials.meter_number)

        try:
            _LOGGER.debug("Fetching water consumption data...")
            async with self._session.get(
                data_url,
                headers=headers,
                ssl=False,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                data: list[dict[str, Any]] = await self._parse_json_response(
                    response, "Data fetch"
                )
                self._last_poll_time = datetime.now()
                _LOGGER.debug("Successfully fetched water consumption data")
                return data

        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching water data: %s", err)
            raise

    async def fetch_all_historical_data(self) -> list[dict[str, Any]]:
        """Fetch all available historical water consumption data.

        This method fetches all readings available from the API.
        The API returns all historical data by default.
        """
        _LOGGER.info("Fetching all historical water consumption data...")
        return await self.fetch_water_data()
