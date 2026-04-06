"""Tests for the TP-Link Router binary sensor."""

from unittest.mock import MagicMock

import pytest

from custom_components.tplink_router_5g.binary_sensor import (
    BINARY_SENSORS,
    TPLinkRouterBinarySensor,
    async_setup_entry,
)
from custom_components.tplink_router_5g.const import DOMAIN


def test_binary_sensor_is_on_best_connection(mock_coordinator, mock_config_entry):
    """Test the optimal connection logic."""
    description = next(d for d in BINARY_SENSORS if d.key == "best_connection")
    sensor = TPLinkRouterBinarySensor(mock_coordinator, mock_config_entry, description)

    # 1. Both active
    mock_coordinator.data = {
        "extra_lte_status": {"endc_support": "1", "nr_dl_mod": "256QAM"}
    }
    assert sensor.is_on is True

    # 2. Only one active
    mock_coordinator.data = {
        "extra_lte_status": {"endc_support": "0", "nr_dl_mod": "256QAM"}
    }
    assert sensor.is_on is False

    # 3. None active
    mock_coordinator.data = {}
    assert sensor.is_on is False


def test_binary_sensor_is_on_endc(mock_coordinator, mock_config_entry):
    """Test ENDC binary sensor logic."""
    description = next(d for d in BINARY_SENSORS if d.key == "endc_support")
    sensor = TPLinkRouterBinarySensor(mock_coordinator, mock_config_entry, description)

    # 1. Active
    mock_coordinator.data = {"extra_lte_status": {"endc_support": "1"}}
    assert sensor.is_on is True

    # 2. Inactive
    mock_coordinator.data = {"extra_lte_status": {"endc_support": "0"}}
    assert sensor.is_on is False


def test_binary_sensor_device_info(mock_coordinator, mock_config_entry):
    """Test device_info links to router."""
    mock_coordinator.mac = None  # Force host fallback
    description = next(d for d in BINARY_SENSORS if d.key == "best_connection")
    sensor = TPLinkRouterBinarySensor(mock_coordinator, mock_config_entry, description)
    info = sensor.device_info
    assert info["identifiers"] == {(DOMAIN, "host_192.168.253.1")}
    assert info["manufacturer"] == "TP-Link"


@pytest.mark.asyncio
async def test_binary_sensor_setup_entry():
    """Test platform setup."""
    hass = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test"
    coordinator = MagicMock()
    hass.data = {DOMAIN: {"test": coordinator}}

    async_add_entities = MagicMock()
    await async_setup_entry(hass, entry, async_add_entities)
    async_add_entities.assert_called_once()
