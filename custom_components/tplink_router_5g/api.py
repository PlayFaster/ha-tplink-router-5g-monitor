"""TP-Link Router 5G API client."""

import logging
import asyncio
from tplinkrouterc6u import TplinkRouterProvider, LTEStatus

_LOGGER = logging.getLogger(__name__)

def _safe_int(value, default=0):
    """Safely convert value to int."""
    if value is None or value == "":
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

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
        """Fetch all LTE/5G and extra metrics in a single session."""
        await self._ensure_client()
        if not hasattr(self.client, "req_act") or not hasattr(self.client, "ActItem"):
            lte = await asyncio.to_thread(self.client.get_lte_status) if hasattr(self.client, "get_lte_status") else None
            return lte, {}

        def fetch_all():
            ActItem = self.client.ActItem
            acts = [
                # 0: Link Config
                ActItem(ActItem.GET, 'DEV2_LTE_LINK_CFG', '1,0,0,0,0,0', attrs=['enable', 'connectStatus', 'networkType', 'simStatus', 'roamingStatus', 'endcStatus']),
                # 1: Data Usage
                ActItem(ActItem.GET, 'DEV2_XTP_LTE_INTF_CFG', '1,0,0,0,0,0', attrs=['totalStatistics', 'curRxSpeed', 'curTxSpeed', 'dailyFlow', 'limitation', 'paymentDay']),
                # 2: Net Status
                ActItem(ActItem.GET, 'DEV2_LTE_NET_STATUS', '1,0,0,0,0,0', attrs=['smsUnreadCount', 'sigLevel', 'rfInfoRsrp', 'rfInfoRsrq', 'rfInfoSnr', 'smsSendResult', 'smsSendCause']),
                # 3: ISP
                ActItem(ActItem.GET, 'DEV2_LTE_PROF_STAT', '1,0,0,0,0,0', attrs=['ispName']),
                # 4: Cells (5G Metrics)
                ActItem(ActItem.GL, 'DEV2_LTE_SERVING_CELL_INFO', '0,0,0,0,0,0', attrs=[]),
            ]
            _, values = self.client.req_act(acts)
            return values

        values = await asyncio.to_thread(fetch_all)
        
        lte_status = LTEStatus()
        if values:
            try:
                if len(values) > 0 and values[0]:
                    v0 = values[0]
                    lte_status.enable = _safe_int(v0.get('enable'))
                    lte_status.connect_status = _safe_int(v0.get('connectStatus'))
                    lte_status.network_type = _safe_int(v0.get('networkType'))
                    lte_status.sim_status = _safe_int(v0.get('simStatus'))
                if len(values) > 1 and values[1]:
                    v1 = values[1]
                    lte_status.total_statistics = _safe_int(v1.get('totalStatistics'))
                    lte_status.cur_rx_speed = _safe_int(v1.get('curRxSpeed'))
                    lte_status.cur_tx_speed = _safe_int(v1.get('curTxSpeed'))
                if len(values) > 2 and values[2]:
                    v2 = values[2]
                    lte_status.sms_unread_count = _safe_int(v2.get('smsUnreadCount'))
                    lte_status.sig_level = _safe_int(v2.get('sigLevel'))
                    lte_status.rsrp = _safe_int(v2.get('rfInfoRsrp'))
                    lte_status.rsrq = _safe_int(v2.get('rfInfoRsrq'))
                    lte_status.snr = _safe_int(v2.get('rfInfoSnr'))
                if len(values) > 3 and values[3]:
                    lte_status.isp_name = values[3].get('ispName')
            except Exception as err:
                _LOGGER.debug("Error mapping LTE status: %s", err)

        # 2. Parse Extra Metrics
        extra = {}
        if values:
            if len(values) > 0 and values[0]:
                extra["roaming"] = values[0].get("roamingStatus")
                extra["endc_support"] = values[0].get("endcStatus")
            if len(values) > 1 and values[1]:
                extra["daily_usage"] = values[1].get("dailyFlow")
                extra["usage_limit"] = values[1].get("limitation")
                extra["payment_day"] = values[1].get("paymentDay")
            if len(values) > 2 and values[2]:
                res_code = _safe_int(values[2].get("smsSendResult"), 3)
                extra["sms_send_result"] = {0:"Success", 1:"Fail", 2:"Sending", 3:"Idle"}.get(res_code, f"Unknown ({res_code})")
                cause_code = _safe_int(values[2].get("smsSendCause"), 0)
                extra["sms_send_cause"] = "None" if cause_code == 0 else f"Error {cause_code}"

            if len(values) > 4 and isinstance(values[4], list):
                for cell in values[4]:
                    if cell.get('cellConnectionStatus') != '1':
                        continue
                    net_type = cell.get('networkType')
                    prefix = "nr_" if net_type == '8' else "lte_"
                    for k, v in cell.items():
                        if net_type == '8':
                            if k == 'SSRSRP': extra[f"{prefix}rsrp"] = v
                            elif k == 'SSRSRQ': extra[f"{prefix}rsrq"] = v
                            elif k == 'SSSINR': extra[f"{prefix}snr"] = v
                        else:
                            if k == 'RSRP': extra[f"{prefix}rsrp"] = v
                            elif k == 'RSRQ': extra[f"{prefix}rsrq"] = v
                            elif k == 'SNR': extra[f"{prefix}snr"] = v
                        
                        if k == 'band': extra[f"{prefix}band"] = v
                        elif k == 'RSSI': extra[f"{prefix}rssi"] = v
                        elif k == 'PCI': extra[f"{prefix}pci"] = v
                        elif k == 'TAC': extra[f"{prefix}tac"] = v
                        elif k == 'cid': extra[f"{prefix}cid"] = v
                        elif k == 'ARFCN': extra[f"{prefix}arfcn"] = v
                        elif k == 'downlinkModType': extra[f"{prefix}dl_mod"] = v
                        elif k == 'uplinkModType': extra[f"{prefix}ul_mod"] = v
                        elif k == 'downBandWidth': # Values are in KHz, convert to MHz string
                            try:
                                extra[f"{prefix}dl_bw"] = f"{int(float(v)) // 1000}MHz"
                            except:
                                extra[f"{prefix}dl_bw"] = v
                        elif k == 'CQI': extra[f"{prefix}cqi"] = v
                        elif k == 'txPowerPUCCH': extra[f"{prefix}tx_power"] = v
                        elif k == 'numRbs': extra[f"{prefix}rbs"] = v

        return lte_status, extra

    async def get_ipv4_status(self):
        """Get IPv4 status."""
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
