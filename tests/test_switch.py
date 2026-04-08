"""Tests for the TP-Link Router switch."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from tplinkrouterc6u import Connection

from custom_components.tplink_router_5g.const import CONF_STOP_POLLING, DOMAIN
from custom_components.tplink_router_5g.switch import (
    WIFI_SWITCHES,
    TPLinkPausePollingSwitch,
    TPLinkWifiSwitch,
    async_setup_entry,
)


@pytest.mark.asyncio
async def test_wifi_switch(mock_coordinator, mock_config_entry):
    """Test turning the wifi switch on and off."""
    description = next(d for d in WIFI_SWITCHES if d.key == "wifi_2g_main")
    switch = TPLinkWifiSwitch(mock_coordinator, mock_config_entry, description)

    mock_coordinator.data = {"status": MagicMock(wifi_2g_enable=False)}
    assert switch.is_on is False

    # Ensure API methods are AsyncMocks
    mock_coordinator.api.login = AsyncMock()
    mock_coordinator.api.set_wifi = AsyncMock()
    mock_coordinator.api.logout = AsyncMock()

    await switch.async_turn_on()
    mock_coordinator.api.set_wifi.assert_called_with(Connection.HOST_2G, True)

    await switch.async_turn_off()
    mock_coordinator.api.set_wifi.assert_called_with(Connection.HOST_2G, False)
    mock_coordinator.async_request_refresh.assert_called()


@pytest.mark.asyncio
async def test_wifi_switch_error(mock_coordinator, mock_config_entry):
    """Test error handling in wifi switch and ensure logout is called."""
    description = next(d for d in WIFI_SWITCHES if d.key == "wifi_2g_main")
    switch = TPLinkWifiSwitch(mock_coordinator, mock_config_entry, description)

    mock_coordinator.api.login = AsyncMock()
    mock_coordinator.api.logout = AsyncMock()
    mock_coordinator.api.set_wifi = AsyncMock(side_effect=Exception("Set fail"))

    with pytest.raises(Exception, match="Set fail"):
        await switch.async_turn_on()

    mock_coordinator.api.logout.assert_called_once()


@pytest.mark.asyncio
async def test_wifi_switch_turn_off_error(mock_coordinator, mock_config_entry):
    """Test error handling in wifi switch turn off."""
    description = next(d for d in WIFI_SWITCHES if d.key == "wifi_2g_main")
    switch = TPLinkWifiSwitch(mock_coordinator, mock_config_entry, description)

    mock_coordinator.api.login = AsyncMock()
    mock_coordinator.api.logout = AsyncMock()
    mock_coordinator.api.set_wifi = AsyncMock(side_effect=Exception("Off fail"))

    with pytest.raises(Exception, match="Off fail"):
        await switch.async_turn_off()

    mock_coordinator.api.logout.assert_called_once()


@pytest.mark.asyncio
async def test_wifi_switch_no_status(mock_coordinator, mock_config_entry):
    """Test is_on when status data is missing."""
    description = next(d for d in WIFI_SWITCHES if d.key == "wifi_2g_main")
    switch = TPLinkWifiSwitch(mock_coordinator, mock_config_entry, description)

    # 1. No data at all
    mock_coordinator.data = None
    assert switch.is_on is False

    # 2. No status key
    mock_coordinator.data = {}
    assert switch.is_on is False


def test_wifi_switch_device_info_mac(mock_coordinator, mock_config_entry):
    """Test device_info when MAC is available."""
    description = next(d for d in WIFI_SWITCHES if d.key == "wifi_2g_main")
    switch = TPLinkWifiSwitch(mock_coordinator, mock_config_entry, description)

    mock_coordinator.mac = "AA:BB:CC:DD:EE:FF"
    info = switch.device_info
    assert info["identifiers"] == {(DOMAIN, "AA:BB:CC:DD:EE:FF_wifi")}
    assert info["via_device"] == (DOMAIN, "AA:BB:CC:DD:EE:FF")


def test_wifi_switch_device_info_no_mac(mock_coordinator, mock_config_entry):
    """Test device_info when MAC is NOT available."""
    description = next(d for d in WIFI_SWITCHES if d.key == "wifi_2g_main")
    switch = TPLinkWifiSwitch(mock_coordinator, mock_config_entry, description)

    mock_coordinator.mac = None
    info = switch.device_info

    # Check identifiers
    expected_id = "host_192.168.253.1_wifi"
    assert info["identifiers"] == {(DOMAIN, expected_id)}

    # Check via_device
    expected_via = (DOMAIN, "host_192.168.253.1")
    assert info["via_device"] == expected_via


@pytest.mark.asyncio
async def test_pause_polling_switch(mock_coordinator, mock_config_entry):
    """Test turning the pause switch on and off."""
    mock_config_entry.options[CONF_STOP_POLLING] = False

    switch = TPLinkPausePollingSwitch(mock_coordinator, mock_config_entry)
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


def test_pause_polling_switch_device_info(mock_coordinator, mock_config_entry):
    """Test device_info for pause polling switch."""
    switch = TPLinkPausePollingSwitch(mock_coordinator, mock_config_entry)

    # 1. With MAC
    mock_coordinator.mac = "AA:BB:CC"
    assert switch.device_info["identifiers"] == {(DOMAIN, "AA:BB:CC")}

    # 2. No MAC
    mock_coordinator.mac = None
    assert switch.device_info["identifiers"] == {(DOMAIN, "host_192.168.253.1")}


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
