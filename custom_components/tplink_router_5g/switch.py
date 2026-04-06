"""Switch platform for TP-Link Router 5G."""

from dataclasses import dataclass
from collections.abc import Callable
from typing import Any
import logging

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.const import CONF_HOST, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from tplinkrouterc6u import Connection

from .const import CONF_STOP_POLLING, DOMAIN
from .coordinator import TPLinkRouterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True, kw_only=True)
class TPLinkSwitchEntityDescription(SwitchEntityDescription):
    """Describes TP-Link switch entity."""
    group: str = "main"
    property_name: str | None = None
    wifi_connection: Connection | None = None

SWITCH_TYPES: tuple[TPLinkSwitchEntityDescription, ...] = (
    # --- Main Device: Configuration ---
    TPLinkSwitchEntityDescription(
        key="pause_polling",
        name="Pause Polling",
        icon="mdi:pause-circle-outline",
        entity_category=EntityCategory.CONFIG,
        group="main",
    ),
    
    # --- Wi-Fi Sub-device: Guest ---
    TPLinkSwitchEntityDescription(
        key="wifi_guest_24g",
        name="Guest Wi-Fi 2.4G",
        icon="mdi:wifi",
        group="wifi",
        property_name='guest_2g_enable',
        wifi_connection=Connection.GUEST_2G,
    ),
    TPLinkSwitchEntityDescription(
        key="wifi_guest_5g",
        name="Guest Wi-Fi 5G",
        icon="mdi:wifi",
        group="wifi",
        property_name='guest_5g_enable',
        wifi_connection=Connection.GUEST_5G,
    ),
    TPLinkSwitchEntityDescription(
        key="wifi_guest_6g",
        name="Guest Wi-Fi 6G",
        icon="mdi:wifi",
        group="wifi",
        property_name='guest_6g_enable',
        wifi_connection=Connection.GUEST_6G,
    ),
    
    # --- Wi-Fi Sub-device: Main ---
    TPLinkSwitchEntityDescription(
        key="wifi_24g",
        name="Wi-Fi 2.4G",
        icon="mdi:wifi",
        group="wifi",
        property_name='wifi_2g_enable',
        wifi_connection=Connection.HOST_2G,
    ),
    TPLinkSwitchEntityDescription(
        key="wifi_5g",
        name="Wi-Fi 5G",
        icon="mdi:wifi",
        group="wifi",
        property_name='wifi_5g_enable',
        wifi_connection=Connection.HOST_5G,
    ),
    TPLinkSwitchEntityDescription(
        key="wifi_6g",
        name="Wi-Fi 6G",
        icon="mdi:wifi",
        group="wifi",
        property_name='wifi_6g_enable',
        wifi_connection=Connection.HOST_6G,
    ),
    
    # --- Wi-Fi Sub-device: IoT ---
    TPLinkSwitchEntityDescription(
        key="iot_24g",
        name="IoT Wi-Fi 2.4G",
        icon="mdi:wifi",
        group="wifi",
        property_name='iot_2g_enable',
        wifi_connection=Connection.IOT_2G,
    ),
    TPLinkSwitchEntityDescription(
        key="iot_5g",
        name="IoT Wi-Fi 5G",
        icon="mdi:wifi",
        group="wifi",
        property_name='iot_5g_enable',
        wifi_connection=Connection.IOT_5G,
    ),
    TPLinkSwitchEntityDescription(
        key="iot_6g",
        name="IoT Wi-Fi 6G",
        icon="mdi:wifi",
        group="wifi",
        property_name='iot_6g_enable',
        wifi_connection=Connection.IOT_6G,
    ),
)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the switch platform."""
    coordinator: TPLinkRouterDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for description in SWITCH_TYPES:
        if description.key == "pause_polling":
            entities.append(TPLinkPausePollingSwitch(coordinator, entry, description))
        else:
            entities.append(TPLinkWifiSwitch(coordinator, entry, description))
            
    async_add_entities(entities)

class TPLinkPausePollingSwitch(CoordinatorEntity[TPLinkRouterDataUpdateCoordinator], SwitchEntity):
    """Switch to pause/resume polling."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    entity_description: TPLinkSwitchEntityDescription

    def __init__(self, coordinator, entry, description):
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"

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
            await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        """Return device information."""
        host = self._entry.options[CONF_HOST]
        group = self.entity_description.group
        
        main_identifiers = {(DOMAIN, self.coordinator.mac)} if self.coordinator.mac else {(DOMAIN, host)}
        
        if group == "main":
            connections = {(CONNECTION_NETWORK_MAC, self.coordinator.mac)} if self.coordinator.mac else set()
            return {
                "identifiers": main_identifiers,
                "connections": connections,
                "name": self._entry.title,
                "manufacturer": "TP-Link",
                "model": self.coordinator.firmware.model if self.coordinator.firmware else "NX510v",
                "sw_version": self.coordinator.firmware.firmware_version if self.coordinator.firmware else None,
                "hw_version": self.coordinator.firmware.hardware_version if self.coordinator.firmware else None,
                "configuration_url": f"http://{host}",
            }

class TPLinkWifiSwitch(CoordinatorEntity[TPLinkRouterDataUpdateCoordinator], SwitchEntity):
    """Switch to enable/disable Wi-Fi bands."""

    _attr_has_entity_name = True
    entity_description: TPLinkSwitchEntityDescription

    def __init__(self, coordinator, entry, description):
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        if not self.coordinator.data or not self.coordinator.data.get("status"):
            return False
        return getattr(self.coordinator.data["status"], self.entity_description.property_name, False)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if not self.coordinator.data or not self.coordinator.data.get("status"):
            return False
        return getattr(self.coordinator.data["status"], self.entity_description.property_name) is not None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await self.coordinator.api.login()
        await self.coordinator.api.set_wifi(self.entity_description.wifi_connection, True)
        await self.coordinator.api.logout()
        setattr(self.coordinator.data["status"], self.entity_description.property_name, True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self.coordinator.api.login()
        await self.coordinator.api.set_wifi(self.entity_description.wifi_connection, False)
        await self.coordinator.api.logout()
        setattr(self.coordinator.data["status"], self.entity_description.property_name, False)
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device information for Wi-Fi sub-device."""
        host = self._entry.options[CONF_HOST]
        main_identifiers = {(DOMAIN, self.coordinator.mac)} if self.coordinator.mac else {(DOMAIN, host)}
        sub_id_prefix = self.coordinator.mac if self.coordinator.mac else host
        
        return {
            "identifiers": {(DOMAIN, f"{sub_id_prefix}_wifi")},
            "name": f"{self._entry.title} Wi-Fi",
            "manufacturer": "TP-Link",
            "via_device": list(main_identifiers)[0],
        }
