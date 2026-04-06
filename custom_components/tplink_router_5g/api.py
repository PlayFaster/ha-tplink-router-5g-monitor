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

    async def get_sms(self):
        """Get SMS messages if supported by library client."""
        await self._ensure_client()
        if hasattr(self.client, "get_sms"):
            return await asyncio.to_thread(self.client.get_sms)
        return []

    async def send_sms(self, number, text):
        """Send an SMS message."""
        await self._ensure_client()
        if hasattr(self.client, "send_sms"):
            await asyncio.to_thread(self.client.send_sms, number, text)

    async def get_ipv4_status(self):
        """Get IPv4 status including DNS."""
        await self._ensure_client()
        if hasattr(self.client, "get_ipv4_status"):
            return await asyncio.to_thread(self.client.get_ipv4_status)
        return None

    async def get_vpn_status(self):
        """Get VPN status."""
        await self._ensure_client()
        if hasattr(self.client, "get_vpn_status"):
            return await asyncio.to_thread(self.client.get_vpn_status)
        return None

    async def get_extra_lte_status(self):
        """Fetch extra metrics including daily usage and detailed cell info."""
        await self._ensure_client()
        if not hasattr(self.client, "req_act") or not hasattr(self.client, "ActItem"):
            return {}

        def probe():
            ActItem = self.client.ActItem
            # 1. Serving Cell Info (Signal/Tower)
            act_cell = ActItem(ActItem.GL, 'DEV2_LTE_SERVING_CELL_INFO', '0,0,0,0,0,0', attrs=[])
            # 2. Interface Config (Daily Usage/Limits)
            act_intf = ActItem(ActItem.GET, 'DEV2_XTP_LTE_INTF_CFG', '1,0,0,0,0,0', attrs=[])
            # 3. Link Config (Roaming/ENDC)
            act_link = ActItem(ActItem.GET, 'DEV2_LTE_LINK_CFG', '1,0,0,0,0,0', attrs=[])
            
            _, values = self.client.req_act([act_cell, act_intf, act_link])
            return values

        values = await asyncio.to_thread(probe)
        extra = {}
        
        # Parse Serving Cells
        if values and len(values) > 0 and isinstance(values[0], list):
            for cell in values[0]:
                if cell.get('cellConnectionStatus') != '1':
                    continue
                net_type = cell.get('networkType')
                prefix = "nr_" if net_type == '8' else "lte_"
                
                extra[f"{prefix}band"] = cell.get('band')
                extra[f"{prefix}rsrp"] = cell.get('SSRSRP') if net_type == '8' else cell.get('RSRP')
                extra[f"{prefix}rsrq"] = cell.get('SSRSRQ') if net_type == '8' else cell.get('RSRQ')
                extra[f"{prefix}snr"] = cell.get('SSSINR') if net_type == '8' else cell.get('SNR')
                extra[f"{prefix}rssi"] = cell.get('RSSI')
                extra[f"{prefix}pci"] = cell.get('PCI')
                extra[f"{prefix}tac"] = cell.get('TAC')
                extra[f"{prefix}cid"] = cell.get('cid')
                extra[f"{prefix}arfcn"] = cell.get('ARFCN')
                extra[f"{prefix}dl_mod"] = cell.get('downlinkModType')
                extra[f"{prefix}ul_mod"] = cell.get('uplinkModType')
                extra[f"{prefix}dl_bw"] = cell.get('dlBandwidth')
                extra[f"{prefix}ul_bw"] = cell.get('ulBandwidth')
                extra[f"{prefix}cqi"] = cell.get('CQI')
                extra[f"{prefix}tx_power"] = cell.get('txPowerPUCCH')
                extra[f"{prefix}rbs"] = cell.get('numRbs')

        # Parse Interface Config
        if values and len(values) > 1 and isinstance(values[1], dict):
            intf = values[1]
            extra["daily_usage"] = intf.get("dailyFlow")
            extra["usage_limit"] = intf.get("limitation")
            extra["payment_day"] = intf.get("paymentDay")

        # Parse Link Config
        if values and len(values) > 2 and isinstance(values[2], dict):
            link = values[2]
            extra["roaming"] = link.get("roamingStatus")
            extra["endc_support"] = link.get("endcStatus")
            # Extra SMS diagnostics if available in status block
            extra["sms_send_result"] = link.get("smsSendResult")
            extra["sms_send_cause"] = link.get("smsSendCause")

        return extra

    async def reboot(self):
        """Reboot the router."""
        await self._ensure_client()
        await asyncio.to_thread(self.client.reboot)

    async def set_wifi(self, wifi, enable):
        """Enable or disable a wifi connection."""
        await self._ensure_client()
        await asyncio.to_thread(self.client.set_wifi, wifi, enable)
