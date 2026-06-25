"""Switch platform for BC Pellet Stove."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PelletStoveCoordinator
from .entity import PelletStoveEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up pellet stove switches."""
    coordinator: PelletStoveCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PelletStovePowerSwitch(coordinator)])


class PelletStovePowerSwitch(PelletStoveEntity, SwitchEntity):
    """Stove power. Uses GET /power (toggle) when the desired state differs."""

    _attr_name = "Power"
    _attr_icon = "mdi:fire"

    def __init__(self, coordinator: PelletStoveCoordinator) -> None:
        super().__init__(coordinator, "power")

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        return bool(self.coordinator.data.get("power"))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_set_power(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_set_power(False)

    async def _async_set_power(self, on: bool) -> None:
        current = bool(self.coordinator.data.get("power")) if self.coordinator.data else False
        await self.coordinator.api.async_set_power(on, current)
        await self.coordinator.async_request_refresh()
