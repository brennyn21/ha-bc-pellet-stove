"""Binary sensor platform for BC Pellet Stove."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PelletStoveCoordinator
from .entity import PelletStoveEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up pellet stove binary sensors."""
    coordinator: PelletStoveCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            PelletStoveErrorBinarySensor(coordinator),
            PelletStoveChildLockBinarySensor(coordinator),
            PelletStoveInitializedBinarySensor(coordinator),
        ]
    )


class PelletStoveErrorBinarySensor(PelletStoveEntity, BinarySensorEntity):
    """Whether the stove is reporting an error condition."""

    _attr_name = "Error"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: PelletStoveCoordinator) -> None:
        super().__init__(coordinator, "error")

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        return bool(self.coordinator.data.get("error"))


class PelletStoveChildLockBinarySensor(PelletStoveEntity, BinarySensorEntity):
    """Child lock state (read-only; no local HTTP control endpoint)."""

    _attr_name = "Child lock"
    _attr_device_class = BinarySensorDeviceClass.LOCK

    def __init__(self, coordinator: PelletStoveCoordinator) -> None:
        super().__init__(coordinator, "child_lock")

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        # HA lock device class: on=unlocked, off=locked; firmware childLock=true means locked.
        return not bool(self.coordinator.data.get("childLock"))


class PelletStoveInitializedBinarySensor(PelletStoveEntity, BinarySensorEntity):
    """Whether UART communication with the stove MCU is established."""

    _attr_name = "Initialized"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:check-network"

    def __init__(self, coordinator: PelletStoveCoordinator) -> None:
        super().__init__(coordinator, "initialized")

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        return bool(self.coordinator.data.get("initialized"))
