"""Binary sensor platform for TP-Link Router 5G."""

import logging
from dataclasses import dataclass
from typing import Final

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    EntityCategory,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TPLinkRouterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class TPLinkBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes TP-Link binary sensor entity."""

    group: str = "signal"


BINARY_SENSORS: Final[tuple[TPLinkBinarySensorEntityDescription, ...]] = (
    TPLinkBinarySensorEntityDescription(
        key="best_connection",
        name="Best Connection",
        icon="mdi:star-check",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        group="signal",
    ),
    TPLinkBinarySensorEntityDescription(
        key="endc_support",
        name="5G ENDC Support",
        icon="mdi:signal-5g",
        entity_category=EntityCategory.DIAGNOSTIC,
        group="signal",
    ),
    TPLinkBinarySensorEntityDescription(
        key="roaming",
        name="Roaming Status",
        icon="mdi:airplane",
        entity_category=EntityCategory.DIAGNOSTIC,
        group="signal",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator: TPLinkRouterDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in BINARY_SENSORS:
        entities.append(TPLinkRouterBinarySensor(coordinator, entry, description))

    async_add_entities(entities)


class TPLinkRouterBinarySensor(
    CoordinatorEntity[TPLinkRouterDataUpdateCoordinator], BinarySensorEntity
):
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
            # Option D: Hybrid Potential Logic
            endc = extra.get("endc_support") == "1"
            if not endc:
                return False

            lte_rsrp = extra.get("lte_rsrp")
            lte_snr_raw = extra.get("lte_snr")
            lte_snr = 0.1 * lte_snr_raw if lte_snr_raw is not None else None

            nr_rsrp = extra.get("nr_rsrp")
            nr_snr_raw = extra.get("nr_snr")
            nr_snr = 0.1 * nr_snr_raw if nr_snr_raw is not None else None

            lte_healthy = (lte_rsrp is not None and lte_rsrp > -100) or (
                lte_snr is not None and lte_snr > 15
            )
            nr_healthy = (nr_rsrp is not None and nr_rsrp > -105) or (
                nr_snr is not None and nr_snr > 10
            )

            return endc and lte_healthy and nr_healthy

        if key == "endc_support":
            return extra.get("endc_support") == "1"

        if key == "roaming":
            return extra.get("roaming") == "1"

        return False

    @property
    def device_info(self):
        """Return device information with sub-device support."""
        host = self._entry.options[CONF_HOST]
        group = self.entity_description.group
        sub_id_prefix = self.coordinator.mac if self.coordinator.mac else f"host_{host}"

        group_names = {
            "system": "System",
            "signal": "Signal",
            "home_network": "Home Network",
            "data": "Data",
            "sms": "SMS",
        }
        display_group = group_names.get(group, group.capitalize())
        sub_name = f"{self._entry.title} {display_group}"

        return {
            "identifiers": {(DOMAIN, f"{sub_id_prefix}_{group}")},
            "name": sub_name,
            "manufacturer": "TP-Link",
            "model": self.coordinator.model,
            "sw_version": self.coordinator.sw_version,
            "hw_version": self.coordinator.hw_version,
            "configuration_url": f"http://{host}",
            "via_device": (DOMAIN, f"{sub_id_prefix}_system"),
        }
