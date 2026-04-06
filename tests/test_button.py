"""Tests for the TP-Link Router button."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.tplink_router_5g.button import (
    BUTTON_TYPES,
    TPLinkRebootButton,
    async_setup_entry,
)
from custom_components.tplink_router_5g.const import DOMAIN


@pytest.mark.asyncio
async def test_reboot_button_press(mock_coordinator, mock_config_entry):
    """Test reboot button trigger."""
    description = next(d for d in BUTTON_TYPES if d.key == "reboot")
    button = TPLinkRebootButton(
        mock_coordinator, mock_config_entry, description
    )

    await button.async_press()
    mock_coordinator.api.reboot.assert_called_once()


def test_button_device_info(mock_coordinator, mock_config_entry):
    """Test device_info for router group."""
    description = next(d for d in BUTTON_TYPES if d.key == "reboot")
    button = TPLinkRebootButton(
        mock_coordinator, mock_config_entry, description
    )

    assert button.device_info["identifiers"] == {(DOMAIN, "host_192.168.253.1")}


@pytest.mark.asyncio
async def test_button_setup_entry():
    """Test platform setup."""
    hass = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test"
    coordinator = MagicMock()
    hass.data = {DOMAIN: {"test": coordinator}}

    async_add_entities = MagicMock()
    await async_setup_entry(hass, entry, async_add_entities)
    async_add_entities.assert_called_once()
