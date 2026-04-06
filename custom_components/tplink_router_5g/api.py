"""TP-Link Router 5G API client."""

import logging
import asyncio
from tplinkrouterc6u import TplinkRouterProvider, LTEStatus

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

    async def get_lte_and_extra_status(self):
        """Fetch all LTE/5G and extra metrics in a single session to reduce load."""
        await self._ensure_client()
        if not hasattr(self.client, "req_act") or not hasattr(self.client, "ActItem"):
            # Fallback to standard if req_act not available (should not happen for EX)
            lte = await asyncio.to_thread(self.client.get_lte_status) if hasattr(self.client, "get_lte_status") else None
            return lte, {}

        def fetch_all():
            ActItem = self.client.ActItem
            # Define all OIDs we need
            acts = [
                # 0: Standard LTE Link Config
                ActItem(ActItem.GET, 'DEV2_LTE_LINK_CFG', '1,0,0,0,0,0', attrs=['enable', 'connectStatus', 'networkType', 'simStatus', 'roamingStatus', 'endcStatus']),
                # 1: Data Usage and Speed
                ActItem(ActItem.GET, 'DEV2_XTP_LTE_INTF_CFG', '1,0,0,0,0,0', attrs=['totalStatistics', 'curRxSpeed', 'curTxSpeed', 'dailyFlow', 'limitation', 'paymentDay']),
                # 2: Standard Net Status (Signal/Unread)
                ActItem(ActItem.GET, 'DEV2_LTE_NET_STATUS', '1,0,0,0,0,0', attrs=['smsUnreadCount', 'sigLevel', 'rfInfoRsrp', 'rfInfoRsrq', 'rfInfoSnr', 'smsSendResult', 'smsSendCause']),
                # 3: ISP Name
                ActItem(ActItem.GET, 'DEV2_LTE_PROF_STAT', '1,0,0,0,0,0', attrs=['ispName']),
                # 4: Detailed Serving Cells (5G Metrics)
                ActItem(ActItem.GL, 'DEV2_LTE_SERVING_CELL_INFO', '0,0,0,0,0,0', attrs=[]),
            ]
            
            _, values = self.client.req_act(acts)
            return values

        values = await asyncio.to_thread(fetch_all)
        
        # 1. Reconstruct LTEStatus (to maintain compatibility with sensor value_fns)
        lte_status = LTEStatus()
        try:
            if values and len(values) > 0 and values[0]:
                v0 = values[0]
                lte_status.enable = int(v0.get('enable', 0))
                lte_status.connect_status = int(v0.get('connectStatus', 0))
                lte_status.network_type = int(v0.get('networkType', 0))
                lte_status.sim_status = int(v0.get('simStatus', 0))
            
            if values and len(values) > 1 and values[1]:
                v1 = values[1]
                lte_status.total_statistics = int(v1.get('totalStatistics', 0))
                lte_status.cur_rx_speed = int(v1.get('curRxSpeed', 0))
                lte_status.cur_tx_speed = int(v1.get('curTxSpeed', 0))
                
            if values and len(values) > 2 and values[2]:
                v2 = values[2]
                lte_status.sms_unread_count = int(v2.get('smsUnreadCount', 0))
                lte_status.sig_level = int(v2.get('sigLevel', 0))
                lte_status.rsrp = int(v2.get('rfInfoRsrp', 0))
                lte_status.rsrq = int(v2.get('rfInfoRsrq', 0))
                lte_status.snr = int(v2.get('rfInfoSnr', 0))
                
            if values and len(values) > 3 and values[3]:
                lte_status.isp_name = values[3].get('ispName')
        except (ValueError, TypeError, AttributeError) as err:
            _LOGGER.debug("Error mapping LTE status: %s", err)

        # 2. Parse Extra Metrics
        extra = {}
        # From v0 (Link Config)
        if values and len(values) > 0 and values[0]:
            extra["roaming"] = values[0].get("roamingStatus")
            extra["endc_support"] = values[0].get("endcStatus")
            
        # From v1 (Interface Config)
        if values and len(values) > 1 and values[1]:
            extra["daily_usage"] = values[1].get("dailyFlow")
            extra["usage_limit"] = values[1].get("limitation")
            extra["payment_day"] = values[1].get("paymentDay")
            
        # From v2 (Net Status)
        if values and len(values) > 2 and values[2]:
            extra["sms_send_result"] = values[2].get("smsSendResult")
            extra["sms_send_cause"] = values[2].get("smsSendCause")

        # From v4 (Cell Info)
        if values and len(values) > 4 and isinstance(values[4], list):
            for cell in values[4]:
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

        return lte_status, extra

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

    async def reboot(self):
        """Reboot the router."""
        await self._ensure_client()
        await asyncio.to_thread(self.client.reboot)

    async def set_wifi(self, wifi, enable):
        """Enable or disable a wifi connection."""
        await self._ensure_client()
        await asyncio.to_thread(self.client.set_wifi, wifi, enable)
