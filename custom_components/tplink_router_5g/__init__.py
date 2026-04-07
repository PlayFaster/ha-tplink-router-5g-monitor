"""The TP-Link Router 5G integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall

from .api import TPLinkRouter5GAPI
from .const import CONF_VERIFY_SSL, DOMAIN
from .coordinator import TPLinkRouterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SWITCH,
    Platform.NUMBER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TP-Link Router 5G Monitor from a config entry."""
    api = TPLinkRouter5GAPI(
        entry.options[CONF_HOST],
        entry.options.get(CONF_USERNAME),
        entry.options[CONF_PASSWORD],
        entry.options.get(CONF_VERIFY_SSL, False),
    )

    coordinator = TPLinkRouterDataUpdateCoordinator(hass, entry, api)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def send_sms_service(call: ServiceCall) -> None:
        """Service to send SMS."""
        number = call.data.get("number")
        text = call.data.get("text")
        try:
            await api.send_sms(number, text)
        except Exception as err:
            _LOGGER.error("Failed to send SMS: %s", err)

    hass.services.async_register(DOMAIN, "send_sms", send_sms_service)

    async def _async_background_setup():
        try:
            await coordinator.async_refresh()
            _LOGGER.info("%s: Background initialization complete.", entry.title)
        except Exception as err:
            _LOGGER.warning(
                "%s: Background initialization failed: %s", entry.title, err
            )

    # Use the modern background task API for better lifecycle management
    entry.async_create_background_task(
        hass, _async_background_setup(), "tplink-router-setup"
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and release resources."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        # Standardized Cleanup: Remove the domain key if no entries remain
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload_ok
