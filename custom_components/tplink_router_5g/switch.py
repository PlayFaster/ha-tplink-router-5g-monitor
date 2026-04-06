"""Switch platform for TP-Link Router 5G."""

import logging
from dataclasses import dataclass
from typing import Any, Final

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_STOP_POLLING, DOMAIN
from .coordinator import TPLinkRouterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class TPLinkWifiSwitchDescription(SwitchEntityDescription):
    """Describes TP-Link wifi switch entity."""

    wifi_connection: str
    property_name: str
    group: str = "wifi"


WIFI_SWITCHES: Final[tuple[TPLinkWifiSwitchDescription, ...]] = (
    TPLinkWifiSwitchDescription(
        key="wifi_2g_main",
        name="Main Wi-Fi 2.4GHz",
        icon="mdi:wifi",
        wifi_connection="wifi_2g",
        property_name="wifi_2g_enable",
    ),
    TPLinkWifiSwitchDescription(
        key="wifi_5g_main",
        name="Main Wi-Fi 5GHz",
        icon="mdi:wifi",
        wifi_connection="wifi_5g",
        property_name="wifi_5g_enable",
    ),
    TPLinkWifiSwitchDescription(
        key="wifi_6g_main",
        name="Main Wi-Fi 6GHz",
        icon="mdi:wifi",
        wifi_connection="wifi_6g",
        property_name="wifi_6g_enable",
    ),
    TPLinkWifiSwitchDescription(
        key="wifi_2g_guest",
        name="Guest Wi-Fi 2.4GHz",
        icon="mdi:wifi",
        wifi_connection="wifi_2g_guest",
        property_name="wifi_2g_guest_enable",
    ),
    TPLinkWifiSwitchDescription(
        key="wifi_5g_guest",
        name="Guest Wi-Fi 5GHz",
        icon="mdi:wifi",
        wifi_connection="wifi_5g_guest",
        property_name="wifi_5g_guest_enable",
    ),
    TPLinkWifiSwitchDescription(
        key="wifi_6g_guest",
        name="Guest Wi-Fi 6GHz",
        icon="mdi:wifi",
        wifi_connection="wifi_6g_guest",
        property_name="wifi_6g_guest_enable",
    ),
    TPLinkWifiSwitchDescription(
        key="wifi_2g_iot",
        name="IoT Wi-Fi 2.4GHz",
        icon="mdi:wifi",
        wifi_connection="wifi_2g_iot",
        property_name="wifi_2g_iot_enable",
    ),
    TPLinkWifiSwitchDescription(
        key="wifi_5g_iot",
        name="IoT Wi-Fi 5GHz",
        icon="mdi:wifi",
        wifi_connection="wifi_5g_iot",
        property_name="wifi_5g_iot_enable",
    ),
    TPLinkWifiSwitchDescription(
        key="wifi_6g_iot",
        name="IoT Wi-Fi 6GHz",
        icon="mdi:wifi",
        wifi_connection="wifi_6g_iot",
        property_name="wifi_6g_iot_enable",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the switch platform."""
    coordinator: TPLinkRouterDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in WIFI_SWITCHES:
        entities.append(TPLinkWifiSwitch(coordinator, entry, description))

    entities.append(TPLinkPausePollingSwitch(coordinator, entry))

    async_add_entities(entities)


class TPLinkWifiSwitch(
    CoordinatorEntity[TPLinkRouterDataUpdateCoordinator], SwitchEntity
):
    """Representation of a TP-Link Router Wi-Fi switch."""

    _attr_has_entity_name = True
    entity_description: TPLinkWifiSwitchDescription

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
        return getattr(
            self.coordinator.data["status"], self.entity_description.property_name, False
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        try:
            await self.coordinator.api.login()
            await self.coordinator.api.set_wifi(
                self.entity_description.wifi_connection, True
            )
            await self.coordinator.api.logout()
        except Exception as err:
            _LOGGER.error(
                "%s: Failed to turn on %s: %s",
                self._entry.title,
                self.entity_description.key,
                err,
            )
            raise

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        try:
            await self.coordinator.api.login()
            await self.coordinator.api.set_wifi(
                self.entity_description.wifi_connection, False
            )
            await self.coordinator.api.logout()
        except Exception as err:
            _LOGGER.error(
                "%s: Failed to turn off %s: %s",
                self._entry.title,
                self.entity_description.key,
                err,
            )
            raise

        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        """Return device information with sub-device support."""
        host = self._entry.options[CONF_HOST]
        group = self.entity_description.group

        if self.coordinator.mac:
            main_identifiers = {(DOMAIN, self.coordinator.mac)}
            sub_id_prefix = self.coordinator.mac
        else:
            main_identifiers = {(DOMAIN, f"host_{host}")}
            sub_id_prefix = f"host_{host}"

        identifiers_list = list(main_identifiers)
        via_device = identifiers_list[0] if identifiers_list else (DOMAIN, host)

        return {
            "identifiers": {(DOMAIN, f"{sub_id_prefix}_{group}")},
            "name": f"{self._entry.title} Wi-Fi",
            "manufacturer": "TP-Link",
            "via_device": via_device,
        }


class TPLinkPausePollingSwitch(
    CoordinatorEntity[TPLinkRouterDataUpdateCoordinator], SwitchEntity
):
    """Representation of a switch to pause/resume polling."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, entry):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_pause_polling"
        self._attr_name = "Pause Polling"
        self._attr_icon = "mdi:pause-circle-outline"

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
        """Update memory and persist to options."""
        new_options = dict(self._entry.options)
        new_options[CONF_STOP_POLLING] = state
        self.hass.config_entries.async_update_entry(self._entry, options=new_options)
        self.async_write_ha_state()
        if not state:
            await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        """Return device information linking to the main router device."""
        host = self._entry.options[CONF_HOST]
        if self.coordinator.mac:
            main_identifiers = {(DOMAIN, self.coordinator.mac)}
        else:
            main_identifiers = {(DOMAIN, f"host_{host}")}

        model = (
            self.coordinator.firmware.model
            if self.coordinator.firmware
            else "TP-Link Router"
        )

        return {
            "identifiers": main_identifiers,
            "name": self._entry.title,
            "manufacturer": "TP-Link",
            "model": model,
            "configuration_url": f"http://{host}",
        }
