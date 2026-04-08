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
    mock_coordinator.model = "NX510v"
    mock_coordinator.sw_version = "1.0.0"

    description = next(d for d in SENSOR_TYPES if d.key == "cpu_used")
    sensor = TPLinkRouterSensor(mock_coordinator, mock_config_entry, description)
    info = sensor.device_info
    assert info["identifiers"] == {(DOMAIN, "host_192.168.253.1_system")}
    assert info["manufacturer"] == "TP-Link"
    assert info["model"] == "NX510v"
    assert info["sw_version"] == "1.0.0"

    description_data = next(d for d in SENSOR_TYPES if d.key == "daily_usage")
    sensor_data = TPLinkRouterSensor(
        mock_coordinator, mock_config_entry, description_data
    )
    info_data = sensor_data.device_info
    assert info_data["identifiers"] == {(DOMAIN, "host_192.168.253.1_data")}


def test_sensor_last_updated(mock_coordinator, mock_config_entry):
    """Test the last updated sensor."""
    from homeassistant.util import dt as dt_util

    now = dt_util.now()
    mock_coordinator.last_update_success_time = now
    mock_coordinator.data = {"status": MagicMock()}

    description = next(d for d in SENSOR_TYPES if d.key == "last_updated")
    sensor = TPLinkRouterSensor(mock_coordinator, mock_config_entry, description)
    assert sensor.native_value == now


def test_sensor_ipv4_status(mock_coordinator, mock_config_entry):
    """Test IPv4 status sensor extraction."""
    mock_coordinator.data = {"ipv4_status": MagicMock(wan_ipv4_pridns="8.8.8.8")}
    description = next(d for d in SENSOR_TYPES if d.key == "primary_dns")
    sensor = TPLinkRouterSensor(mock_coordinator, mock_config_entry, description)
    assert sensor.native_value == "8.8.8.8"


def test_sensor_no_data(mock_coordinator, mock_config_entry):
    """Test sensor behavior when no data is available."""
    mock_coordinator.data = None
    description = next(d for d in SENSOR_TYPES if d.key == "cpu_used")
    sensor = TPLinkRouterSensor(mock_coordinator, mock_config_entry, description)
    assert sensor.native_value is None


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
