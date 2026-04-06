"""TP-Link Router 5G API client."""

import logging
import asyncio
from tplinkrouterc6u import TplinkRouterProvider

_LOGGER = logging.getLogger(__name__)

class TPLinkRouter5GAPI:
    """Async wrapper for the TP-Link Router library."""

    def __init__(self, host, username, password, verify_ssl=False):
        """Initialize the API."""
        self.host = host
        if not (host.startswith('http://') or host.startswith('https://')):
            self.host = f"http://{host}"
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.client = None

    async def _ensure_client(self):
        """Ensure the client is initialized in a thread-safe way."""
        if self.client is None:
            self.client = await asyncio.to_thread(
                TplinkRouterProvider.get_client,
                self.host,
                self.password,
                self.username,
                _LOGGER,
                self.verify_ssl,
            )

    async def login(self):
        """Authorize with the router."""
        await self._ensure_client()
        await asyncio.to_thread(self.client.authorize)

    async def logout(self):
        """Logout from the router."""
        if not self.client:
            return
        try:
            await asyncio.to_thread(self.client.logout)
        except Exception as e:
            _LOGGER.debug("Logout failed: %s", e)

    async def get_firmware(self):
        """Get firmware info."""
        await self._ensure_client()
        return await asyncio.to_thread(self.client.get_firmware)

    async def get_status(self):
        """Get basic status."""
        await self._ensure_client()
        return await asyncio.to_thread(self.client.get_status)

    async def get_lte_status(self):
        """Get LTE/5G status."""
        await self._ensure_client()
        if hasattr(self.client, "get_lte_status"):
            return await asyncio.to_thread(self.client.get_lte_status)
        return None

    async def get_extra_lte_status(self):
        """Fetch extra cell info for 5G metrics (the discovery we made)."""
        await self._ensure_client()
        if not hasattr(self.client, "req_act") or not hasattr(self.client, "ActItem"):
            return {}

        def probe():
            ActItem = self.client.ActItem
            # Use GL (Get List) to get all serving cells
            act = ActItem(ActItem.GL, 'DEV2_LTE_SERVING_CELL_INFO', '0,0,0,0,0,0', attrs=[])
            _, values = self.client.req_act([act])
            return values

        values = await asyncio.to_thread(probe)
        
        if not values or not isinstance(values[0], list):
            return {}

        extra = {}
        for cell in values[0]:
            if cell.get('cellConnectionStatus') != '1':
                continue
            
            net_type = cell.get('networkType')
            prefix = ""
            if net_type == '3': # LTE
                prefix = "lte_"
            elif net_type == '8': # NR (5G)
                prefix = "nr_"
            else:
                continue

            # Map fields discovered during research
            extra[f"{prefix}band"] = cell.get('band')
            extra[f"{prefix}rsrp"] = cell.get('SSRSRP') if net_type == '8' else cell.get('RSRP')
            extra[f"{prefix}rsrq"] = cell.get('SSRSRQ') if net_type == '8' else cell.get('RSRQ')
            extra[f"{prefix}snr"] = cell.get('SSSINR') if net_type == '8' else cell.get('SNR')
            extra[f"{prefix}rssi"] = cell.get('RSSI')
            extra[f"{prefix}pci"] = cell.get('PCI')
            extra[f"{prefix}dl_mod"] = cell.get('downlinkModType')
            extra[f"{prefix}ul_mod"] = cell.get('uplinkModType')

        return extra

    async def reboot(self):
        """Reboot the router."""
        await self._ensure_client()
        await asyncio.to_thread(self.client.reboot)
