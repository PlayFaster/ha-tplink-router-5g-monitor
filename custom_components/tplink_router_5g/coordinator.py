"""DataUpdateCoordinator for TP-Link Router 5G."""

import asyncio
import logging
from datetime import timedelta
from typing import Any

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

        # Load hardware identity from persistent ConfigEntry data.
        # This ensures device info is stable from boot.
        self.model = entry.data.get("model", "TP-Link Router")
        self.sw_version = entry.data.get("sw_version")
        self.hw_version = entry.data.get("hw_version")
        self.mac = entry.data.get("mac")

        # Keep reference to raw firmware object for compatibility if needed
        self.firmware = None

        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, 120)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{entry.title} Data",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API with resilience and timeout."""
        is_paused = self.entry.options.get(CONF_STOP_POLLING, False)
        is_first_run = self.data is None

        if is_paused and not is_first_run:
            _LOGGER.debug(
                "%s: Polling is paused; returning cached data.", self.entry.title
            )
            return self.data

        try:
            async with asyncio.timeout(30):  # 30s timeout for the whole cycle
                # Session Start
                await self.api.login()

                # 1. Main Status
                status = await self.api.get_status()
                if status and status.lan_macaddr:
                    self.mac = status.lan_macaddr

                # 2. Firmware Info
                new_fw = await self.api.get_firmware()
                self.firmware = new_fw

                if new_fw and (
                    new_fw.firmware_version != self.sw_version
                    or new_fw.model != self.model
                ):
                    # Check for metadata changes (e.g. firmware update)
                    _LOGGER.info(
                        "%s: Hardware metadata updated: %s (%s)",
                        self.entry.title,
                        new_fw.model,
                        new_fw.firmware_version,
                    )
                    self.model = new_fw.model
                    self.sw_version = new_fw.firmware_version
                    self.hw_version = new_fw.hardware_version

                    new_data = dict(self.entry.data)
                    new_data.update(
                        {
                            "model": self.model,
                            "sw_version": self.sw_version,
                            "hw_version": self.hw_version,
                            "mac": self.mac,
                        }
                    )
                    self.hass.config_entries.async_update_entry(
                        self.entry, data=new_data
                    )

                # 3. Consolidated LTE and 5G Metrics
                lte_status, extra_lte = await self.api.get_lte_and_extra_status()

                # 4. Optional Info
                ipv4_status = await self.api.get_ipv4_status()
                vpn_status = await self.api.get_vpn_status()

                data = {
                    "status": status,
                    "lte_status": lte_status,
                    "extra_lte_status": extra_lte,
                    "ipv4_status": ipv4_status,
                    "vpn_status": vpn_status,
                    "firmware": self.firmware,
                }

                self.last_update_success_time = dt_util.now()
                self.consecutive_failures = 0
                return data

        except TimeoutError as err:
            self.consecutive_failures += 1
            if self.data is not None and self.consecutive_failures <= 2:
                _LOGGER.warning(
                    "%s: Fetch timed out. Holding last known values.", self.entry.title
                )
                return self.data
            _LOGGER.error("%s: API request timed out", self.entry.title)
            raise UpdateFailed("API request timed out") from err
        except Exception as err:
            self.consecutive_failures += 1
            if self.data is not None and self.consecutive_failures <= 2:
                _LOGGER.warning(
                    "%s: Fetch failed (%s). Holding last known values.",
                    self.entry.title,
                    err,
                )
                return self.data

            _LOGGER.error("%s: Connection lost: %s", self.entry.title, err)
            raise UpdateFailed(f"Communication error: {err}") from err
        finally:
            # Session End
            try:
                await self.api.logout()
            except Exception as logout_err:
                _LOGGER.debug("%s: Logout failed: %s", self.entry.title, logout_err)
