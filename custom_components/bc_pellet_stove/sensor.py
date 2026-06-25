"""Sensor platform for BC Pellet Stove."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS, UnitOfTemperature
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
    """Set up pellet stove sensors."""
    coordinator: PelletStoveCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            PelletStoveCurrentTempSensor(coordinator),
            PelletStoveErrorCodeSensor(coordinator),
            PelletStoveFirmwareSensor(coordinator),
            PelletStoveWifiRssiSensor(coordinator),
        ]
    )


class PelletStoveCurrentTempSensor(PelletStoveEntity, SensorEntity):
    """Current room temperature from /status."""

    _attr_name = "Current temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: PelletStoveCoordinator) -> None:
        super().__init__(coordinator, "current_temp")

    @property
    def native_value(self) -> int | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("currentTemp")

    @property
    def native_unit_of_measurement(self) -> str | None:
        if not self.coordinator.data:
            return None
        unit = self.coordinator.data.get("tempUnit", "F")
        return UnitOfTemperature.FAHRENHEIT if unit == "F" else UnitOfTemperature.CELSIUS


class PelletStoveErrorCodeSensor(PelletStoveEntity, SensorEntity):
    """Active error code from the stove MCU."""

    _attr_name = "Error code"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: PelletStoveCoordinator) -> None:
        super().__init__(coordinator, "error_code")

    @property
    def native_value(self) -> int | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("errorCode")


class PelletStoveFirmwareSensor(PelletStoveEntity, SensorEntity):
    """Firmware version reported by the ESP8266 module."""

    _attr_name = "Firmware version"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:chip"

    def __init__(self, coordinator: PelletStoveCoordinator) -> None:
        super().__init__(coordinator, "firmware_version")

    @property
    def native_value(self) -> str | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("firmwareVersion")


class PelletStoveWifiRssiSensor(PelletStoveEntity, SensorEntity):
    """WiFi signal strength of the ESP8266 module."""

    _attr_name = "WiFi RSSI"
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: PelletStoveCoordinator) -> None:
        super().__init__(coordinator, "wifi_rssi")

    @property
    def native_value(self) -> int | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("wifiRSSI")
