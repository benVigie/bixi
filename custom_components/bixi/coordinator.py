"""Bixi Coordinator. Manage the station updates."""

import logging
from dataclasses import dataclass
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

from .const import BIXI_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class BixiStation:
    """Bixi station data."""

    name: str
    docks_available: int
    bikes_available: int
    ebikes_available: int


class BixiCoordinator(DataUpdateCoordinator[Any]):
    """Bixi data coordinator class."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, stations: list[str]) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=10)
        )
        self._stations = stations

    async def _async_update_data(self) -> Any:
        """Fetch data from API endpoint."""
        try:
            async with async_timeout.timeout(10):
                return await self.hass.async_add_executor_job(self.fetch_data)
        except Exception as err:
            msg = f"Error communicating with API: {err}"
            raise UpdateFailed(msg) from err

    def fetch_data(self) -> Any:
        """Fetch the bixi updates."""
        try:
            response = requests.get(BIXI_URL, timeout=10)
            response.raise_for_status()
            json = response.json()
            stations_update = {}

            stations_update = {
                station["properties"]["station"]["name"]: station["properties"][
                    "station"
                ]
                for station in json["features"]
                if (
                    "properties" in station
                    and "station" in station["properties"]
                    and "name" in station["properties"]["station"]
                    and station["properties"]["station"]["name"] in self._stations
                )
            }
        except requests.HTTPError as err:
            msg = "Cannot retrieve bixi update"
            raise UpdateFailed(msg) from err
        except requests.ConnectTimeout as ex:
            msg = "Connection timeout while connecting to Sanix API"
            raise requests.ConnectTimeout(msg) from ex
        except requests.ConnectionError as ex:
            msg = "Connection error while connecting to Sanix API"
            raise UpdateFailed(msg) from ex
        else:
            return stations_update

    def _parse_bixi_data_to_create_station(self, bixi_data: dict) -> BixiStation:
        return BixiStation(
            name=bixi_data.get("name", "unknown"),
            docks_available=bixi_data.get("docks_available", 0),
            bikes_available=bixi_data.get("bikes_available", 0),
            ebikes_available=bixi_data.get("ebikes_available", 0),
        )
