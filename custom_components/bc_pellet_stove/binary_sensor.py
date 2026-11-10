"""Binary sensor platform for BC Pellet Stove."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PelletStoveCoordinator
from .entity import PelletStoveEntity


@dataclass(frozen=True, kw_only=True)
class PelletStoveBinarySensorDescription(BinarySensorEntityDescription):
    """Binary sensor mapped from a /status JSON field."""

    value_fn: Callable[[dict[str, Any] | None], bool | None]


BINARY_SENSORS: tuple[PelletStoveBinarySensorDescription, ...] = (
    PelletStoveBinarySensorDescription(
        key="error",
        name="Error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda d: bool(d.get("error")) if d else None,
    ),
    PelletStoveBinarySensorDescription(
        key="child_lock",
        name="Child lock",
        device_class=BinarySensorDeviceClass.LOCK,
        # HA lock: on=unlocked, off=locked; firmware childLock=true means locked.
        value_fn=lambda d: (not bool(d.get("childLock"))) if d else None,
    ),
    PelletStoveBinarySensorDescription(
        key="initialized",
        name="Initialized",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:check-network",
        value_fn=lambda d: bool(d.get("initialized")) if d else None,
    ),
    PelletStoveBinarySensorDescription(
        key="timer_active",
        name="Timer active",
        icon="mdi:timer-outline",
        value_fn=lambda d: bool(d.get("timerActive")) if d else None,
    ),
    PelletStoveBinarySensorDescription(
        key="schedule_active",
        name="Schedule active",
        icon="mdi:calendar-check",
        value_fn=lambda d: bool(d.get("scheduleActive")) if d else None,
    ),
    PelletStoveBinarySensorDescription(
        key="temp_auto_rules_enabled",
        name="Temp auto rules enabled",
        icon="mdi:thermometer-auto",
        value_fn=lambda d: bool(d.get("tempAutoRulesEnabled")) if d else None,
    ),
    PelletStoveBinarySensorDescription(
        key="manual_auto_temp_enabled",
        name="Manual auto temp enabled",
        icon="mdi:thermometer-lines",
        value_fn=lambda d: bool(d.get("manualAutoTempEnabled")) if d else None,
    ),
    PelletStoveBinarySensorDescription(
        key="manual_use_aux_temp",
        name="Use aux sensor temp",
        icon="mdi:thermometer-bluetooth",
        value_fn=lambda d: bool(d.get("manualUseAuxTemp")) if d else None,
    ),
    PelletStoveBinarySensorDescription(
        key="mqtt_connected",
        name="MQTT connected",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda d: bool(d.get("mqttConnected")) if d else None,
    ),
    PelletStoveBinarySensorDescription(
        key="mqtt_enabled",
        name="MQTT enabled",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:cloud-outline",
        value_fn=lambda d: bool(d.get("mqttEnabled")) if d else None,
    ),
    PelletStoveBinarySensorDescription(
        key="ntp_synced",
        name="NTP synced",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:clock-check-outline",
        value_fn=lambda d: bool(d.get("ntpSynced")) if d else None,
    ),
    PelletStoveBinarySensorDescription(
        key="dst_enabled",
        name="Daylight saving",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:clock-time-four-outline",
        value_fn=lambda d: bool(d.get("dstEnabled")) if d else None,
    ),
    PelletStoveBinarySensorDescription(
        key="heartbeat_responded",
        name="MCU heartbeat",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:heart-pulse",
        value_fn=lambda d: bool(d.get("heartbeatResponded")) if d else None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up pellet stove binary sensors."""
    coordinator: PelletStoveCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PelletStoveBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
    )


class PelletStoveBinarySensor(PelletStoveEntity, BinarySensorEntity):
    """Generic /status binary sensor."""

    entity_description: PelletStoveBinarySensorDescription

    def __init__(
        self,
        coordinator: PelletStoveCoordinator,
        description: PelletStoveBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self.coordinator.data)
