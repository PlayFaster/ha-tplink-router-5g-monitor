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
async def test_polling_interval_remove_hass(mock_coordinator, mock_config_entry):
    """Test removing the number entity from hass."""
    number = TPLinkPollingInterval(
        mock_coordinator, mock_config_entry, POLLING_INTERVAL_DESCRIPTION, 120
    )
    number.hass = MagicMock()
    number.async_write_ha_state = MagicMock()
    # Start a task
    with patch("asyncio.sleep", AsyncMock()):
        await number.async_set_native_value(300)
        assert number._refresh_task is not None

        task = number._refresh_task
        await number.async_will_remove_from_hass()
        assert task.cancelled()
        assert number._refresh_task is None


@pytest.mark.asyncio
async def test_polling_interval_error(mock_coordinator, mock_config_entry):
    """Test error handling in polling interval apply."""
    number = TPLinkPollingInterval(
        mock_coordinator, mock_config_entry, POLLING_INTERVAL_DESCRIPTION, 120
    )
    number.hass = MagicMock()
    number.async_write_ha_state = MagicMock()

    # Simulate error in refresh
    mock_coordinator.async_request_refresh.side_effect = Exception("Refresh fail")

    with patch("asyncio.sleep", AsyncMock()):
        await number.async_set_native_value(300)
        if number._refresh_task:
            await number._refresh_task
        # Should log error but not crash


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
