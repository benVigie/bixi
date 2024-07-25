"""Bixi Coordinator."""

import logging
from datetime import timedelta

import async_timeout
import requests
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class BixiCoordinator(DataUpdateCoordinator[any]):
    """Bixi data coordinator."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, stations: list[str]) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=10)
        )
        self._stations = stations

    async def _async_update_data(self) -> any:
        """Fetch data from API endpoint."""
        try:
            async with async_timeout.timeout(10):
                return await self.hass.async_add_executor_job(self.fetch_data2)
                # return await self.fetch_data()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def fetch_data(self):
        """Fetch data from Bixi API."""
        client = async_get_clientsession(self.hass)
        response = await client.get(
            "https://layer.bicyclesharing.net/map/v1/mtl/map-inventory"
        )

        json = await response.json()
        stations_update = []
        for station in json["features"]:
            # print(station["properties"]["station"])
            if (
                "properties" in station
                and "station" in station["properties"]
                and "name" in station["properties"]["station"]
                and station["properties"]["station"]["name"] in self._stations
                # and station["properties"]["station"]["name"]
            ):
                stations_update.append(station["properties"]["station"])
        print(stations_update)

    def fetch_data2(self):
        """Fetch the update."""
        try:
            response = requests.get(
                "https://layer.bicyclesharing.net/map/v1/mtl/map-inventory", timeout=10
            )
            response.raise_for_status()
            json = response.json()
            stations_update = {}
            for station in json["features"]:
                # print(station["properties"]["station"])
                if (
                    "properties" in station
                    and "station" in station["properties"]
                    and "name" in station["properties"]["station"]
                    and station["properties"]["station"]["name"] in self._stations
                ):
                    stations_update[station["properties"]["station"]["name"]] = station[
                        "properties"
                    ]["station"]
            return stations_update
        except requests.HTTPError as err:
            if err.response is not None:
                if err.response.status_code == 401:
                    raise Exception("Could not authorize.") from err
        except requests.ConnectTimeout as ex:
            raise requests.ConnectTimeout(
                "Connection timeout while connecting to Sanix API"
            ) from ex
        except requests.ConnectionError as ex:
            raise Exception("Connection error while connecting to Sanix API") from ex
