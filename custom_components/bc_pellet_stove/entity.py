"""Base entity for BC Pellet Stove."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import stove_base_url, stove_name_from_status
from .const import CONF_DEVICE_ID, CONF_HOST, CONF_NAME, CONF_PORT, DEFAULT_NAME, DEFAULT_PORT, DOMAIN
from .coordinator import PelletStoveCoordinator


def status_int(data: dict[str, Any] | None, key: str) -> int | None:
    """Read an int from /status. Empty string means the setting is cleared."""
    if not data:
        return None
    value = data.get(key)
    if isinstance(value, bool) or value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class PelletStoveEntity(CoordinatorEntity[PelletStoveCoordinator]):
    """Shared device info and coordinator access."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: PelletStoveCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Group this stove's entities under one device that survives an IP change."""
        data = self.coordinator.data or {}
        entry_data = self.coordinator.entry.data
        host = entry_data[CONF_HOST]
        port = entry_data.get(CONF_PORT, DEFAULT_PORT)
        device_id = entry_data.get(CONF_DEVICE_ID, host)
        return DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=stove_name_from_status(
                data, entry_data.get(CONF_NAME, DEFAULT_NAME)
            ),
            manufacturer="BC Innovate",
            model="Pellet Stove WiFi",
            sw_version=data.get("firmwareVersion"),
            configuration_url=stove_base_url(host, port),
        )
