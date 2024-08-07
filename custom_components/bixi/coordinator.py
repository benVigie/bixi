"""Bixi Coordinator. Manage the station updates."""

import logging
from datetime import timedelta
from typing import Any

import async_timeout
import requests
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from custom_components.bixi.model import BixiStationList

from .bixi_helper import fetch_stations_data
from .const import BIXI_FETCH_TIMEOUT, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BixiCoordinator(DataUpdateCoordinator[Any]):
    """Bixi data coordinator class."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, stations: list[str], polling_interval: int
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=polling_interval),
        )
        self._stations = stations
        self._polling_interval = polling_interval

    async def _async_update_data(self) -> Any:
        """Fetch data from API endpoint."""
        try:
            async with async_timeout.timeout(BIXI_FETCH_TIMEOUT):
                return await self.hass.async_add_executor_job(self.fetch_data)
        except Exception as err:
            msg = f"Error communicating with API: {err}"
            raise UpdateFailed(msg) from err

    def fetch_data(self) -> BixiStationList:
        """Fetch the bixi stations updates."""
        try:
            return fetch_stations_data(self._stations)
        except requests.HTTPError as err:
            msg = "Cannot retrieve bixi update"
            raise UpdateFailed(msg) from err
        except requests.ConnectTimeout as ex:
            msg = "Connection timeout while connecting to Sanix API"
            raise requests.ConnectTimeout(msg) from ex
        except requests.ConnectionError as ex:
            msg = "Connection error while connecting to Sanix API"
            raise UpdateFailed(msg) from ex
