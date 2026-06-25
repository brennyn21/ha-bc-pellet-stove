"""Base entity for BC Pellet Stove."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_HOST, DOMAIN
from .coordinator import PelletStoveCoordinator


class PelletStoveEntity(CoordinatorEntity[PelletStoveCoordinator]):
    """Shared device info and coordinator access."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: PelletStoveCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Group all entities under one Pellet Stove device."""
        data = self.coordinator.data or {}
        host = self.coordinator.entry.data[CONF_HOST]
        return DeviceInfo(
            identifiers={(DOMAIN, host)},
            name="Pellet Stove",
            manufacturer="BC Innovate",
            model="Pellet Stove WiFi",
            sw_version=data.get("firmwareVersion"),
        )
