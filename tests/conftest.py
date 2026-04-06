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
    return mock_entry


@pytest.fixture
def mock_coordinator():
    """Fixture to mock a DataUpdateCoordinator."""
    coordinator = MagicMock()
    coordinator.data = {}
    coordinator.last_update_success_time = None
    coordinator.async_request_refresh = AsyncMock()
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
