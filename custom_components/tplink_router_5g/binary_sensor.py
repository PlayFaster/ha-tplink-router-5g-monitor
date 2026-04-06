"""Binary sensor platform for TP-Link Router 5G."""

from dataclasses import dataclass
from typing import Final
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)
from homeassistant.const import (
    CONF_HOST,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TPLinkRouterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True, kw_only=True)
class TPLinkBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes TP-Link binary sensor entity."""
    group: str = "main"

BINARY_SENSORS: Final[tuple[TPLinkBinarySensorEntityDescription, ...]] = (
    TPLinkBinarySensorEntityDescription(
        key="best_connection",
        name="Best Connection",
        icon="mdi:star-check",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        group="main",
    ),
    TPLinkBinarySensorEntityDescription(
        key="endc_support",
        name="5G ENDC Support",
        icon="mdi:signal-5g",
        group="main",
    ),
    TPLinkBinarySensorEntityDescription(
        key="roaming",
        name="Roaming Status",
        icon="mdi:airplane",
        group="main",
    ),
)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary sensor platform."""
    coordinator: TPLinkRouterDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for description in BINARY_SENSORS:
        entities.append(TPLinkRouterBinarySensor(coordinator, entry, description))
        
    async_add_entities(entities)

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
            
        key = self.entity_description.key
        extra = self.coordinator.data.get("extra_lte_status", {})
        
        if key == "best_connection":
            # Best connection: 5G ENDC is supported AND NR DL Modulation is 256QAM
            endc = extra.get("endc_support") == "1"
            dl_mod = extra.get("nr_dl_mod") == "256QAM"
            return endc and dl_mod
            
        if key == "endc_support":
            return extra.get("endc_support") == "1"
            
        if key == "roaming":
            return extra.get("roaming") == "1"
            
        return False

    @property
    def device_info(self):
        """Return device information linking to the main router device."""
        host = self._entry.options[CONF_HOST]
        main_identifiers = {(DOMAIN, self.coordinator.mac)} if self.coordinator.mac else {(DOMAIN, f"host_{host}")}
        
        return {
            "identifiers": main_identifiers,
            "name": self._entry.title,
            "manufacturer": "TP-Link",
            "model": self.coordinator.firmware.model if self.coordinator.firmware else "TP-Link Router",
            "configuration_url": f"http://{host}",
        }
