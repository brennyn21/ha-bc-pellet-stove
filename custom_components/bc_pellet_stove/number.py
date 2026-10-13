"""Number platform for BC Pellet Stove."""

from __future__ import annotations

from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BAND_RANGE, DOMAIN, TEMP_RANGE_C, TEMP_RANGE_F
from .coordinator import PelletStoveCoordinator
from .entity import PelletStoveEntity, status_int


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up pellet stove number controls."""
    coordinator: PelletStoveCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            PelletStoveSetTempNumber(coordinator),
            PelletStoveBurnLevelNumber(coordinator),
            PelletStoveBandNumber(
                coordinator,
                "turn_off_above",
                "turnOffAbove",
                "/turnoffabove",
                "Turn off above",
                "mdi:thermometer-chevron-up",
            ),
            PelletStoveBandNumber(
                coordinator,
                "turn_on_below",
                "turnOnBelow",
                "/turnonbelow",
                "Turn on below",
                "mdi:thermometer-chevron-down",
            ),
        ]
    )


class PelletStoveSetTempNumber(PelletStoveEntity, NumberEntity):
    """Target temperature via GET /settemp."""

    _attr_name = "Set temperature"
    _attr_icon = "mdi:thermostat"
    _attr_mode = NumberMode.AUTO

    def __init__(self, coordinator: PelletStoveCoordinator) -> None:
        super().__init__(coordinator, "set_temp")

    @property
    def native_value(self) -> float | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("setTemp")

    @property
    def native_min_value(self) -> float:
        return float(self._temp_range[0])

    @property
    def native_max_value(self) -> float:
        return float(self._temp_range[1])

    @property
    def native_step(self) -> float:
        return 1.0

    @property
    def native_unit_of_measurement(self) -> str | None:
        if not self.coordinator.data:
            return UnitOfTemperature.FAHRENHEIT
        unit = self.coordinator.data.get("tempUnit", "F")
        return UnitOfTemperature.FAHRENHEIT if unit == "F" else UnitOfTemperature.CELSIUS

    @property
    def _temp_range(self) -> tuple[int, int]:
        if self.coordinator.data and self.coordinator.data.get("tempUnit") == "C":
            return TEMP_RANGE_C
        return TEMP_RANGE_F

    async def async_set_native_value(self, value: float) -> None:
        unit = "C" if self.coordinator.data and self.coordinator.data.get("tempUnit") == "C" else "F"
        await self.coordinator.api.async_set_temperature(int(value), unit)
        await self.coordinator.async_request_refresh()


class PelletStoveBurnLevelNumber(PelletStoveEntity, NumberEntity):
    """Burn level (1–5) via GET /level."""

    _attr_name = "Burn level"
    _attr_icon = "mdi:fire"
    _attr_mode = NumberMode.AUTO
    _attr_native_min_value = 1
    _attr_native_max_value = 5
    _attr_native_step = 1

    def __init__(self, coordinator: PelletStoveCoordinator) -> None:
        super().__init__(coordinator, "burn_level")

    @property
    def native_value(self) -> float | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("level")

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.api.async_set_level(int(value))
        await self.coordinator.async_request_refresh()


class PelletStoveBandNumber(PelletStoveEntity, NumberEntity):
    """Temp-mode band in degrees from the setpoint. 0 turns that side off."""

    _attr_mode = NumberMode.BOX
    _attr_native_min_value = BAND_RANGE[0]
    _attr_native_max_value = BAND_RANGE[1]
    _attr_native_step = 1

    def __init__(
        self,
        coordinator: PelletStoveCoordinator,
        key: str,
        status_key: str,
        path: str,
        name: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator, key)
        self._status_key = status_key
        self._path = path
        self._attr_name = name
        self._attr_icon = icon

    @property
    def _in_temp_mode(self) -> bool:
        mode = (self.coordinator.data or {}).get("mode", "")
        return str(mode).lower() == "temp"

    async def async_added_to_hass(self) -> None:
        """Hide the band until the stove is in Temp mode."""
        await super().async_added_to_hass()
        self._sync_visibility()

    def _handle_coordinator_update(self) -> None:
        """Show the band only while the stove stays in Temp mode."""
        self._sync_visibility()
        super()._handle_coordinator_update()

    def _sync_visibility(self) -> None:
        """Match the stove page: band controls are hidden outside Temp mode."""
        if self.registry_entry is None:
            return
        registry = er.async_get(self.hass)
        hidden_by = self.registry_entry.hidden_by
        if self._in_temp_mode:
            if hidden_by == er.RegistryEntryHider.INTEGRATION:
                self.registry_entry = registry.async_update_entity(
                    self.entity_id, hidden_by=None
                )
            return
        if hidden_by is None:
            self.registry_entry = registry.async_update_entity(
                self.entity_id, hidden_by=er.RegistryEntryHider.INTEGRATION
            )

    @property
    def native_value(self) -> float | None:
        if not self.coordinator.data:
            return None
        value = status_int(self.coordinator.data, self._status_key)
        return 0 if value is None else value

    @property
    def native_unit_of_measurement(self) -> str | None:
        unit = (self.coordinator.data or {}).get("tempUnit", "F")
        return "°F" if unit == "F" else "°C"

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.api.async_set_band(self._path, int(value))
        await self.coordinator.async_request_refresh()
