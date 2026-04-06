"""Sensor platform for TP-Link Router 5G."""

from dataclasses import dataclass
from collections.abc import Callable
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
    
    # --- Main Device: Connection Metrics ---
    TPLinkSensorEntityDescription(
        key="lte_network_type",
        name="Network Type",
        icon="mdi:transmission-tower",
        sensor_type="lte_status",
        value_fn=lambda data: data["lte_status"].network_type_info if data["lte_status"] else None,
    ),

    # --- Data Sub-device ---
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
        key="wired_clients_total",
        name="Total Wired Clients",
        icon="mdi:lan-connect",
        state_class=SensorStateClass.TOTAL,
        group="clients",
        value_fn=lambda data: data["status"].wired_total,
    ),
)

EXTRA_LTE_SENSOR_TYPES: Final[tuple[TPLinkSensorEntityDescription, ...]] = (
    # --- Main Device: 5G Metrics ---
    TPLinkSensorEntityDescription(
        key="nr_rsrp",
        name="5G RSRP",
        icon="mdi:signal-cellular-3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        sensor_type="extra_lte_status",
        value_fn=lambda data: data["extra_lte_status"].get("nr_rsrp"),
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
        icon="mdi:antenna-tower",
        sensor_type="extra_lte_status",
        value_fn=lambda data: f"N{data['extra_lte_status'].get('nr_band')}" if data["extra_lte_status"].get("nr_band") else None,
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
        key="lte_anchor_rsrp",
        name="LTE Anchor RSRP",
        icon="mdi:signal-cellular-2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        sensor_type="extra_lte_status",
        value_fn=lambda data: data["extra_lte_status"].get("lte_rsrp"),
    ),
    TPLinkSensorEntityDescription(
        key="lte_anchor_band",
        name="LTE Anchor Band",
        icon="mdi:antenna-tower",
        sensor_type="extra_lte_status",
        value_fn=lambda data: f"B{data['extra_lte_status'].get('lte_band')}" if data["extra_lte_status"].get("lte_band") else None,
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

    @property
    def native_value(self):
        """Return the value of the sensor."""
        if not self.coordinator.data:
            return None
        try:
            return self.entity_description.value_fn(self.coordinator.data)
        except (KeyError, AttributeError):
            return None

    @property
    def device_info(self):
        """Return device information with sub-device support."""
        host = self._entry.options[CONF_HOST]
        group = self.entity_description.group
        
        if group == "main":
            return {
                "identifiers": {(DOMAIN, host)},
                "name": self._entry.title,
                "manufacturer": "TP-Link",
                "model": self.coordinator.firmware.model if self.coordinator.firmware else "5G Router",
                "sw_version": self.coordinator.firmware.firmware_version if self.coordinator.firmware else None,
                "hw_version": self.coordinator.firmware.hardware_version if self.coordinator.firmware else None,
                "configuration_url": f"http://{host}",
            }
            
        # Sub-device naming logic
        sub_name = f"{self._entry.title} {group.capitalize()}"
        return {
            "identifiers": {(DOMAIN, f"{host}_{group}")},
            "name": sub_name,
            "manufacturer": "TP-Link",
            "via_device": (DOMAIN, host),
        }
