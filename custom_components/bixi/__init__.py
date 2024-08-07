"""
The Bixi integration.

This integration will poll every x minutes the bixi API to keep track about available
bikes and dock for a saved list of stations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import BixiCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


@dataclass
class BixiData:
    """BixiData runtime data."""

    stations: list[str]


type BixiConfigEntry = ConfigEntry[BixiData]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    # Setup coordinator
    coordinator = BixiCoordinator(hass, entry.data["stations"])
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.title] = coordinator

    # Set up Bixi from a config entry
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: BixiConfigEntry) -> bool:
    """Unload a config entry."""
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.title)
        return True

    return False
