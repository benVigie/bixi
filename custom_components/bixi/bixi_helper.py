"""Bixi service helper."""

import logging
import re

import requests
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client

from .const import BIXI_FETCH_TIMEOUT, BIXI_URL
from .model import BixiStation, BixiStationList

_LOGGER = logging.getLogger(__name__)


async def fetch_bixi_station_names(hass: HomeAssistant) -> list[str]:
    """Retrieve the complete list of Bixi stations within their'just put everything here' api."""  # noqa: E501
    try:
        async_client = aiohttp_client.async_get_clientsession(hass)
        response = await async_client.get(BIXI_URL)
        json = await response.json()

        stations = [
            station["properties"]["station"]["name"]
            for station in json["features"]
            if "properties" in station and "station" in station["properties"]
        ]
        _LOGGER.info(
            "%d valid stations on %d data", len(stations), len(json["features"])
        )
    except requests.ConnectTimeout as ex:
        msg = f"Connection timeout while connecting to Bixi API ({BIXI_FETCH_TIMEOUT}s)"
        raise requests.ConnectTimeout(msg) from ex
    except Exception as ex:
        msg = "Connection error while connecting to Bixi API"
        raise requests.ConnectionError(msg) from ex
    else:
        return stations


def fetch_stations_data(stations: list[str]) -> BixiStationList:
    """Fetch bixi stations info for the given station list."""
    response = requests.get(BIXI_URL, timeout=10)
    response.raise_for_status()
    json = response.json()

    return {
        station["properties"]["station"]["name"]: _parse_bixi_data_to_bixistation(
            station["properties"]["station"]
        )
        for station in json["features"]
        if (
            "properties" in station
            and "station" in station["properties"]
            and "name" in station["properties"]["station"]
            and station["properties"]["station"]["name"] in stations
        )
    }


def get_uid_for_station_name(station_name: str) -> str:
    """Create a unique id for the given station name."""
    x = re.search(
        r"([A-Za-z0-9-ÎÉéèô'. ])+[ \/]{3}([A-Za-z0-9-ÎÉéèô'. ])+", station_name
    )
    if x is not None:
        parts = x.group().lower().split(" / ")
        return f"{re.sub('[^A-Za-z0-9]+', '',
                         parts[0])[0:4]}_{re.sub('[^A-Za-z0-9]+', '', parts[1])[0:4]}"
    # Some of the Bixi stations are not formated as the other ones... Simply kept the max we can  # noqa: E501
    return re.sub("[^A-Za-z0-9]+", "", station_name.lower())[0:8]


def _parse_bixi_data_to_bixistation(bixi_data: dict) -> BixiStation:
    return BixiStation(
        name=bixi_data.get("name", "unknown"),
        docks_available=bixi_data.get("docks_available", 0),
        bikes_available=bixi_data.get("bikes_available", 0),
        ebikes_available=bixi_data.get("ebikes_available", 0),
    )


class CannotConnectError(HomeAssistantError):
    """Error to indicate we cannot connect."""
