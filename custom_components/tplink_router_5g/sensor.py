"""Sensor platform for TP-Link Router 5G."""

from dataclasses import dataclass
from collections.abc import Callable
from datetime import timedelta
from typing import Any, Final
import logging

from homeassistant.components.sensor import (
    SensorStateClass,
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
)
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfDataRate,
    UnitOfInformation,
    CONF_HOST,
    EntityCategory,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import TPLinkRouterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True, kw_only=True)
class TPLinkSensorEntityDescription(SensorEntityDescription):
    """Describes TP-Link sensor entity."""
    value_fn: Callable[[Any], Any]
    sensor_type: str = "status"
    group: str = "main"

SENSOR_TYPES: Final[tuple[TPLinkSensorEntityDescription, ...]] = (
    # --- Main Device: Diagnostics ---
    TPLinkSensorEntityDescription(
        key="cpu_used",
        name="CPU Used",
        icon="mdi:cpu-64-bit",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: (data["status"].cpu_usage * 100) if data["status"].cpu_usage is not None else None,
    ),
    TPLinkSensorEntityDescription(
        key="memory_used",
        name="Memory Used",
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: (data["status"].mem_usage * 100) if data["status"].mem_usage is not None else None,
    ),
    TPLinkSensorEntityDescription(
        key="lte_isp_name",
        name="ISP Name",
        icon="mdi:sim-outline",
        sensor_type="lte_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["lte_status"].isp_name if data["lte_status"] else None,
    ),
    TPLinkSensorEntityDescription(
        key="sim_status_info",
        name="SIM Status",
        icon="mdi:sim-outline",
        sensor_type="lte_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["lte_status"].sim_status_info if data["lte_status"] else None,
    ),
    TPLinkSensorEntityDescription(
        key="lan_ipv4_addr",
        name="LAN IPv4 Address",
        icon="mdi:lan",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["status"].lan_ipv4_addr,
    ),
    TPLinkSensorEntityDescription(
        key="wan_ipv4_addr",
        name="WAN IPv4 Address",
        icon="mdi:wan",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["status"].wan_ipv4_addr,
    ),
    TPLinkSensorEntityDescription(
        key="wan_ipv4_gateway",
        name="WAN Gateway",
        icon="mdi:router-network",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["status"].wan_ipv4_gateway,
    ),
    TPLinkSensorEntityDescription(
        key="primary_dns",
        name="Primary DNS",
        icon="mdi:dns",
        sensor_type="ipv4_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["ipv4_status"].wan_ipv4_pridns if data["ipv4_status"] else None,
    ),
    TPLinkSensorEntityDescription(
        key="secondary_dns",
        name="Secondary DNS",
        icon="mdi:dns",
        sensor_type="ipv4_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["ipv4_status"].wan_ipv4_snddns if data["ipv4_status"] else None,
    ),
    TPLinkSensorEntityDescription(
        key="last_updated",
        name="Last Updated",
        icon="mdi:update",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: None, # Handled in native_value
    ),
    
    # --- Main Device: Connection Metrics ---
    TPLinkSensorEntityDescription(
        key="lte_connection_status",
        name="Connection Status",
        icon="mdi:signal-variant",
        sensor_type="lte_status",
        value_fn=lambda data: {
            0: "Disconnected",
            1: "Connecting",
            2: "Connected",
            3: "Disconnecting",
            4: "Connected",
        }.get(data["lte_status"].connect_status, f"Unknown ({data['lte_status'].connect_status})") if data["lte_status"] else None,
    ),
    TPLinkSensorEntityDescription(
        key="lte_network_type",
        name="Network Type",
        icon="mdi:transmission-tower",
        sensor_type="lte_status",
        value_fn=lambda data: data["lte_status"].network_type_info if data["lte_status"] else None,
    ),

    # --- Data Sub-device ---
    TPLinkSensorEntityDescription(
        key="daily_usage",
        name="Daily Data Usage",
        icon="mdi:chart-timeline-variant",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        sensor_type="extra_lte_status",
        group="data",
        value_fn=lambda data: data["extra_lte_status"].get("daily_usage"),
    ),
    TPLinkSensorEntityDescription(
        key="usage_limit",
        name="Data Limit",
        icon="mdi:gauge",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        sensor_type="extra_lte_status",
        group="data",
        value_fn=lambda data: data["extra_lte_status"].get("usage_limit"),
    ),
    TPLinkSensorEntityDescription(
        key="payment_day",
        name="Data Reset Day",
        icon="mdi:calendar-refresh",
        sensor_type="extra_lte_status",
        group="data",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("payment_day"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_total_statistics",
        name="Total Data Statistics",
        icon="mdi:sim-outline",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        sensor_type="lte_status",
        group="data",
        value_fn=lambda data: data["lte_status"].total_statistics if data["lte_status"] else None,
    ),
    TPLinkSensorEntityDescription(
        key="lte_cur_rx_speed",
        name="Current Download Speed",
        icon="mdi:download",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        sensor_type="lte_status",
        group="data",
        value_fn=lambda data: data["lte_status"].cur_rx_speed if data["lte_status"] else None,
    ),
    TPLinkSensorEntityDescription(
        key="lte_cur_tx_speed",
        name="Current Upload Speed",
        icon="mdi:upload",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        sensor_type="lte_status",
        group="data",
        value_fn=lambda data: data["lte_status"].cur_tx_speed if data["lte_status"] else None,
    ),

    # --- SMS Sub-device ---
    TPLinkSensorEntityDescription(
        key="lte_sms_unread_count",
        name="Unread SMS",
        icon="mdi:email-outline",
        state_class=SensorStateClass.TOTAL,
        sensor_type="lte_status",
        group="sms",
        value_fn=lambda data: data["lte_status"].sms_unread_count if data["lte_status"] else None,
    ),
    TPLinkSensorEntityDescription(
        key="sms_send_result",
        name="Last SMS Send Result",
        icon="mdi:email-check-outline",
        sensor_type="extra_lte_status",
        group="sms",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("sms_send_result"),
    ),
    TPLinkSensorEntityDescription(
        key="sms_send_cause",
        name="Last SMS Send Cause",
        icon="mdi:email-alert-outline",
        sensor_type="extra_lte_status",
        group="sms",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("sms_send_cause"),
    ),

    # --- Clients Sub-device ---
    TPLinkSensorEntityDescription(
        key="clients_total",
        name="Total Clients",
        icon="mdi:account-multiple",
        state_class=SensorStateClass.TOTAL,
        group="clients",
        value_fn=lambda data: data["status"].clients_total,
    ),
    TPLinkSensorEntityDescription(
        key="wifi_clients_total",
        name="Total Main Wi-Fi Clients",
        icon="mdi:wifi",
        state_class=SensorStateClass.TOTAL,
        group="clients",
        value_fn=lambda data: data["status"].wifi_clients_total,
    ),
    TPLinkSensorEntityDescription(
        key="guest_wifi_clients_total",
        name="Total Guest Wi-Fi Clients",
        icon="mdi:wifi",
        state_class=SensorStateClass.TOTAL,
        group="clients",
        value_fn=lambda data: data["status"].guest_clients_total,
    ),
    TPLinkSensorEntityDescription(
        key="iot_clients_total",
        name="Total IoT Clients",
        icon="mdi:wifi",
        state_class=SensorStateClass.TOTAL,
        group="clients",
        value_fn=lambda data: data["status"].iot_clients_total,
    ),
    TPLinkSensorEntityDescription(
        key="wired_clients_total",
        name="Total Wired Clients",
        icon="mdi:lan-connect",
        state_class=SensorStateClass.TOTAL,
        group="clients",
        value_fn=lambda data: data["status"].wired_total,
    ),
)

EXTRA_LTE_SENSOR_TYPES: Final[tuple[TPLinkSensorEntityDescription, ...]] = (
    # --- 5G Metrics ---
    TPLinkSensorEntityDescription(
        key="nr_rsrp",
        name="5G RSRP",
        icon="mdi:signal-cellular-3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        sensor_type="extra_lte_status",
        value_fn=lambda data: data["extra_lte_status"].get("nr_rsrp"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_rssi",
        name="5G RSSI",
        icon="mdi:signal-cellular-3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        sensor_type="extra_lte_status",
        value_fn=lambda data: data["extra_lte_status"].get("nr_rssi"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_rsrq",
        name="5G RSRQ",
        icon="mdi:signal-cellular-3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="dB",
        sensor_type="extra_lte_status",
        value_fn=lambda data: data["extra_lte_status"].get("nr_rsrq"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_snr",
        name="5G SNR",
        icon="mdi:signal-cellular-3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="dB",
        sensor_type="extra_lte_status",
        value_fn=lambda data: 0.1 * int(data["extra_lte_status"].get("nr_snr")) if data["extra_lte_status"].get("nr_snr") else None,
    ),
    TPLinkSensorEntityDescription(
        key="nr_band",
        name="5G Band",
        icon="mdi:radio-tower",
        sensor_type="extra_lte_status",
        value_fn=lambda data: f"N{data['extra_lte_status'].get('nr_band')}" if data["extra_lte_status"].get('nr_band') else None,
    ),
    TPLinkSensorEntityDescription(
        key="nr_dl_mod",
        name="5G DL Modulation",
        icon="mdi:speedometer",
        sensor_type="extra_lte_status",
        value_fn=lambda data: data["extra_lte_status"].get("nr_dl_mod"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_ul_mod",
        name="5G UL Modulation",
        icon="mdi:speedometer",
        sensor_type="extra_lte_status",
        value_fn=lambda data: data["extra_lte_status"].get("nr_ul_mod"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_bw",
        name="5G Bandwidth",
        icon="mdi:arrow-expand-horizontal",
        sensor_type="extra_lte_status",
        value_fn=lambda data: f"{data['extra_lte_status'].get('nr_dl_bw')}MHz" if data["extra_lte_status"].get('nr_dl_bw') else None,
    ),
    TPLinkSensorEntityDescription(
        key="nr_cqi",
        name="5G CQI",
        icon="mdi:quality-high",
        state_class=SensorStateClass.MEASUREMENT,
        sensor_type="extra_lte_status",
        value_fn=lambda data: data["extra_lte_status"].get("nr_cqi"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_tx_power",
        name="5G Transmit Power",
        icon="mdi:transmission-tower-export",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="dBm",
        sensor_type="extra_lte_status",
        value_fn=lambda data: data["extra_lte_status"].get("nr_tx_power"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_rbs",
        name="5G Resource Blocks",
        icon="mdi:office-building-marker",
        state_class=SensorStateClass.MEASUREMENT,
        sensor_type="extra_lte_status",
        value_fn=lambda data: data["extra_lte_status"].get("nr_rbs"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_pci",
        name="5G PCI",
        icon="mdi:transmission-tower",
        sensor_type="extra_lte_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("nr_pci"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_tac",
        name="5G TAC",
        icon="mdi:transmission-tower",
        sensor_type="extra_lte_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("nr_tac"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_cid",
        name="5G Cell ID",
        icon="mdi:transmission-tower",
        sensor_type="extra_lte_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("nr_cid"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_arfcn",
        name="5G ARFCN",
        icon="mdi:radio-tower",
        sensor_type="extra_lte_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("nr_arfcn"),
    ),

    # --- LTE Anchor Metrics ---
    TPLinkSensorEntityDescription(
        key="lte_anchor_rsrp",
        name="LTE Anchor RSRP",
        icon="mdi:signal-cellular-2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        sensor_type="extra_lte_status",
        value_fn=lambda data: data["extra_lte_status"].get("lte_rsrp"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_rssi",
        name="LTE Anchor RSSI",
        icon="mdi:signal-cellular-2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        sensor_type="extra_lte_status",
        value_fn=lambda data: data["extra_lte_status"].get("lte_rssi"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_rsrq",
        name="LTE Anchor RSRQ",
        icon="mdi:signal-cellular-2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="dB",
        sensor_type="extra_lte_status",
        value_fn=lambda data: data["extra_lte_status"].get("lte_rsrq"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_band",
        name="LTE Anchor Band",
        icon="mdi:radio-tower",
        sensor_type="extra_lte_status",
        value_fn=lambda data: f"B{data['extra_lte_status'].get('lte_band')}" if data["extra_lte_status"].get('lte_band') else None,
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_bw",
        name="LTE Anchor Bandwidth",
        icon="mdi:arrow-expand-horizontal",
        sensor_type="extra_lte_status",
        value_fn=lambda data: f"{data['extra_lte_status'].get('lte_dl_bw')}MHz" if data["extra_lte_status"].get('lte_dl_bw') else None,
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_pci",
        name="LTE Anchor PCI",
        icon="mdi:transmission-tower",
        sensor_type="extra_lte_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("lte_pci"),
    ),
)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor platform."""
    coordinator: TPLinkRouterDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for description in SENSOR_TYPES:
        entities.append(TPLinkRouterSensor(coordinator, entry, description))
        
    for description in EXTRA_LTE_SENSOR_TYPES:
        entities.append(TPLinkRouterSensor(coordinator, entry, description))
        
    async_add_entities(entities)

class TPLinkRouterSensor(CoordinatorEntity[TPLinkRouterDataUpdateCoordinator], SensorEntity):
    """Representation of a TP-Link Router sensor."""

    _attr_has_entity_name = True
    entity_description: TPLinkSensorEntityDescription

    def __init__(self, coordinator, entry, description):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        if description.icon:
            self._attr_icon = description.icon

    @property
    def native_value(self):
        """Return the value of the sensor."""
        if not self.coordinator.data:
            return None
        
        key = self.entity_description.key
        
        # Special case: Last Updated
        if key == "last_updated":
            return self.coordinator.last_update_success_time

        try:
            return self.entity_description.value_fn(self.coordinator.data)
        except (KeyError, AttributeError):
            return None

    @property
    def device_info(self):
        """Return device information with sub-device support."""
        host = self._entry.options[CONF_HOST]
        group = self.entity_description.group
        
        main_identifiers = {(DOMAIN, self.coordinator.mac)} if self.coordinator.mac else {(DOMAIN, host)}
        
        if group == "main":
            connections = {(CONNECTION_NETWORK_MAC, self.coordinator.mac)} if self.coordinator.mac else set()
            return {
                "identifiers": main_identifiers,
                "connections": connections,
                "name": self._entry.title,
                "manufacturer": "TP-Link",
                "model": self.coordinator.firmware.model if self.coordinator.firmware else "NX510v",
                "sw_version": self.coordinator.firmware.firmware_version if self.coordinator.firmware else None,
                "hw_version": self.coordinator.firmware.hardware_version if self.coordinator.firmware else None,
                "configuration_url": f"http://{host}",
            }
            
        # Sub-device naming logic
        group_names = {
            "sms": "SMS",
            "wifi": "Wi-Fi",
            "data": "Data",
            "clients": "Clients",
        }
        display_group = group_names.get(group, group.capitalize())
        sub_name = f"{self._entry.title} {display_group}"
        
        # Consistent sub-device identifier using host/mac as prefix
        sub_id_prefix = self.coordinator.mac if self.coordinator.mac else host
        
        return {
            "identifiers": {(DOMAIN, f"{sub_id_prefix}_{group}")},
            "name": sub_name,
            "manufacturer": "TP-Link",
            "via_device": list(main_identifiers)[0],
        }
