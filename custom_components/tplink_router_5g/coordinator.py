"""DataUpdateCoordinator for TP-Link Router 5G."""

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import CONF_SCAN_INTERVAL, CONF_STOP_POLLING

_LOGGER = logging.getLogger(__name__)

class TPLinkRouterDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching TP-Link Router data with resilience."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api):
        """Initialize the coordinator."""
        self.api = api
        self.entry = entry
        self.consecutive_failures = 0
        self.last_update_success_time = None
        self.firmware = None
        self.mac = None

        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, 30)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{entry.title} Data",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self):
        """Fetch data from API with resilience."""
        is_paused = self.entry.options.get(CONF_STOP_POLLING, False)
        is_first_run = self.data is None

        if is_paused and not is_first_run:
            _LOGGER.debug("%s: Polling is paused; returning cached data.", self.entry.title)
            return self.data

        try:
            # Login and fetch everything
            await self.api.login()
            
            if not self.firmware:
                self.firmware = await self.api.get_firmware()
            
            status = await self.api.get_status()
            if status and status.lan_macaddr:
                self.mac = status.lan_macaddr
            
            lte_status = await self.api.get_lte_status()
            extra_lte = await self.api.get_extra_lte_status()
            ipv4_status = await self.api.get_ipv4_status()
            vpn_status = await self.api.get_vpn_status()
            
            data = {
                "status": status,
                "lte_status": lte_status,
                "extra_lte_status": extra_lte,
                "ipv4_status": ipv4_status,
                "vpn_status": vpn_status,
                "firmware": self.firmware
            }

            self.last_update_success_time = dt_util.now()
            self.consecutive_failures = 0
            return data

        except Exception as err:
            self.consecutive_failures += 1
            if self.data is not None and self.consecutive_failures == 1:
                _LOGGER.warning("%s: Fetch failed. Holding last known values.", self.entry.title)
                return self.data
            
            _LOGGER.error("%s: Connection lost: %s", self.entry.title, err)
            raise UpdateFailed(f"Communication error: {err}")
        finally:
            await self.api.logout()
