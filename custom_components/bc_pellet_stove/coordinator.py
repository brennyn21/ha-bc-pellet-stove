"""Data update coordinator for BC Pellet Stove."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PelletStoveApi
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class PelletStoveCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll GET /status and share the result across all entities."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, api: PelletStoveApi
    ) -> None:
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.entry = entry
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.async_get_status()
        except Exception as err:
            raise UpdateFailed(f"Error fetching stove status: {err}") from err
