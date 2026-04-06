"""Number platform for TP-Link Router 5G."""

import asyncio
import logging
from datetime import timedelta

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.const import (
    CONF_HOST,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .const import CONF_SCAN_INTERVAL, DOMAIN
from .coordinator import TPLinkRouterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

POLLING_INTERVAL_DESCRIPTION = NumberEntityDescription(
    key="polling_interval",
    name="Polling Interval",
    translation_key="polling_interval",
    icon="mdi:timer-cog",
    native_min_value=30,
    native_max_value=7200,
    native_step=10,
    native_unit_of_measurement=UnitOfTime.SECONDS,
    entity_category=EntityCategory.CONFIG,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator: TPLinkRouterDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    initial_value = entry.options.get(CONF_SCAN_INTERVAL, 120)
    async_add_entities(
        [
            TPLinkPollingInterval(
                coordinator, entry, POLLING_INTERVAL_DESCRIPTION, initial_value
            )
        ]
    )


class TPLinkPollingInterval(NumberEntity):
    """Representation of a number entity to control polling interval."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator, entry, description, initial_value):
        """Initialize the number entity."""
        self.coordinator = coordinator
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        self._attr_native_value = initial_value
        self._refresh_task = None

    async def async_set_native_value(self, value: float) -> None:
        """Update the setting."""
        self._attr_native_value = value
        self.async_write_ha_state()

        if self._refresh_task:
            self._refresh_task.cancel()

        self._refresh_task = asyncio.create_task(self._async_debounced_apply(value))

    async def _async_debounced_apply(self, value: float):
        """Apply the value after a short delay."""
        try:
            await asyncio.sleep(2)
            val_int = int(value)
            self.coordinator.update_interval = timedelta(seconds=val_int)

            new_options = dict(self._entry.options)
            new_options[CONF_SCAN_INTERVAL] = val_int
            self.hass.config_entries.async_update_entry(
                self._entry, options=new_options
            )

            await self.coordinator.async_request_refresh()
        except asyncio.CancelledError:
            pass
        except Exception as err:
            _LOGGER.error("Failed to apply polling interval: %s", err)

    async def async_will_remove_from_hass(self) -> None:
        """Cancel any pending refresh task."""
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
            finally:
                self._refresh_task = None

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
            "model": self.coordinator.firmware.model
            if self.coordinator.firmware
            else "TP-Link Router",
            "configuration_url": f"http://{host}",
        }
