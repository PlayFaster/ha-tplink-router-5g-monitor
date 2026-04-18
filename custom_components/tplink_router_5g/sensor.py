"""Sensor platform for TP-Link Router 5G."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfDataRate,
    UnitOfInformation,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import TPLinkRouterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class TPLinkSensorEntityDescription(SensorEntityDescription):
    """Describes TP-Link sensor entity."""

    value_fn: Callable[[Any], Any]
    sensor_type: str = "status"
    group: str = "system"
    min_limit: float | None = None
    max_limit: float | None = None


SENSOR_TYPES: Final[tuple[TPLinkSensorEntityDescription, ...]] = (
    # --- System Sub-device ---
    TPLinkSensorEntityDescription(
        key="cpu_used",
        name="CPU Used",
        icon="mdi:cpu-64-bit",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        min_limit=0,
        max_limit=100,
        group="system",
        value_fn=lambda data: (
            (data["status"].cpu_usage * 100)
            if data["status"].cpu_usage is not None
            else None
        ),
    ),
    TPLinkSensorEntityDescription(
        key="memory_used",
        name="Memory Used",
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        min_limit=0,
        max_limit=100,
        group="system",
        value_fn=lambda data: (
            (data["status"].mem_usage * 100)
            if data["status"].mem_usage is not None
            else None
        ),
    ),
    TPLinkSensorEntityDescription(
        key="lte_isp_name",
        name="ISP Name",
        icon="mdi:sim-outline",
        sensor_type="lte_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        group="signal",
        value_fn=lambda data: (
            data["lte_status"].isp_name if data["lte_status"] else None
        ),
    ),
    TPLinkSensorEntityDescription(
        key="sim_status_info",
        name="SIM Status",
        icon="mdi:sim-outline",
        sensor_type="lte_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        group="signal",
        value_fn=lambda data: (
            data["lte_status"].sim_status_info if data["lte_status"] else None
        ),
    ),
    TPLinkSensorEntityDescription(
        key="lan_ipv4_addr",
        name="LAN IPv4 Address",
        icon="mdi:lan",
        entity_category=EntityCategory.DIAGNOSTIC,
        group="system",
        value_fn=lambda data: data["status"].lan_ipv4_addr,
    ),
    TPLinkSensorEntityDescription(
        key="wan_ipv4_addr",
        name="WAN IPv4 Address",
        icon="mdi:wan",
        entity_category=EntityCategory.DIAGNOSTIC,
        group="system",
        value_fn=lambda data: data["status"].wan_ipv4_addr,
    ),
    TPLinkSensorEntityDescription(
        key="wan_ipv4_gateway",
        name="WAN Gateway",
        icon="mdi:router-network",
        entity_category=EntityCategory.DIAGNOSTIC,
        group="system",
        value_fn=lambda data: data["status"].wan_ipv4_gateway,
    ),
    TPLinkSensorEntityDescription(
        key="wan_uptime",
        name="WAN Uptime",
        icon="mdi:clock-start",
        device_class=SensorDeviceClass.TIMESTAMP,
        sensor_type="extra_lte_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        group="system",
        value_fn=lambda data: data["extra_lte_status"].get("wan_uptime"),
    ),
    TPLinkSensorEntityDescription(
        key="primary_dns",
        name="Primary DNS",
        icon="mdi:dns",
        sensor_type="ipv4_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        group="system",
        value_fn=lambda data: (
            data["ipv4_status"].wan_ipv4_pridns if data["ipv4_status"] else None
        ),
    ),
    TPLinkSensorEntityDescription(
        key="secondary_dns",
        name="Secondary DNS",
        icon="mdi:dns",
        sensor_type="ipv4_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        group="system",
        value_fn=lambda data: (
            data["ipv4_status"].wan_ipv4_snddns if data["ipv4_status"] else None
        ),
    ),
    TPLinkSensorEntityDescription(
        key="last_updated",
        name="Last Updated",
        icon="mdi:update",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        group="system",
        value_fn=lambda data: None,  # Handled in native_value
    ),
    # --- Signal Sub-device ---
    TPLinkSensorEntityDescription(
        key="lte_connection_status",
        name="Connection Status",
        icon="mdi:signal-variant",
        sensor_type="lte_status",
        group="signal",
        value_fn=lambda data: (
            {
                0: "Disconnected",
                1: "Connecting",
                2: "Connected",
                3: "Disconnecting",
                4: "Connected",
            }.get(
                data["lte_status"].connect_status,
                f"Unknown ({data['lte_status'].connect_status})",
            )
            if data["lte_status"]
            else None
        ),
    ),
    TPLinkSensorEntityDescription(
        key="lte_network_type",
        name="Network Type",
        icon="mdi:transmission-tower",
        sensor_type="lte_status",
        group="signal",
        value_fn=lambda data: (
            data["lte_status"].network_type_info if data["lte_status"] else None
        ),
    ),
    TPLinkSensorEntityDescription(
        key="registration_status",
        name="Registration Status",
        icon="mdi:tower-fire",
        sensor_type="extra_lte_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        group="signal",
        value_fn=lambda data: data["extra_lte_status"].get("registration_status"),
    ),
    TPLinkSensorEntityDescription(
        key="service_status",
        name="Service Status",
        icon="mdi:cellphone-basic",
        sensor_type="extra_lte_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        group="signal",
        value_fn=lambda data: data["extra_lte_status"].get("service_status"),
    ),
    # --- Data Sub-device ---
    TPLinkSensorEntityDescription(
        key="daily_usage",
        name="Monthly Download",
        icon="mdi:chart-timeline-variant",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        sensor_type="extra_lte_status",
        group="data",
        min_limit=0,
        max_limit=109951162777600,  # 100 TB
        value_fn=lambda data: data["extra_lte_status"].get("daily_usage"),
    ),
    TPLinkSensorEntityDescription(
        key="data_remaining",
        name="Data Remaining",
        icon="mdi:gauge-low",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        sensor_type="extra_lte_status",
        group="data",
        min_limit=0,
        max_limit=109951162777600,  # 100 TB
        value_fn=lambda data: data["extra_lte_status"].get("data_left"),
    ),
    TPLinkSensorEntityDescription(
        key="usage_limit",
        name="Data Limit",
        icon="mdi:gauge",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        sensor_type="extra_lte_status",
        group="data",
        min_limit=0,
        max_limit=109951162777600,  # 100 TB
        value_fn=lambda data: data["extra_lte_status"].get("usage_limit"),
    ),
    TPLinkSensorEntityDescription(
        key="payment_day",
        name="Data Reset Day",
        icon="mdi:calendar-refresh",
        sensor_type="extra_lte_status",
        group="data",
        entity_category=EntityCategory.DIAGNOSTIC,
        min_limit=1,
        max_limit=31,
        value_fn=lambda data: data["extra_lte_status"].get("payment_day"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_total_statistics",
        name="Monthly Usage",
        icon="mdi:sim-outline",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        sensor_type="lte_status",
        group="data",
        value_fn=lambda data: (
            data["lte_status"].total_statistics if data["lte_status"] else None
        ),
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
        value_fn=lambda data: (
            data["lte_status"].cur_rx_speed if data["lte_status"] else None
        ),
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
        value_fn=lambda data: (
            data["lte_status"].cur_tx_speed if data["lte_status"] else None
        ),
    ),
    # --- SMS Sub-device ---
    TPLinkSensorEntityDescription(
        key="lte_sms_unread_count",
        name="Unread SMS",
        icon="mdi:email-outline",
        state_class=SensorStateClass.TOTAL,
        sensor_type="lte_status",
        group="sms",
        value_fn=lambda data: (
            data["lte_status"].sms_unread_count if data["lte_status"] else None
        ),
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
    # --- Home Network Sub-device ---
    TPLinkSensorEntityDescription(
        key="clients_total",
        name="Total Clients",
        icon="mdi:account-multiple",
        state_class=SensorStateClass.TOTAL,
        group="home_network",
        value_fn=lambda data: data["status"].clients_total,
    ),
    TPLinkSensorEntityDescription(
        key="wifi_clients_total",
        name="Total Main Wi-Fi Clients",
        icon="mdi:wifi",
        state_class=SensorStateClass.TOTAL,
        group="home_network",
        value_fn=lambda data: data["status"].wifi_clients_total,
    ),
    TPLinkSensorEntityDescription(
        key="guest_wifi_clients_total",
        name="Total Guest Wi-Fi Clients",
        icon="mdi:wifi",
        state_class=SensorStateClass.TOTAL,
        group="home_network",
        value_fn=lambda data: data["status"].guest_clients_total,
    ),
    TPLinkSensorEntityDescription(
        key="iot_clients_total",
        name="Total IoT Clients",
        icon="mdi:wifi",
        state_class=SensorStateClass.TOTAL,
        group="home_network",
        value_fn=lambda data: data["status"].iot_clients_total,
    ),
    TPLinkSensorEntityDescription(
        key="wired_clients_total",
        name="Total Wired Clients",
        icon="mdi:lan-connect",
        state_class=SensorStateClass.TOTAL,
        group="home_network",
        value_fn=lambda data: data["status"].wired_total,
    ),
)

EXTRA_LTE_SENSOR_TYPES: Final[tuple[TPLinkSensorEntityDescription, ...]] = (
    # --- 5G Metrics (Signal Sub-device) ---
    TPLinkSensorEntityDescription(
        key="nr_rsrp",
        name="5G RSRP",
        icon="mdi:signal-cellular-3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=-140,
        max_limit=-40,
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
        group="signal",
        min_limit=-125,
        max_limit=-20,
        value_fn=lambda data: data["extra_lte_status"].get("nr_rssi"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_rsrq",
        name="5G RSRQ",
        icon="mdi:signal-cellular-3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="dB",
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=-25,
        max_limit=0,
        value_fn=lambda data: data["extra_lte_status"].get("nr_rsrq"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_snr",
        name="5G SNR",
        icon="mdi:signal-cellular-3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="dB",
        suggested_display_precision=1,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=-10,
        max_limit=45,
        value_fn=lambda data: (
            0.1 * int(data["extra_lte_status"].get("nr_snr"))
            if data["extra_lte_status"].get("nr_snr")
            else None
        ),
    ),
    TPLinkSensorEntityDescription(
        key="nr_signal_pct",
        name="5G Signal Strength",
        icon="mdi:signal",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=0,
        max_limit=100,
        value_fn=lambda data: data["extra_lte_status"].get("nr_signal_pct"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_band",
        name="5G Band",
        icon="mdi:radio-tower",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: (
            f"N{data['extra_lte_status'].get('nr_band')}"
            if data["extra_lte_status"].get("nr_band")
            else None
        ),
    ),
    TPLinkSensorEntityDescription(
        key="nr_dl_mod",
        name="5G DL Modulation",
        icon="mdi:speedometer",
        sensor_type="extra_lte_status",
        group="signal",
        value_fn=lambda data: data["extra_lte_status"].get("nr_dl_mod"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_ul_mod",
        name="5G UL Modulation",
        icon="mdi:speedometer",
        sensor_type="extra_lte_status",
        group="signal",
        value_fn=lambda data: data["extra_lte_status"].get("nr_ul_mod"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_dl_mcs",
        name="5G DL MCS",
        icon="mdi:numeric",
        state_class=SensorStateClass.MEASUREMENT,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=0,
        max_limit=31,
        value_fn=lambda data: data["extra_lte_status"].get("nr_dl_mcs"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_ul_mcs",
        name="5G UL MCS",
        icon="mdi:numeric",
        state_class=SensorStateClass.MEASUREMENT,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=0,
        max_limit=31,
        value_fn=lambda data: data["extra_lte_status"].get("nr_ul_mcs"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_dl_bw",
        name="5G Downlink Bandwidth",
        icon="mdi:arrow-expand-horizontal",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="MHz",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("nr_dl_bw"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_ul_bw",
        name="5G Uplink Bandwidth",
        icon="mdi:arrow-expand-horizontal",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="MHz",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("nr_ul_bw"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_dl_freq",
        name="5G Downlink Frequency",
        icon="mdi:waveform",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="MHz",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("nr_dl_freq"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_ul_freq",
        name="5G Uplink Frequency",
        icon="mdi:waveform",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="MHz",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        min_limit=100,
        value_fn=lambda data: data["extra_lte_status"].get("nr_ul_freq"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_cqi",
        name="5G CQI",
        icon="mdi:quality-high",
        state_class=SensorStateClass.MEASUREMENT,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=1,
        max_limit=15,
        value_fn=lambda data: data["extra_lte_status"].get("nr_cqi"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_tx_power",
        name="5G Transmit Power",
        icon="mdi:transmission-tower-export",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="dBm",
        suggested_display_precision=1,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=-40,
        max_limit=25,
        value_fn=lambda data: (
            0.1 * int(data["extra_lte_status"].get("nr_tx_power"))
            if data["extra_lte_status"].get("nr_tx_power") is not None
            else None
        ),
    ),
    TPLinkSensorEntityDescription(
        key="nr_rbs",
        name="5G Resource Blocks",
        icon="mdi:office-building-marker",
        state_class=SensorStateClass.MEASUREMENT,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=0,
        max_limit=273,
        value_fn=lambda data: data["extra_lte_status"].get("nr_rbs"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_pci",
        name="5G PCI",
        icon="mdi:transmission-tower",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        min_limit=0,
        max_limit=1007,
        value_fn=lambda data: data["extra_lte_status"].get("nr_pci"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_tac",
        name="5G TAC",
        icon="mdi:transmission-tower",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        min_limit=1,
        value_fn=lambda data: data["extra_lte_status"].get("nr_tac"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_cid",
        name="5G Cell ID",
        icon="mdi:transmission-tower",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        min_limit=1,
        value_fn=lambda data: data["extra_lte_status"].get("nr_cid"),
    ),
    TPLinkSensorEntityDescription(
        key="nr_arfcn",
        name="5G ARFCN",
        icon="mdi:radio-tower",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("nr_arfcn"),
    ),
    # --- LTE Anchor Metrics (Signal Sub-device) ---
    TPLinkSensorEntityDescription(
        key="lte_anchor_rsrp",
        name="LTE Anchor RSRP",
        icon="mdi:signal-cellular-2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=-140,
        max_limit=-40,
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
        group="signal",
        min_limit=-120,
        max_limit=-20,
        value_fn=lambda data: data["extra_lte_status"].get("lte_rssi"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_rsrq",
        name="LTE Anchor RSRQ",
        icon="mdi:signal-cellular-2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="dB",
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=-25,
        max_limit=0,
        value_fn=lambda data: data["extra_lte_status"].get("lte_rsrq"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_snr",
        name="LTE Anchor SNR",
        icon="mdi:signal-cellular-2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="dB",
        suggested_display_precision=1,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=-10,
        max_limit=45,
        value_fn=lambda data: (
            0.1 * int(data["extra_lte_status"].get("lte_snr"))
            if data["extra_lte_status"].get("lte_snr") is not None
            else None
        ),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_signal_pct",
        name="LTE Anchor Signal Strength",
        icon="mdi:signal",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=0,
        max_limit=100,
        value_fn=lambda data: data["extra_lte_status"].get("lte_signal_pct"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_band",
        name="LTE Anchor Band",
        icon="mdi:radio-tower",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: (
            f"B{data['extra_lte_status'].get('lte_band')}"
            if data["extra_lte_status"].get("lte_band")
            else None
        ),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_dl_bw",
        name="LTE Anchor Downlink Bandwidth",
        icon="mdi:arrow-expand-horizontal",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="MHz",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("lte_dl_bw"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_ul_bw",
        name="LTE Anchor Uplink Bandwidth",
        icon="mdi:arrow-expand-horizontal",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="MHz",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("lte_ul_bw"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_dl_freq",
        name="LTE Downlink Frequency",
        icon="mdi:waveform",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="MHz",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("lte_dl_freq"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_ul_freq",
        name="LTE Uplink Frequency",
        icon="mdi:waveform",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="MHz",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("lte_ul_freq"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_dl_mcs",
        name="LTE DL MCS",
        icon="mdi:numeric",
        state_class=SensorStateClass.MEASUREMENT,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=0,
        max_limit=31,
        value_fn=lambda data: data["extra_lte_status"].get("lte_dl_mcs"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_ul_mcs",
        name="LTE UL MCS",
        icon="mdi:numeric",
        state_class=SensorStateClass.MEASUREMENT,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=0,
        max_limit=31,
        value_fn=lambda data: data["extra_lte_status"].get("lte_ul_mcs"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_dl_mod",
        name="LTE DL Modulation",
        icon="mdi:speedometer",
        sensor_type="extra_lte_status",
        group="signal",
        value_fn=lambda data: data["extra_lte_status"].get("lte_dl_mod"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_ul_mod",
        name="LTE UL Modulation",
        icon="mdi:speedometer",
        sensor_type="extra_lte_status",
        group="signal",
        value_fn=lambda data: data["extra_lte_status"].get("lte_ul_mod"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_cqi",
        name="LTE CQI",
        icon="mdi:quality-high",
        state_class=SensorStateClass.MEASUREMENT,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=1,
        max_limit=15,
        value_fn=lambda data: data["extra_lte_status"].get("lte_cqi"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_ri",
        name="LTE RI",
        icon="mdi:numeric",
        state_class=SensorStateClass.MEASUREMENT,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=1,
        max_limit=4,
        value_fn=lambda data: data["extra_lte_status"].get("lte_ri"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_pmi",
        name="LTE PMI",
        icon="mdi:numeric",
        state_class=SensorStateClass.MEASUREMENT,
        sensor_type="extra_lte_status",
        group="signal",
        value_fn=lambda data: data["extra_lte_status"].get("lte_pmi"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_tbs",
        name="LTE TBS",
        icon="mdi:numeric",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="bits",
        sensor_type="extra_lte_status",
        group="signal",
        value_fn=lambda data: data["extra_lte_status"].get("lte_tbs"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_tx_power",
        name="LTE Transmit Power",
        icon="mdi:transmission-tower-export",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="dBm",
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=-40,
        max_limit=25,
        value_fn=lambda data: data["extra_lte_status"].get("lte_tx_power"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_rbs",
        name="LTE Resource Blocks",
        icon="mdi:office-building-marker",
        state_class=SensorStateClass.MEASUREMENT,
        sensor_type="extra_lte_status",
        group="signal",
        min_limit=0,
        max_limit=100,
        value_fn=lambda data: data["extra_lte_status"].get("lte_rbs"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_pci",
        name="LTE Anchor PCI",
        icon="mdi:transmission-tower",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        min_limit=0,
        max_limit=1007,
        value_fn=lambda data: data["extra_lte_status"].get("lte_pci"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_tac",
        name="LTE Anchor TAC",
        icon="mdi:transmission-tower",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        min_limit=1,
        value_fn=lambda data: data["extra_lte_status"].get("lte_tac"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_cid",
        name="LTE Anchor Cell ID",
        icon="mdi:transmission-tower",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        min_limit=1,
        value_fn=lambda data: data["extra_lte_status"].get("lte_cid"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_arfcn",
        name="LTE Anchor E-ARFCN",
        icon="mdi:radio-tower",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        min_limit=1,
        max_limit=3300000,
        value_fn=lambda data: data["extra_lte_status"].get("lte_arfcn"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_node_b_id",
        name="LTE Anchor NodeB ID",
        icon="mdi:transmission-tower",
        sensor_type="extra_lte_status",
        group="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("lte_node_b_id"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: TPLinkRouterDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in SENSOR_TYPES:
        entities.append(TPLinkRouterSensor(coordinator, entry, description))

    for description in EXTRA_LTE_SENSOR_TYPES:
        entities.append(TPLinkRouterSensor(coordinator, entry, description))

    async_add_entities(entities)


class TPLinkRouterSensor(
    CoordinatorEntity[TPLinkRouterDataUpdateCoordinator], SensorEntity
):
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

        description = self.entity_description
        key = description.key

        # Special case: Last Updated
        if key == "last_updated":
            return self.coordinator.last_update_success_time

        # Special case: Stable Timestamp for Uptime
        if key == "wan_uptime":
            try:
                uptime_seconds = description.value_fn(self.coordinator.data)
                if uptime_seconds is not None:
                    seconds = int(float(uptime_seconds))
                    boot_time = dt_util.now() - timedelta(seconds=seconds)
                    return boot_time.replace(second=0, microsecond=0)
            except (ValueError, TypeError):
                return None

        try:
            value = description.value_fn(self.coordinator.data)
        except (KeyError, AttributeError):
            return None

        if value is None:
            return None

        # Apply Guard Bands (Option C)
        if isinstance(value, int | float):
            if description.min_limit is not None and value < description.min_limit:
                _LOGGER.debug(
                    "Sensor %s value %s below min_limit %s",
                    key,
                    value,
                    description.min_limit,
                )
                return None
            if description.max_limit is not None and value > description.max_limit:
                _LOGGER.debug(
                    "Sensor %s value %s above max_limit %s",
                    key,
                    value,
                    description.max_limit,
                )
                return None

        return value

    @property
    def device_info(self):
        """Return device information with sub-device support."""
        host = self._entry.options[CONF_HOST]
        group = self.entity_description.group

        group_names = {
            "system": "System",
            "signal": "Signal",
            "home_network": "Home Network",
            "data": "Data",
            "sms": "SMS",
        }
        display_group = group_names.get(group, group.capitalize())
        # Option B: Root is "[Name] System", others are "[Name] [Group]"
        sub_name = f"{self._entry.title} {display_group}"

        sub_id_prefix = self.coordinator.mac if self.coordinator.mac else f"host_{host}"

        info = {
            "identifiers": {(DOMAIN, f"{sub_id_prefix}_{group}")},
            "name": sub_name,
            "manufacturer": "TP-Link",
            "model": self.coordinator.model,
            "sw_version": self.coordinator.sw_version,
            "hw_version": self.coordinator.hw_version,
            "configuration_url": f"http://{host}",
        }

        # Link all sub-devices to the "System" root device
        if group != "system":
            info["via_device"] = (DOMAIN, f"{sub_id_prefix}_system")

        return info
