"""Binary sensor platform for TP-Link Router 5G."""

from dataclasses import dataclass
from collections.abc import Callable
from typing import Any, Final

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)
from homeassistant.const import CONF_HOST, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

from .const import DOMAIN
from .coordinator import TPLinkRouterDataUpdateCoordinator

@dataclass(frozen=True, kw_only=True)
class TPLinkBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes TP-Link binary sensor entity."""
    value_fn: Callable[[Any], bool]

BINARY_SENSORS: Final[tuple[TPLinkBinarySensorEntityDescription, ...]] = (
    TPLinkBinarySensorEntityDescription(
        key="roaming",
        name="Roaming Status",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("roaming") == "1",
    ),
    TPLinkBinarySensorEntityDescription(
        key="endc_support",
        name="5G ENDC Support",
        icon="mdi:signal-5g",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["extra_lte_status"].get("endc_support") == "1",
    ),
)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary sensor platform."""
    coordinator: TPLinkRouterDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TPLinkRouterBinarySensor(coordinator, entry, description) for description in BINARY_SENSORS])

class TPLinkRouterBinarySensor(CoordinatorEntity[TPLinkRouterDataUpdateCoordinator], BinarySensorEntity):
    """Representation of a TP-Link Router binary sensor."""

    _attr_has_entity_name = True
    entity_description: TPLinkBinarySensorEntityDescription

    def __init__(self, coordinator, entry, description):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        if not self.coordinator.data:
            return False
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def device_info(self):
        """Return device information."""
        host = self._entry.options[CONF_HOST]
        # Binary sensors are currently only for the main device
        identifiers = {(DOMAIN, self.coordinator.mac)} if self.coordinator.mac else {(DOMAIN, host)}
        connections = {(CONNECTION_NETWORK_MAC, self.coordinator.mac)} if self.coordinator.mac else set()
        return {
            "identifiers": identifiers,
            "connections": connections,
            "name": self._entry.title,
            "manufacturer": "TP-Link",
            "model": self.coordinator.firmware.model if self.coordinator.firmware else "NX510v",
            "sw_version": self.coordinator.firmware.firmware_version if self.coordinator.firmware else None,
            "hw_version": self.coordinator.firmware.hardware_version if self.coordinator.firmware else None,
            "configuration_url": f"http://{host}",
        }
