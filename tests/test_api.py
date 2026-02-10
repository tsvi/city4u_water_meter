"""Test the City4U API client."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import aiohttp
import pytest

from custom_components.city4u.api import City4UApiClient

from .conftest import create_mock_response


async def test_authenticate_success(
    city4u_client: City4UApiClient, mock_session: MagicMock
) -> None:
    """Test successful authentication."""
    mock_response = create_mock_response(200, json_data={"UserToken": "test_token"})
    mock_session.post.return_value.__aenter__.return_value = mock_response

    await city4u_client.authenticate()

    assert city4u_client.token == "test_token"
    assert city4u_client.token_expires_at is not None
    mock_session.post.assert_called_once()
    _, kwargs = mock_session.post.call_args
    assert kwargs["data"]["UserName"] == "test_user"
    assert kwargs["data"]["Password"] == "test_password"


@pytest.mark.parametrize(
    ("status_code", "response_text"),
    [
        (401, "Unauthorized"),
        (403, "Forbidden"),
        (500, "Internal Server Error"),
        (503, "Service Unavailable"),
    ],
)
async def test_authenticate_failure(
    city4u_client: City4UApiClient,
    mock_session: MagicMock,
    status_code: int,
    response_text: str,
) -> None:
    """Test authentication failure with various status codes."""
    mock_response = create_mock_response(status_code, text=response_text)
    mock_session.post.return_value.__aenter__.return_value = mock_response

    with pytest.raises(aiohttp.ClientResponseError):
        await city4u_client.authenticate()

    assert city4u_client.token is None


async def test_fetch_water_data_success(
    city4u_client: City4UApiClient, mock_session: MagicMock
) -> None:
    """Test successful water data fetching."""
    city4u_client.set_token("test_token")

    expected_data = [
        {
            "totalWaterDataWithMultiplier": 123.45,
            "readingTime": "2025-01-01T12:00:00",
            "meterNumber": "test_meter",
        }
    ]

    mock_response = create_mock_response(200, json_data=expected_data)
    mock_session.get.return_value.__aenter__.return_value = mock_response

    data = await city4u_client.fetch_water_data()

    assert data == expected_data
    mock_session.get.assert_called_once()
    args, kwargs = mock_session.get.call_args
    assert "123456" in args[0]
    assert "test_meter" in args[0]
    assert kwargs["headers"]["token"] == "test_token"


@pytest.mark.parametrize(
    ("status_code", "response_text"),
    [
        (401, "Unauthorized"),
        (404, "Not Found"),
        (500, "Internal Server Error"),
    ],
)
async def test_fetch_water_data_failure(
    city4u_client: City4UApiClient,
    mock_session: MagicMock,
    status_code: int,
    response_text: str,
) -> None:
    """Test water data fetching failure with various status codes."""
    city4u_client.set_token("test_token")

    mock_response = create_mock_response(status_code, text=response_text)
    mock_session.get.return_value.__aenter__.return_value = mock_response

    with pytest.raises(aiohttp.ClientResponseError):
        await city4u_client.fetch_water_data()


@pytest.mark.parametrize(
    ("token", "expires_at", "expected"),
    [
        (None, None, False),
        ("test_token", None, False),
        ("test_token", datetime.now() + timedelta(hours=1), True),
        ("test_token", datetime.now() - timedelta(hours=1), False),
    ],
    ids=[
        "no_token",
        "token_no_expiry",
        "token_valid_expiry",
        "token_expired",
    ],
)
def test_token_validation(
    city4u_client: City4UApiClient,
    token: str | None,
    expires_at: datetime | None,
    expected: bool,
) -> None:
    """Test token validation with various states."""
    city4u_client.set_token(token, expires_at)

    assert city4u_client.is_token_valid() is expected
