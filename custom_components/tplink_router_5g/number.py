"""Number platform for TP-Link Router 5G."""

import asyncio
import logging
from datetime import timedelta

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.const import CONF_HOST, UnitOfTime
from homeassistant.helpers.entity import EntityCategory

from .const import CONF_SCAN_INTERVAL, DOMAIN
from .coordinator import TPLinkRouterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

POLLING_INTERVAL_DESCRIPTION = NumberEntityDescription(
    key="polling_interval",
    name="Polling Interval",
    translation_key="polling_interval",
    native_min_value=30,
    native_max_value=3600,
    native_step=30,
    native_unit_of_measurement=UnitOfTime.SECONDS,
    entity_category=EntityCategory.CONFIG,
)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the number platform."""
    coordinator: TPLinkRouterDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    initial_value = entry.options.get(CONF_SCAN_INTERVAL, 30)
    async_add_entities([TPLinkPollingInterval(coordinator, entry, POLLING_INTERVAL_DESCRIPTION, initial_value)])

class TPLinkPollingInterval(NumberEntity):
    """Number entity to control the polling interval."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    entity_description: NumberEntityDescription

    def __init__(self, coordinator, entry, description, initial_value):
        """Initialize the number entity."""
        self._coordinator = coordinator
        self._entry = entry
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        self._attr_native_value = initial_value
        self._refresh_task = None

    async def async_set_native_value(self, value: float) -> None:
        """Handle the UI slider change."""
        self._attr_native_value = value
        self.async_write_ha_state()
        if self._refresh_task:
            self._refresh_task.cancel()
        self._refresh_task = asyncio.create_task(self._async_debounced_apply(value))

    async def _async_debounced_apply(self, value: float) -> None:
        """Apply change and persist to ConfigEntry Options after a delay."""
        try:
            await asyncio.sleep(2)
            val_int = int(value)
            self._coordinator.update_interval = timedelta(seconds=val_int)
            new_options = dict(self._entry.options)
            new_options[CONF_SCAN_INTERVAL] = val_int
            self.hass.config_entries.async_update_entry(self._entry, options=new_options)
            await self._coordinator.async_request_refresh()
        except asyncio.CancelledError:
            pass
        except Exception as err:
            _LOGGER.error("Failed to apply polling interval change: %s", err)

    @property
    def device_info(self):
        """Return device information."""
        host = self._entry.options[CONF_HOST]
        return {
            "identifiers": {(DOMAIN, host)},
            "name": self._entry.title,
            "manufacturer": "TP-Link",
        }
