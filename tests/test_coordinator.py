"""Tests for the TP-Link Router coordinator."""

from unittest.mock import MagicMock, patch

import pytest

from custom_components.tplink_router_5g.coordinator import (
    TPLinkRouterDataUpdateCoordinator,
)


@pytest.mark.asyncio
async def test_coordinator_update_success(mock_api, mock_config_entry):
    """Test successful data update."""
    hass = MagicMock()
    mock_api.get_status.return_value = MagicMock(clients_total=5)
    mock_api.get_lte_status.return_value = MagicMock(network_type_info="5G NR")
    mock_api.get_extra_lte_status.return_value = {"nr_rsrp": "-80"}
    mock_api.get_firmware.return_value = MagicMock(model="NX510v")

    coordinator = TPLinkRouterDataUpdateCoordinator(hass, mock_config_entry, mock_api)

    with patch("homeassistant.helpers.update_coordinator.DataUpdateCoordinator.__init__"):
        data = await coordinator._async_update_data()

        assert data["status"].clients_total == 5
        assert data["lte_status"].network_type_info == "5G NR"
        assert data["extra_lte_status"]["nr_rsrp"] == "-80"
        assert coordinator.consecutive_failures == 0
