"""Tests for the TP-Link Router sensor."""

from unittest.mock import MagicMock

import pytest

from custom_components.tplink_router_5g.const import DOMAIN
from custom_components.tplink_router_5g.sensor import (
    EXTRA_LTE_SENSOR_TYPES,
    SENSOR_TYPES,
    TPLinkRouterSensor,
    async_setup_entry,
)


def test_sensor_native_value(mock_coordinator, mock_config_entry):
    """Test standard technical sensor extraction."""
    mock_coordinator.data = {"status": MagicMock(cpu_usage=0.5)}
    description = next(d for d in SENSOR_TYPES if d.key == "cpu_used")
    sensor = TPLinkRouterSensor(mock_coordinator, mock_config_entry, description)

    assert sensor.native_value == 50.0


def test_sensor_lte_extra_value(mock_coordinator, mock_config_entry):
    """Test extra LTE sensor extraction."""
    mock_coordinator.data = {"extra_lte_status": {"nr_rsrp": -80}}
    description = next(d for d in EXTRA_LTE_SENSOR_TYPES if d.key == "nr_rsrp")
    sensor = TPLinkRouterSensor(mock_coordinator, mock_config_entry, description)

    assert sensor.native_value == -80


def test_sensor_device_info(mock_coordinator, mock_config_entry):
    """Test device_info for main and sub devices."""
    mock_coordinator.mac = None  # Force host fallback
    description = next(d for d in SENSOR_TYPES if d.key == "cpu_used")
    sensor = TPLinkRouterSensor(mock_coordinator, mock_config_entry, description)
    info = sensor.device_info
    assert info["identifiers"] == {(DOMAIN, "host_192.168.253.1")}
    assert info["manufacturer"] == "TP-Link"

    description_data = next(d for d in SENSOR_TYPES if d.key == "daily_usage")
    sensor_data = TPLinkRouterSensor(
        mock_coordinator, mock_config_entry, description_data
    )
    info_data = sensor_data.device_info
    assert info_data["identifiers"] == {(DOMAIN, "host_192.168.253.1_data")}


@pytest.mark.asyncio
async def test_sensor_setup_entry():
    """Test platform setup."""
    hass = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test"
    hass.data = {DOMAIN: {"test": MagicMock()}}

    async_add_entities = MagicMock()
    await async_setup_entry(hass, entry, async_add_entities)
    async_add_entities.assert_called_once()
