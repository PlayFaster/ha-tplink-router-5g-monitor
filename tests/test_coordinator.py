"""Tests for the TP-Link Router coordinator."""

from unittest.mock import MagicMock, patch

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.tplink_router_5g.const import CONF_STOP_POLLING
from custom_components.tplink_router_5g.coordinator import (
    TPLinkRouterDataUpdateCoordinator,
)


@pytest.fixture(autouse=True)
def mock_report_usage():
    """Mock report_usage to avoid 'Frame helper not set up' error."""
    with patch("homeassistant.helpers.frame.report_usage"):
        yield


@pytest.mark.asyncio
async def test_coordinator_update_failure(mock_api, mock_config_entry):
    """Test coordinator update failure and retry logic."""
    hass = MagicMock()
    with patch("homeassistant.helpers.frame._hass", hass):
        mock_api.login.side_effect = Exception("Connection error")
        coordinator = TPLinkRouterDataUpdateCoordinator(
            hass, mock_config_entry, mock_api
        )

        # Mock initial data to test "holding last known values"
        coordinator.data = {"old": "data"}

        with patch(
            "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.__init__",
            return_value=None,
        ):
            # First failure: should return old data and log warning
            data = await coordinator._async_update_data()
            assert data == {"old": "data"}
            assert coordinator.consecutive_failures == 1

            # Third failure: should raise UpdateFailed
            coordinator.consecutive_failures = 2
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()
            assert coordinator.consecutive_failures == 3


@pytest.mark.asyncio
async def test_coordinator_paused_polling(mock_api, mock_config_entry):
    """Test coordinator behavior when polling is paused."""
    hass = MagicMock()
    mock_config_entry.options[CONF_STOP_POLLING] = True

    coordinator = TPLinkRouterDataUpdateCoordinator(hass, mock_config_entry, mock_api)
    coordinator.data = {"cached": "data"}

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.__init__",
        return_value=None,
    ):
        data = await coordinator._async_update_data()
        assert data == {"cached": "data"}
        mock_api.login.assert_not_called()


@pytest.mark.asyncio
async def test_coordinator_timeout(mock_api, mock_config_entry):
    """Test coordinator timeout handling."""
    hass = MagicMock()
    with patch("homeassistant.helpers.frame._hass", hass):
        mock_api.login.side_effect = TimeoutError()
        coordinator = TPLinkRouterDataUpdateCoordinator(
            hass, mock_config_entry, mock_api
        )

        with patch(
            "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.__init__",
            return_value=None,
        ):
            # No old data, should raise UpdateFailed immediately
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()
            assert coordinator.consecutive_failures == 1


@pytest.mark.asyncio
async def test_coordinator_update_success(mock_api, mock_config_entry):
    """Test successful data update."""
    hass = MagicMock()
    # Setup global hass mock for frame helper
    with patch("homeassistant.helpers.frame._hass", hass):
        mock_api.get_status.return_value = MagicMock(
            clients_total=5, lan_macaddr="00:11:22:33:44:55"
        )

        mock_lte = MagicMock(network_type_info="5G NR")
        mock_extra = {"nr_rsrp": "-80"}
        mock_api.get_lte_and_extra_status.return_value = (mock_lte, mock_extra)

        mock_api.get_firmware.return_value = MagicMock(
            model="NX510v", firmware_version="1.0.0", hardware_version="V1"
        )

        coordinator = TPLinkRouterDataUpdateCoordinator(
            hass, mock_config_entry, mock_api
        )

        with patch(
            "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.__init__",
            return_value=None,
        ):
            data = await coordinator._async_update_data()

            assert data["status"].clients_total == 5
            assert data["lte_status"].network_type_info == "5G NR"
            assert data["extra_lte_status"]["nr_rsrp"] == "-80"
            assert coordinator.consecutive_failures == 0
            assert coordinator.mac == "00:11:22:33:44:55"
