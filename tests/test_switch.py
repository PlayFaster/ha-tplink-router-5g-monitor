"""Tests for the TP-Link Router switch."""

from unittest.mock import MagicMock, AsyncMock

import pytest

from custom_components.tplink_router_5g.const import CONF_STOP_POLLING, DOMAIN
from custom_components.tplink_router_5g.switch import (
    WIFI_SWITCHES,
    TPLinkWifiSwitch,
    TPLinkPausePollingSwitch,
    async_setup_entry,
)


@pytest.mark.asyncio
async def test_wifi_switch(mock_coordinator, mock_config_entry):
    """Test turning the wifi switch on and off."""
    description = next(d for d in WIFI_SWITCHES if d.key == "wifi_2g_main")
    switch = TPLinkWifiSwitch(
        mock_coordinator, mock_config_entry, description
    )
    
    mock_coordinator.data = {"status": MagicMock(wifi_2g_enable=False)}
    assert switch.is_on is False

    await switch.async_turn_on()
    mock_coordinator.api.set_wifi.assert_called_with("wifi_2g", True)

    await switch.async_turn_off()
    mock_coordinator.api.set_wifi.assert_called_with("wifi_2g", False)
    mock_coordinator.async_request_refresh.assert_called()


@pytest.mark.asyncio
async def test_pause_polling_switch(mock_coordinator, mock_config_entry):
    """Test turning the pause switch on and off."""
    mock_config_entry.options[CONF_STOP_POLLING] = False

    switch = TPLinkPausePollingSwitch(
        mock_coordinator, mock_config_entry
    )
    switch.hass = MagicMock()
    switch.hass.data = {DOMAIN: {mock_config_entry.entry_id: mock_coordinator}}
    switch.async_write_ha_state = MagicMock()

    await switch.async_turn_on()
    switch.hass.config_entries.async_update_entry.assert_called()
    _args, kwargs = switch.hass.config_entries.async_update_entry.call_args
    assert kwargs["options"][CONF_STOP_POLLING] is True

    await switch.async_turn_off()
    _args, kwargs = switch.hass.config_entries.async_update_entry.call_args
    assert kwargs["options"][CONF_STOP_POLLING] is False
    mock_coordinator.async_request_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_switch_setup_entry():
    """Test platform setup."""
    hass = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test"
    entry.options = {CONF_STOP_POLLING: False}
    coordinator = MagicMock()
    hass.data = {DOMAIN: {"test": coordinator}}

    async_add_entities = MagicMock()
    await async_setup_entry(hass, entry, async_add_entities)
    async_add_entities.assert_called_once()
