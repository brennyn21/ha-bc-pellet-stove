"""Button platform for BC Pellet Stove."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    """Set up pellet stove buttons."""
    coordinator: PelletStoveCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PelletStoveCancelTimerButton(coordinator)])


class PelletStoveCancelTimerButton(PelletStoveEntity, ButtonEntity):
    """Cancel an active timer via GET /timer/cancel."""

    _attr_name = "Cancel timer"
    _attr_icon = "mdi:timer-cancel-outline"

    def __init__(self, coordinator: PelletStoveCoordinator) -> None:
        super().__init__(coordinator, "cancel_timer")

    async def async_press(self) -> None:
        await self.coordinator.api.async_cancel_timer()
        await self.coordinator.async_request_refresh()
