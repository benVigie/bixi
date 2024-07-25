"""Bixi service helper"""

import logging
import re

import requests
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client

from .const import BIXI_FETCH_TIMEOUT, BIXI_URL

_LOGGER = logging.getLogger(__name__)


async def fetch_bixi_station_names(hass: HomeAssistant) -> list[str]:
    """Retrieve the complete list of Bixi stations within their 'just put everything here' api."""
    try:
        async_client = aiohttp_client.async_get_clientsession(hass)
        response = await async_client.get(BIXI_URL)
        json = await response.json()

        stations = []
        for station in json["features"]:
            if "properties" in station and "station" in station["properties"]:
                stations.append(station["properties"]["station"]["name"])

        _LOGGER.info(f"{len(stations)} valid stations on {len(json["features"])} data")
        return stations
    except requests.ConnectTimeout as ex:
        raise requests.ConnectTimeout(
            f"Connection timeout while connecting to Bixi API ({BIXI_FETCH_TIMEOUT}s)"
        ) from ex
    except Exception as ex:
        raise requests.ConnectionError(
            "Connection error while connecting to Bixi API"
        ) from ex


def fetch_stations_data(stations: list[str]) -> dict[str, any]:
    """Fetch bixi stations info for the given station list."""
    try:
        response = requests.get(BIXI_URL, timeout=BIXI_FETCH_TIMEOUT)
        response.raise_for_status()
        json = response.json()
        stations_info = {}
        for station in json["features"]:
            if (
                "properties" in station
                and "station" in station["properties"]
                and "name" in station["properties"]["station"]
                and station["properties"]["station"]["name"] in stations
            ):
                stations_info[station["properties"]["station"]["name"]] = station[
                    "properties"
                ]["station"]
        return stations_info
    except requests.ConnectTimeout as ex:
        raise requests.ConnectTimeout(
            f"Connection timeout while connecting to Bixi API ({BIXI_FETCH_TIMEOUT}s)"
        ) from ex
    except requests.ConnectionError as ex:
        raise CannotConnect("Connection error while connecting to Bixi API") from ex


def get_uid_for_station_name(station_name: str) -> str:
    """Create a unique id for the given station name"""
    x = re.search(
        r"([A-Za-z0-9-ÎÉéèô'. ])+[ \/]{3}([A-Za-z0-9-ÎÉéèô'. ])+", station_name
    )
    if x is not None:
        parts = x.group().lower().split(" / ")
        return f"{re.sub('[^A-Za-z0-9]+', '', parts[0])[0:4]}_{re.sub('[^A-Za-z0-9]+', '', parts[1])[0:4]}"
    # Some of the Bixi stations are not formated as the other ones... Simply kept the max we can
    return re.sub("[^A-Za-z0-9]+", "", station_name.lower())[0:8]


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
