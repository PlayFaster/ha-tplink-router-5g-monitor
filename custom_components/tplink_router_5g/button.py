"""Button platform for TP-Link Router 5G."""

import logging
from dataclasses import dataclass

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TPLinkRouterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class TPLinkButtonEntityDescription(ButtonEntityDescription):
    """Describes TP-Link button entity."""

    group: str = "main"


BUTTON_TYPES = (
    TPLinkButtonEntityDescription(
        key="reboot",
        name="Reboot",
        icon="mdi:restart",
        device_class=ButtonDeviceClass.RESTART,
        group="main",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator: TPLinkRouterDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in BUTTON_TYPES:
        entities.append(TPLinkRebootButton(coordinator, entry, description))

    async_add_entities(entities)


class TPLinkRebootButton(
    CoordinatorEntity[TPLinkRouterDataUpdateCoordinator], ButtonEntity
):
    """Representation of a TP-Link Router reboot button."""

    _attr_has_entity_name = True
    entity_description: TPLinkButtonEntityDescription

    def __init__(self, coordinator, entry, description):
        """Initialize the button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.coordinator.api.login()
            try:
                await self.coordinator.api.reboot()
            finally:
                await self.coordinator.api.logout()
        except Exception as err:
            _LOGGER.error("%s: Reboot failed: %s", self._entry.title, err)

    @property
    def device_info(self):
        """Return device information linking to the main router device."""
        host = self._entry.options[CONF_HOST]
        main_identifiers = (
            {(DOMAIN, self.coordinator.mac)}
            if self.coordinator.mac
            else {(DOMAIN, f"host_{host}")}
        )

        return {
            "identifiers": main_identifiers,
            "name": self._entry.title,
            "manufacturer": "TP-Link",
            "model": self.coordinator.model,
            "sw_version": self.coordinator.sw_version,
            "hw_version": self.coordinator.hw_version,
            "configuration_url": f"http://{host}",
        }
