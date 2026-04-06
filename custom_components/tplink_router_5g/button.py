"""Button platform for TP-Link Router 5G."""

import logging
from dataclasses import dataclass

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import CONF_HOST
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

from .const import DOMAIN
from .coordinator import TPLinkRouterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True, kw_only=True)
class TPLinkButtonEntityDescription(ButtonEntityDescription):
    """Describes TP-Link button entity."""

REBOOT_DESCRIPTION = TPLinkButtonEntityDescription(
    key="reboot",
    name="Reboot",
    icon="mdi:restart",
    device_class=ButtonDeviceClass.RESTART,
)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the button platform."""
    coordinator: TPLinkRouterDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TPLinkRebootButton(coordinator, entry, REBOOT_DESCRIPTION)])

class TPLinkRebootButton(CoordinatorEntity[TPLinkRouterDataUpdateCoordinator], ButtonEntity):
    """Button to reboot the TP-Link router."""

    _attr_has_entity_name = True
    entity_description: TPLinkButtonEntityDescription

    def __init__(self, coordinator, entry, description):
        """Initialize the reboot button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"

    @property
    def device_info(self):
        """Return device information."""
        host = self._entry.options[CONF_HOST]
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

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.coordinator.api.login()
            await self.coordinator.api.reboot()
            await self.coordinator.api.logout()
        except Exception as err:
            _LOGGER.error("%s: Reboot failed: %s", self._entry.title, err)
