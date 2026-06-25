"""HTTP client for the Pellet Stove ESP8266 local API."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import MODE_TO_ENDPOINT

_LOGGER = logging.getLogger(__name__)


class PelletStoveApi:
    """Thin wrapper around the stove's built-in HTTP server."""

    def __init__(self, session: aiohttp.ClientSession, host: str, port: int) -> None:
        self._session = session
        self._base_url = f"http://{host}:{port}"

    async def async_get_status(self) -> dict[str, Any]:
        """Fetch the full JSON status document."""
        async with self._session.get(
            f"{self._base_url}/status", timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            response.raise_for_status()
            data: dict[str, Any] = await response.json()
            return data

    async def async_toggle_power(self) -> None:
        """Toggle power via GET /power (device has no explicit on/off param)."""
        async with self._session.get(
            f"{self._base_url}/power", timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            response.raise_for_status()

    async def async_set_power(self, on: bool, current_power: bool) -> None:
        """Set power by toggling only when the desired state differs."""
        if current_power != on:
            await self.async_toggle_power()

    async def async_set_temperature(self, value: int, unit: str) -> None:
        """Set target temperature via GET /settemp."""
        async with self._session.get(
            f"{self._base_url}/settemp",
            params={"val": value, "unit": unit},
            timeout=aiohttp.ClientTimeout(total=10),
        ) as response:
            response.raise_for_status()

    async def async_set_level(self, level: int) -> None:
        """Set burn level via GET /level."""
        async with self._session.get(
            f"{self._base_url}/level",
            params={"val": level},
            timeout=aiohttp.ClientTimeout(total=10),
        ) as response:
            response.raise_for_status()

    async def async_set_mode(self, mode: str) -> None:
        """Set operation mode via GET /mode/{mode}."""
        endpoint = MODE_TO_ENDPOINT[mode]
        async with self._session.get(
            f"{self._base_url}{endpoint}", timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            response.raise_for_status()
