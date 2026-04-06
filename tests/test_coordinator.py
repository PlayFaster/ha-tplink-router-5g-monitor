"""Tests for the TP-Link Router coordinator."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.tplink_router_5g.coordinator import (
    TPLinkRouterDataUpdateCoordinator,
)


@pytest.fixture(autouse=True)
def mock_report_usage():
    """Mock report_usage to avoid 'Frame helper not set up' error."""
    with patch("homeassistant.helpers.frame.report_usage"):
        yield


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

        mock_api.get_firmware.return_value = MagicMock(model="NX510v")

        coordinator = TPLinkRouterDataUpdateCoordinator(
            hass, mock_config_entry, mock_api
        )

        with (
            patch(
                "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.__init__"
            ),
            patch("asyncio.sleep", AsyncMock()),
        ):
            data = await coordinator._async_update_data()

            assert data["status"].clients_total == 5
            assert data["lte_status"].network_type_info == "5G NR"
            assert data["extra_lte_status"]["nr_rsrp"] == "-80"
            assert coordinator.consecutive_failures == 0
            assert coordinator.mac == "00:11:22:33:44:55"
