"""Sensor platform for BC Pellet Stove."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, SIGNAL_STRENGTH_DECIBELS, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PelletStoveCoordinator
from .entity import PelletStoveEntity


def _status_number(data: dict[str, Any] | None, key: str) -> float | None:
    """Read a numeric /status field; null/empty means unavailable."""
    if not data:
        return None
    value = data.get(key)
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _status_str(data: dict[str, Any] | None, key: str) -> str | None:
    if not data:
        return None
    value = data.get(key)
    if value is None or value == "":
        return None
    return str(value)


def _status_unix(data: dict[str, Any] | None, key: str) -> datetime | None:
    value = _status_number(data, key)
    if value is None or value <= 0:
        return None
    return datetime.fromtimestamp(int(value), tz=timezone.utc)


def _temp_unit(data: dict[str, Any] | None) -> str | None:
    if not data:
        return None
    unit = data.get("tempUnit", "F")
    return UnitOfTemperature.FAHRENHEIT if unit == "F" else UnitOfTemperature.CELSIUS


def _timer_remaining_minutes(data: dict[str, Any] | None) -> float | None:
    if not data or not data.get("timerActive"):
        return None
    hours = _status_number(data, "timerHours") or 0
    minutes = _status_number(data, "timerMinutes") or 0
    return round(hours * 60 + minutes, 1)


def _schedule_id(data: dict[str, Any] | None) -> int | None:
    if not data or not data.get("scheduleActive"):
        return None
    value = _status_number(data, "scheduleId")
    if value is None or value < 0:
        return None
    return int(value)


def _layout_label(data: dict[str, Any] | None) -> str | None:
    if not data or "alternateLayout" not in data:
        return None
    return "Alt" if data.get("alternateLayout") else "Original"


@dataclass(frozen=True, kw_only=True)
class PelletStoveSensorDescription(SensorEntityDescription):
    """Sensor mapped from a /status JSON field."""

    value_fn: Callable[[dict[str, Any] | None], Any]
    unit_fn: Callable[[dict[str, Any] | None], str | None] | None = None


SENSORS: tuple[PelletStoveSensorDescription, ...] = (
    PelletStoveSensorDescription(
        key="current_temp",
        name="Current temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _status_number(d, "currentTemp"),
        unit_fn=_temp_unit,
    ),
    PelletStoveSensorDescription(
        key="aux_temp",
        name="Aux temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _status_number(d, "auxTemp"),
        unit_fn=_temp_unit,
    ),
    PelletStoveSensorDescription(
        key="aux_humidity",
        name="Aux humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda d: _status_number(d, "auxHumidity"),
    ),
    PelletStoveSensorDescription(
        key="manual_on_temp",
        name="Manual on temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _status_number(d, "manualOnTemp"),
        unit_fn=_temp_unit,
    ),
    PelletStoveSensorDescription(
        key="manual_off_temp",
        name="Manual off temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _status_number(d, "manualOffTemp"),
        unit_fn=_temp_unit,
    ),
    PelletStoveSensorDescription(
        key="runtime",
        name="Power changed at",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-outline",
        value_fn=lambda d: _status_unix(d, "runtime"),
    ),
    PelletStoveSensorDescription(
        key="timer_remaining",
        name="Timer remaining",
        icon="mdi:timer-outline",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="min",
        value_fn=_timer_remaining_minutes,
    ),
    PelletStoveSensorDescription(
        key="timer_type",
        name="Timer type",
        icon="mdi:timer-cog-outline",
        value_fn=lambda d: _status_str(d, "timerType") if d and d.get("timerActive") else None,
    ),
    PelletStoveSensorDescription(
        key="schedule_id",
        name="Active schedule",
        icon="mdi:calendar-clock",
        value_fn=_schedule_id,
    ),
    PelletStoveSensorDescription(
        key="temp_unit",
        name="Temperature unit",
        icon="mdi:temperature-fahrenheit",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _status_str(d, "tempUnit"),
    ),
    PelletStoveSensorDescription(
        key="dp_layout",
        name="DP layout",
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_layout_label,
    ),
    PelletStoveSensorDescription(
        key="timezone",
        name="Timezone offset",
        icon="mdi:earth",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement="h",
        value_fn=lambda d: _status_number(d, "timezone"),
    ),
    PelletStoveSensorDescription(
        key="module_time",
        name="Module time",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _status_unix(d, "moduleTimeUnix"),
    ),
    PelletStoveSensorDescription(
        key="ip_address",
        name="IP address",
        icon="mdi:ip-network",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _status_str(d, "ipAddress"),
    ),
    PelletStoveSensorDescription(
        key="wifi_ssid",
        name="WiFi SSID",
        icon="mdi:wifi",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _status_str(d, "wifiSSID"),
    ),
    PelletStoveSensorDescription(
        key="wifi_status",
        name="WiFi status",
        icon="mdi:wifi-check",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _status_str(d, "wifiStatus"),
    ),
    PelletStoveSensorDescription(
        key="mqtt_username",
        name="MQTT username",
        icon="mdi:account-key",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _status_str(d, "mqttUsername"),
    ),
    PelletStoveSensorDescription(
        key="error_code",
        name="Error code",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("errorCode") if d else None,
    ),
    PelletStoveSensorDescription(
        key="firmware_version",
        name="Firmware version",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:chip",
        value_fn=lambda d: _status_str(d, "firmwareVersion"),
    ),
    PelletStoveSensorDescription(
        key="wifi_rssi",
        name="WiFi RSSI",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("wifiRSSI") if d else None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up pellet stove sensors."""
    coordinator: PelletStoveCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PelletStoveSensor(coordinator, description) for description in SENSORS
    )


class PelletStoveSensor(PelletStoveEntity, SensorEntity):
    """Generic /status sensor."""

    entity_description: PelletStoveSensorDescription

    def __init__(
        self,
        coordinator: PelletStoveCoordinator,
        description: PelletStoveSensorDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def native_unit_of_measurement(self) -> str | None:
        if self.entity_description.unit_fn is not None:
            return self.entity_description.unit_fn(self.coordinator.data)
        return self.entity_description.native_unit_of_measurement
