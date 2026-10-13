"""BC Pellet Stove local HTTP integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PelletStoveApi
from .const import CONF_DEVICE_ID, CONF_HOST, CONF_NAME, CONF_PORT, DEFAULT_NAME, DOMAIN
from .coordinator import PelletStoveCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BC Pellet Stove from a config entry."""
    session = async_get_clientsession(hass)
    api = PelletStoveApi(session, entry.data[CONF_HOST], entry.data[CONF_PORT])
    coordinator = PelletStoveCoordinator(hass, entry, api)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload BC Pellet Stove."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: PelletStoveCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Keep an existing stove attached to the same device when its IP changes."""
    if entry.version > 1:
        return True

    data = dict(entry.data)
    data.setdefault(CONF_NAME, DEFAULT_NAME)
    # Device registry currently keys the device by host. Preserve that id.
    data.setdefault(CONF_DEVICE_ID, data[CONF_HOST])
    hass.config_entries.async_update_entry(entry, data=data, version=2)
    _LOGGER.debug("Migrated BC Pellet Stove entry %s to version 2", entry.entry_id)
    return True
