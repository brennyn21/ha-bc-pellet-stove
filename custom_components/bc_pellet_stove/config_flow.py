"""Config flow for BC Pellet Stove."""

from __future__ import annotations

import logging
import uuid
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PelletStoveApi, stove_name_from_status
from .const import (
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def _form_schema(*, host: str | None = None, port: int = DEFAULT_PORT) -> vol.Schema:
    """Build the setup form, prefilling host only when editing an existing stove."""
    host_field: vol.Marker = (
        vol.Required(CONF_HOST, default=host)
        if host is not None
        else vol.Required(CONF_HOST)
    )
    return vol.Schema(
        {
            host_field: str,
            vol.Required(CONF_PORT, default=port): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=65535)
            ),
        }
    )


class PelletStoveConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle setup for one or more pellet stoves on the local network."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add a stove. Repeat this step once for each stove."""
        return await self._async_handle_settings(user_input, reconfigure=False)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Update the IP address or port of an existing stove."""
        return await self._async_handle_settings(user_input, reconfigure=True)

    async def _async_handle_settings(
        self, user_input: dict[str, Any] | None, *, reconfigure: bool
    ) -> ConfigFlowResult:
        """Validate a stove connection and create or update its config entry."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry() if reconfigure else None

        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            port = int(user_input[CONF_PORT])

            if not host:
                errors[CONF_HOST] = "invalid_host"
            elif self._host_in_use(host, port, entry):
                errors["base"] = "already_configured"
            else:
                session = async_get_clientsession(self.hass)
                api = PelletStoveApi(session, host, port)
                try:
                    status = await api.async_get_status()
                except aiohttp.ClientError as err:
                    _LOGGER.debug("Connection failed for %s:%s — %s", host, port, err)
                    errors["base"] = "cannot_connect"
                except Exception:
                    _LOGGER.exception("Unexpected error connecting to %s:%s", host, port)
                    errors["base"] = "unknown"
                else:
                    username = status.get("mqttUsername")
                    username = username.strip() if isinstance(username, str) else ""
                    name = stove_name_from_status(status, f"{DEFAULT_NAME} ({host})")
                    if username and self._username_in_use(username, entry):
                        return self.async_abort(reason="already_configured")

                    if entry is not None:
                        return self.async_update_reload_and_abort(
                            entry,
                            title=name,
                            data_updates={
                                CONF_NAME: name,
                                CONF_HOST: host,
                                CONF_PORT: port,
                            },
                        )

                    device_id = username or uuid.uuid4().hex
                    await self.async_set_unique_id(device_id)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=name,
                        data={
                            CONF_NAME: name,
                            CONF_HOST: host,
                            CONF_PORT: port,
                            CONF_DEVICE_ID: device_id,
                        },
                    )

        if entry is not None:
            schema = _form_schema(
                host=entry.data.get(CONF_HOST, ""),
                port=entry.data.get(CONF_PORT, DEFAULT_PORT),
            )
            step_id = "reconfigure"
        else:
            schema = _form_schema()
            step_id = "user"

        return self.async_show_form(step_id=step_id, data_schema=schema, errors=errors)

    def _username_in_use(self, username: str, current: ConfigEntry | None) -> bool:
        """Return True when another entry already uses this MQTT username."""
        for entry in self._async_current_entries():
            if current is not None and entry.entry_id == current.entry_id:
                continue
            if username in {
                entry.unique_id,
                entry.data.get(CONF_DEVICE_ID),
                entry.data.get(CONF_NAME),
                entry.title,
            }:
                return True
        return False

    def _host_in_use(
        self, host: str, port: int, current: ConfigEntry | None
    ) -> bool:
        """Return True when another entry already polls this host and port."""
        for entry in self._async_current_entries():
            if current is not None and entry.entry_id == current.entry_id:
                continue
            if (
                entry.data.get(CONF_HOST) == host
                and int(entry.data.get(CONF_PORT, DEFAULT_PORT)) == port
            ):
                return True
        return False
