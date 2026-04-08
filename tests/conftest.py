"""Fixtures and utilities for testing the TP-Link Router integration."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.const import CONF_HOST


@pytest.fixture
def mock_config_entry():
    """Fixture to mock a ConfigEntry."""
    mock_entry = MagicMock()
    mock_entry.unique_id = "tplink_unique_123"
    mock_entry.title = "My TP-Link Router"
    mock_entry.options = {CONF_HOST: "192.168.253.1"}
    mock_entry.data = {}

    # Mock async_create_background_task and close coroutine to avoid RuntimeWarning
    def mock_create_background_task(hass, coro, name):
        coro.close()
        return MagicMock()

    mock_entry.async_create_background_task = MagicMock(
        side_effect=mock_create_background_task
    )
    return mock_entry


@pytest.fixture
def mock_coordinator():
    """Fixture to mock a DataUpdateCoordinator."""
    coordinator = MagicMock()
    coordinator.data = {}
    coordinator.last_update_success_time = None
    coordinator.async_request_refresh = AsyncMock()
    # Add flat identity attributes for modern tests
    coordinator.model = "NX510v"
    coordinator.sw_version = "1.0.0"
    coordinator.hw_version = "V1"
    coordinator.mac = "00:11:22:33:44:55"
    return coordinator


@pytest.fixture
def mock_api():
    """Fixture to mock the TP-Link API."""
    api = MagicMock()
    api.login = AsyncMock()
    api.logout = AsyncMock()
    api.get_status = AsyncMock()
    api.get_lte_and_extra_status = AsyncMock(return_value=(MagicMock(), {}))
    api.get_ipv4_status = AsyncMock()
    api.get_vpn_status = AsyncMock()
    api.get_firmware = AsyncMock()
    api.send_sms = AsyncMock()
    api.reboot = AsyncMock()
    api.set_wifi = AsyncMock()
    return api
