"""Data update coordinator for BC Pellet Stove."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PelletStoveApi
from .const import CONF_NAME, CONF_SCAN_INTERVAL, DEFAULT_NAME, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class PelletStoveCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll GET /status and share the result across all entities."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, api: PelletStoveApi
    ) -> None:
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        stove_name = entry.data.get(CONF_NAME, DEFAULT_NAME)
        super().__init__(
            hass,
            _LOGGER,
            name=stove_name,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.entry = entry
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await self.api.async_get_status()
        except Exception as err:
            raise UpdateFailed(f"Error fetching stove status: {err}") from err
        self._sync_name(data)
        return data

    def _sync_name(self, data: dict[str, Any]) -> None:
        """Keep the config entry title aligned with mqttUsername."""
        username = data.get("mqttUsername")
        if not isinstance(username, str) or not username.strip():
            return
        name = username.strip()
        if name == self.entry.data.get(CONF_NAME) and name == self.entry.title:
            return
        self.hass.config_entries.async_update_entry(
            self.entry,
            title=name,
            data={**self.entry.data, CONF_NAME: name},
        )
