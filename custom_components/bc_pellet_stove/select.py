"""Select platform for BC Pellet Stove."""

from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODES
from .coordinator import PelletStoveCoordinator
from .entity import PelletStoveEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up pellet stove mode select."""
    coordinator: PelletStoveCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PelletStoveModeSelect(coordinator)])


class PelletStoveModeSelect(PelletStoveEntity, SelectEntity):
    """Operation mode via GET /mode/{mode}."""

    _attr_name = "Mode"
    _attr_icon = "mdi:thermostat"
    _attr_options = MODES

    def __init__(self, coordinator: PelletStoveCoordinator) -> None:
        super().__init__(coordinator, "mode")

    @property
    def current_option(self) -> str | None:
        if not self.coordinator.data:
            return None
        mode = self.coordinator.data.get("mode", "Manual")
        return str(mode).lower()

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.api.async_set_mode(option)
        await self.coordinator.async_request_refresh()
