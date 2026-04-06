"""Tests for TP-Link Router 5G API."""

from unittest.mock import MagicMock, patch
import asyncio
import pytest

from custom_components.tplink_router_5g.api import (
    TPLinkRouter5GAPI,
    _safe_int,
    _parse_uptime_to_seconds,
)


def test_api_safe_int():
    """Test the safe int helper."""
    assert _safe_int("123") == 123
    assert _safe_int("12.3") == 12
    assert _safe_int("invalid") == 0
    assert _safe_int(None) == 0


def test_api_parse_uptime():
    """Test the uptime parsing helper."""
    assert _parse_uptime_to_seconds("0 days 08:47:33") == 31653
    assert _parse_uptime_to_seconds("1 days, 01:01:01") == 90061
    assert _parse_uptime_to_seconds("01:01:01") == 3661
    assert _parse_uptime_to_seconds("invalid") is None
    assert _parse_uptime_to_seconds("") is None


@pytest.mark.asyncio
async def test_api_get_firmware():
    """Test firmware fetching."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")
    
    with patch("custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client") as mock_client:
        mock_client.return_value.get_firmware = MagicMock(return_value="v1.0")
        assert await api.get_firmware() == "v1.0"


@pytest.mark.asyncio
async def test_api_send_sms():
    """Test sending SMS."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")
    
    with patch("custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client") as mock_client:
        client_instance = mock_client.return_value
        client_instance.send_sms = MagicMock()
        
        await api.send_sms("12345", "test")
        client_instance.send_sms.assert_called_once_with("12345", "test")

@pytest.mark.asyncio
async def test_api_reboot():
    """Test rebooting."""
    api = TPLinkRouter5GAPI("192.168.253.1", "admin", "password")
    
    with patch("custom_components.tplink_router_5g.api.TplinkRouterProvider.get_client") as mock_client:
        client_instance = mock_client.return_value
        client_instance.reboot = MagicMock()
        
        await api.reboot()
        client_instance.reboot.assert_called_once()
