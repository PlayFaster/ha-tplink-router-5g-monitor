"""Switch platform for TP-Link Router 5G."""

import logging

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.const import CONF_HOST
from homeassistant.helpers.entity import EntityCategory

from .const import CONF_STOP_POLLING, DOMAIN
from .coordinator import TPLinkRouterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PAUSE_POLLING_DESCRIPTION = SwitchEntityDescription(
    key="pause_polling",
    name="Pause Polling",
    icon="mdi:pause-circle-outline",
    entity_category=EntityCategory.CONFIG,
)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the switch platform."""
    coordinator: TPLinkRouterDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    initial_state = entry.options.get(CONF_STOP_POLLING, False)
    async_add_entities([TPLinkPausePollingSwitch(coordinator, entry, PAUSE_POLLING_DESCRIPTION, initial_state)])

class TPLinkPausePollingSwitch(SwitchEntity):
    """Switch to pause/resume polling."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    entity_description: SwitchEntityDescription

    def __init__(self, coordinator, entry, description, initial_state):
        """Initialize the switch."""
        self._coordinator = coordinator
        self._entry = entry
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        self._attr_is_on = initial_state

    @property
    def is_on(self) -> bool:
        """Return true if polling is paused."""
        return self._entry.options.get(CONF_STOP_POLLING, False)

    async def async_turn_on(self, **kwargs):
        """Pause polling."""
        await self._async_set_state(True)

    async def async_turn_off(self, **kwargs):
        """Resume polling."""
        await self._async_set_state(False)

    async def _async_set_state(self, state: bool):
        """Update memory, state, and persist to options."""
        new_options = dict(self._entry.options)
        new_options[CONF_STOP_POLLING] = state
        self.hass.config_entries.async_update_entry(self._entry, options=new_options)
        self.async_write_ha_state()
        if not state:
            await self._coordinator.async_request_refresh()

    @property
    def device_info(self):
        """Return device information."""
        host = self._entry.options[CONF_HOST]
        return {
            "identifiers": {(DOMAIN, host)},
            "name": self._entry.title,
            "manufacturer": "TP-Link",
        }
