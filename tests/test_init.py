"""Tests for the TP-Link Router init."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.tplink_router_5g import async_setup_entry, async_unload_entry
from custom_components.tplink_router_5g.const import (
    CONF_SCAN_INTERVAL,
    CONF_STOP_POLLING,
    DOMAIN,
)
from custom_components.tplink_router_5g.coordinator import (
    TPLinkRouterDataUpdateCoordinator,
)


@pytest.fixture(autouse=True)
def mock_report_usage():
    """Mock report_usage to avoid 'Frame helper not set up' error."""
    with patch("homeassistant.helpers.frame.report_usage"):
        yield


@pytest.fixture
def mock_hass():
    """Create a mock HomeAssistant instance with necessary async methods."""
    hass = MagicMock()
    hass.data = {}
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.config_entries.async_update_entry = MagicMock()
    hass.services.async_register = MagicMock()

    def mock_create_task(coro):
        coro.close()
        return MagicMock()

    hass.async_create_task = MagicMock(side_effect=mock_create_task)
    return hass


@pytest.mark.asyncio
async def test_setup_entry_success(mock_hass, mock_config_entry):
    """Test successful setup of the integration."""
    mock_config_entry.entry_id = "test_entry"
    mock_config_entry.options = {
        "host": "192.168.253.1",
        "password": "pass",
        CONF_STOP_POLLING: False,
        CONF_SCAN_INTERVAL: 120,
    }

    with (
        patch("custom_components.tplink_router_5g.TPLinkRouter5GAPI"),
        patch("homeassistant.helpers.frame._hass", mock_hass),
    ):
        assert await async_setup_entry(mock_hass, mock_config_entry) is True

        assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]
        coordinator = mock_hass.data[DOMAIN][mock_config_entry.entry_id]
        assert isinstance(coordinator, TPLinkRouterDataUpdateCoordinator)

        mock_hass.config_entries.async_forward_entry_setups.assert_called_once()
        mock_hass.async_create_task.assert_called_once()
        mock_hass.services.async_register.assert_called_once()


@pytest.mark.asyncio
async def test_unload_entry_success(mock_hass, mock_config_entry):
    """Test successful unloading of the integration."""
    mock_api = MagicMock()
    mock_coordinator = MagicMock()
    mock_coordinator.api = mock_api
    mock_config_entry.entry_id = "test_entry"
    mock_hass.data = {DOMAIN: {"test_entry": mock_coordinator}}

    assert await async_unload_entry(mock_hass, mock_config_entry) is True
    assert mock_hass.data[DOMAIN] == {}
