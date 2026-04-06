"""Tests for the TP-Link Router number."""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.tplink_router_5g.const import CONF_SCAN_INTERVAL, DOMAIN
from custom_components.tplink_router_5g.number import (
    POLLING_INTERVAL_DESCRIPTION,
    TPLinkPollingInterval,
    async_setup_entry,
)


@pytest.mark.asyncio
async def test_polling_interval_change(mock_coordinator, mock_config_entry):
    """Test that changing the slider updates the coordinator and options."""
    number = TPLinkPollingInterval(
        mock_coordinator, mock_config_entry, POLLING_INTERVAL_DESCRIPTION, 120
    )
    number.hass = MagicMock()
    number.async_write_ha_state = MagicMock()

    with patch("asyncio.sleep", AsyncMock()):
        await number.async_set_native_value(300)

        if number._refresh_task:
            await number._refresh_task

        assert number.native_value == 300
        assert mock_coordinator.update_interval == timedelta(seconds=300)

        number.hass.config_entries.async_update_entry.assert_called_once()
        _args, kwargs = number.hass.config_entries.async_update_entry.call_args
        assert kwargs["options"][CONF_SCAN_INTERVAL] == 300

        mock_coordinator.async_request_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_number_setup_entry():
    """Test platform setup."""
    hass = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test"
    entry.options = {CONF_SCAN_INTERVAL: 120}
    coordinator = MagicMock()
    hass.data = {DOMAIN: {"test": coordinator}}

    async_add_entities = MagicMock()
    await async_setup_entry(hass, entry, async_add_entities)
    async_add_entities.assert_called_once()
