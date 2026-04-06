"""Tests for TP-Link Router 5G API."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from custom_components.tplink_router_5g.api import (
    TPLinkRouter5GAPI,
    _safe_int,
)


def test_api_safe_int():
    """Test the safe int helper."""
    assert _safe_int("123") == 123
    assert _safe_int("12.3") == 12
    assert _safe_int("invalid") == 0
    assert _safe_int(None) == 0
    assert _safe_int("") == 0
    assert _safe_int("  ") == 0


@pytest.mark.asyncio
async def test_api_get_lte_unexpected_error():
    """Test get_lte_and_extra_status with an unexpected exception."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")
    with patch(
        "custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client"
    ) as mock_client:
        client = mock_client.return_value
        client.req_act = MagicMock(side_effect=RuntimeError("Extreme failure"))
        client.ActItem = MagicMock()

        # Should not crash, returns empty status
        _lte, extra = await api.get_lte_and_extra_status()
        assert extra == {}


def test_api_init():
    """Test API initialization and host normalization."""
    api = TPLinkRouter5GAPI("192.168.1.1", "user", "pass")
    assert api.host == "http://192.168.1.1"

    api2 = TPLinkRouter5GAPI("https://192.168.1.1", "user", "pass")
    assert api2.host == "https://192.168.1.1"


@pytest.mark.asyncio
async def test_api_logout_error():
    """Test logout with an exception."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")
    api.client = MagicMock()
    api.client.logout.side_effect = Exception("Logout failed")

    # Should not raise exception
    await api.logout()


@pytest.mark.asyncio
async def test_api_send_sms_no_support():
    """Test sending SMS when client does not support it."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")

    with patch(
        "custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client"
    ) as mock_client:
        client_instance = mock_client.return_value
        # Delete send_sms from mock if it exists (MagicMock might have it)
        if hasattr(client_instance, "send_sms"):
            del client_instance.send_sms

        await api.send_sms("12345", "test")
        # Should log warning but not crash


@pytest.mark.asyncio
async def test_api_get_status():
    """Test getting status."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")
    with patch(
        "custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client"
    ) as mock_client:
        mock_client.return_value.get_status = MagicMock(return_value={"status": "ok"})
        assert await api.get_status() == {"status": "ok"}


@pytest.mark.asyncio
async def test_api_optional_methods_missing():
    """Test optional methods when client lacks them."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")
    with patch(
        "custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client"
    ) as mock_client:
        client = mock_client.return_value
        if hasattr(client, "get_ipv4_status"):
            del client.get_ipv4_status
        if hasattr(client, "get_vpn_status"):
            del client.get_vpn_status

        assert await api.get_ipv4_status() is None
        assert await api.get_vpn_status() is None


@pytest.mark.asyncio
async def test_api_set_wifi():
    """Test set_wifi."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")
    with patch(
        "custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client"
    ) as mock_client:
        client = mock_client.return_value
        client.set_wifi = MagicMock()
        await api.set_wifi("wifi_2g", True)
        client.set_wifi.assert_called_once_with("wifi_2g", True)


@pytest.mark.asyncio
async def test_api_send_sms():
    """Test sending SMS."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")

    with patch(
        "custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client"
    ) as mock_client:
        client_instance = mock_client.return_value
        client_instance.send_sms = MagicMock()

        await api.send_sms("12345", "test")
        client_instance.send_sms.assert_called_once_with("12345", "test")


@pytest.mark.asyncio
async def test_api_reboot():
    """Test rebooting."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")

    with patch(
        "custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client"
    ) as mock_client:
        client_instance = mock_client.return_value
        client_instance.reboot = MagicMock()

        await api.reboot()
        client_instance.reboot.assert_called_once()


@pytest.mark.asyncio
async def test_api_get_lte_legacy():
    """Test get_lte_and_extra_status with legacy method."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")
    with patch(
        "custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client"
    ) as mock_client:
        client = mock_client.return_value
        if hasattr(client, "req_act"):
            del client.req_act
        client.get_lte_status = MagicMock(return_value="legacy_lte")

        lte, extra = await api.get_lte_and_extra_status()
        assert lte == "legacy_lte"
        assert extra == {}


@pytest.mark.asyncio
async def test_api_get_lte_full():
    """Test get_lte_and_extra_status with req_act (full metrics)."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")
    with patch(
        "custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client"
    ) as mock_client:
        client = mock_client.return_value
        client.req_act = MagicMock()
        client.ActItem = MagicMock()
        client.ActItem.GET = "GET"
        client.ActItem.GL = "GL"

        # Mock values returned by req_act
        mock_values = [
            # 0: Link Config
            {
                "enable": "1",
                "connectStatus": "2",
                "networkType": "8",
                "simStatus": "1",
                "roamingStatus": "0",
                "endcStatus": "1",
            },
            # 1: Data Usage
            {
                "totalStatistics": "1000",
                "curRxSpeed": "100",
                "curTxSpeed": "50",
                "dailyFlow": "200",
                "limitation": "10000",
                "paymentDay": "1",
            },
            # 2: Net Status
            {
                "smsUnreadCount": "5",
                "sigLevel": "4",
                "rfInfoRsrp": "-80",
                "rfInfoRsrq": "-10",
                "rfInfoSnr": "20",
                "smsSendResult": "0",
                "smsSendCause": "0",
                "regStat": "1",
                "srvStat": "2",
            },
            # 3: ISP
            {"ispName": "MyISP"},
            # 4: Cells (5G Metrics)
            [
                {
                    "cellConnectionStatus": "1",
                    "networkType": "8",  # NR
                    "SSRSRP": "-85",
                    "SSRSRQ": "-12",
                    "SSSINR": "150",
                    "band": "78",
                },
                {
                    "cellConnectionStatus": "1",
                    "networkType": "7",  # LTE
                    "RSRP": "-90",
                    "RSRQ": "-15",
                    "SNR": "10",
                    "band": "3",
                },
            ],
        ]
        client.req_act.return_value = (None, mock_values)

        lte, extra = await api.get_lte_and_extra_status()

        # Check LTEStatus mapping
        assert lte.enable == 1
        assert lte.connect_status == 2
        assert lte.network_type == 8
        assert lte.total_statistics == 1000
        assert lte.isp_name == "MyISP"
        assert lte.sms_unread_count == 5

        # Check Extra metrics
        assert extra["roaming"] == "0"
        assert extra["endc_support"] == "1"
        assert extra["daily_usage"] == 200
        assert extra["usage_limit"] == 10000
        assert extra["data_left"] == 9800
        assert extra["sms_send_result"] == "Success"
        assert extra["registration_status"] == "Registered"
        assert extra["service_status"] == "Full"

        # Check 5G NR metrics
        assert extra["nr_rsrp"] == -85
        assert extra["nr_snr"] == 150
        assert extra["nr_band"] == "78"

        # Check LTE Anchor metrics
        assert extra["lte_rsrp"] == -90
        assert extra["lte_snr"] == 10
        assert extra["lte_band"] == "3"


@pytest.mark.asyncio
async def test_api_ensure_client_concurrent():
    """Test concurrent client initialization to hit the lock logic."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")

    with patch(
        "custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client"
    ) as mock_get_client:
        mock_get_client.return_value = MagicMock()

        # Call multiple times concurrently
        await asyncio.gather(
            api._ensure_client(), api._ensure_client(), api._ensure_client()
        )

        # get_client should only be called once
        mock_get_client.assert_called_once()


@pytest.mark.asyncio
async def test_api_get_lte_none():
    """Test get_lte_and_extra_status when no methods are available."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")
    with patch(
        "custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client"
    ) as mock_client:
        client = mock_client.return_value
        if hasattr(client, "req_act"):
            del client.req_act
        if hasattr(client, "get_lte_status"):
            del client.get_lte_status

        lte, extra = await api.get_lte_and_extra_status()
        assert lte is None
        assert extra == {}


@pytest.mark.asyncio
async def test_api_get_lte_cell_skipped():
    """Test get_lte_and_extra_status with disconnected cells."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")
    with patch(
        "custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client"
    ) as mock_client:
        client = mock_client.return_value
        client.req_act = MagicMock()
        client.ActItem = MagicMock()

        mock_values = [
            {},
            {},
            {},
            {},
            [
                {"cellConnectionStatus": "0", "networkType": "8"},  # Skipped
                {
                    "cellConnectionStatus": "1",
                    "networkType": "7",  # LTE
                    "RSSI": "50",
                    "band": "20",
                    "downlinkModType": "64QAM",
                    "upBandWidth": "10000",
                },
            ],
        ]
        client.req_act.return_value = (None, mock_values)

        _lte, extra = await api.get_lte_and_extra_status()
        assert "nr_rsrp" not in extra
        assert extra["lte_rssi"] == 50
        assert extra["lte_band"] == "20"
        assert extra["lte_dl_mod"] == "64QAM"
        assert extra["lte_ul_bw"] == 10
