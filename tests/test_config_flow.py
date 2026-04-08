"""Tests for the TP-Link Router config flow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import AbortFlow, FlowResultType

from custom_components.tplink_router_5g.config_flow import (
    TPLinkRouter5GConfigFlow,
    TPLinkRouter5GOptionsFlow,
    _validate_credentials,
)
from custom_components.tplink_router_5g.const import DEFAULT_NAME


@pytest.mark.asyncio
async def test_validate_credentials_success():
    """Test _validate_credentials success."""
    user_input = {CONF_HOST: "192.168.253.1", CONF_PASSWORD: "pass"}

    with patch(
        "custom_components.tplink_router_5g.config_flow.TPLinkRouter5GAPI"
    ) as mock_api_class:
        mock_api = mock_api_class.return_value
        mock_api.login = AsyncMock()
        mock_api.logout = AsyncMock()
        mock_api.get_firmware = AsyncMock(return_value=MagicMock())
        mock_api.get_status = AsyncMock(return_value=MagicMock())

        await _validate_credentials(user_input)
        mock_api.login.assert_called_once()
        mock_api.logout.assert_called_once()
        mock_api.get_firmware.assert_called_once()
        mock_api.get_status.assert_called_once()


@pytest.mark.asyncio
async def test_config_flow_user_step_already_configured():
    """Test user step when host is already configured."""
    flow = TPLinkRouter5GConfigFlow()
    flow.hass = MagicMock()
    flow.context = {}

    # Mock existing entry
    flow.hass.config_entries.async_entry_for_domain_unique_id.return_value = MagicMock()

    user_input = {
        CONF_NAME: DEFAULT_NAME,
        CONF_HOST: "192.168.253.1",
        CONF_PASSWORD: "password",
    }

    with (
        patch(
            "custom_components.tplink_router_5g.config_flow._validate_credentials",
            return_value=None,
        ),
        pytest.raises(AbortFlow) as excinfo,
    ):
        await flow.async_step_user(user_input)

    assert excinfo.value.reason == "already_configured"


@pytest.mark.asyncio
async def test_config_flow_user_step_success():
    """Test successful config flow user step."""
    flow = TPLinkRouter5GConfigFlow()
    flow.hass = MagicMock()
    flow.context = {}
    flow.hass.config_entries.async_entry_for_domain_unique_id.return_value = None

    user_input = {
        CONF_NAME: DEFAULT_NAME,
        CONF_HOST: "192.168.253.1",
        CONF_USERNAME: "admin",
        CONF_PASSWORD: "password",
    }

    with patch(
        "custom_components.tplink_router_5g.config_flow._validate_credentials",
        return_value=None,
    ):
        result = await flow.async_step_user(user_input)

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == DEFAULT_NAME
    assert result["options"] == user_input


@pytest.mark.asyncio
async def test_config_flow_user_step_errors():
    """Test error branches in config flow user step."""
    flow = TPLinkRouter5GConfigFlow()
    flow.hass = MagicMock()
    flow.context = {}

    with patch(
        "custom_components.tplink_router_5g.config_flow._validate_credentials",
        side_effect=Exception("Unknown"),
    ):
        result = await flow.async_step_user(
            {CONF_NAME: DEFAULT_NAME, CONF_HOST: "192.168.253.1", CONF_PASSWORD: "p"}
        )
        assert result["errors"] == {"base": "cannot_connect"}


def test_async_get_options_flow():
    """Test getting the options flow."""
    flow = TPLinkRouter5GConfigFlow()
    entry = MagicMock()
    options_flow = flow.async_get_options_flow(entry)
    assert isinstance(options_flow, TPLinkRouter5GOptionsFlow)


@pytest.mark.asyncio
async def test_options_flow_init_success():
    """Test successful options flow init step."""
    entry = MagicMock()
    entry.options = {
        CONF_NAME: DEFAULT_NAME,
        CONF_HOST: "192.168.253.1",
        CONF_PASSWORD: "old_password",
    }
    flow = TPLinkRouter5GOptionsFlow(entry)
    flow.hass = MagicMock()

    user_input = {
        CONF_NAME: "New Name",
        CONF_HOST: "192.168.253.1",
        CONF_PASSWORD: "new_password",
    }

    with patch(
        "custom_components.tplink_router_5g.config_flow._validate_credentials",
        return_value=None,
    ):
        result = await flow.async_step_init(user_input)

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_NAME: "New Name",
        CONF_HOST: "192.168.253.1",
        CONF_PASSWORD: "new_password",
    }


@pytest.mark.asyncio
async def test_options_flow_errors():
    """Test error branches in options flow."""
    entry = MagicMock()
    entry.options = {
        CONF_NAME: DEFAULT_NAME,
        CONF_HOST: "192.168.253.1",
        CONF_PASSWORD: "p",
    }
    flow = TPLinkRouter5GOptionsFlow(entry)
    flow.hass = MagicMock()

    with patch(
        "custom_components.tplink_router_5g.config_flow._validate_credentials",
        side_effect=Exception,
    ):
        result = await flow.async_step_init(
            {CONF_NAME: DEFAULT_NAME, CONF_HOST: "192.168.253.1", CONF_PASSWORD: "p"}
        )
        assert result["errors"] == {"base": "cannot_connect"}
