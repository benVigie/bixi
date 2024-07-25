"""Sensor platform for Bixi integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
)
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .bixi_helper import get_uid_for_station_name
from .const import DOMAIN
from .coordinator import BixiCoordinator

ENTITY_ID_SENSOR_FORMAT = SENSOR_DOMAIN + ".bixi_{}"


class BixiStation:
    name: str


@dataclass(kw_only=True, frozen=True)
class BixiSensorEntityDescription(SensorEntityDescription):
    """Describes a Bixi sensor entity."""

    value_fn: Callable[[BixiStation], str | int]


def _create_sensors_for_station(
    station: str,
) -> tuple[BixiSensorEntityDescription, ...]:
    station_id = get_uid_for_station_name(station)
    return (
        BixiSensorEntityDescription(
            key=f"{station_id}_name",
            translation_key="station_name",
            name=f"{station_id} Station Name",
            icon="mdi:tag",
            value_fn=lambda data: data.get("name", "unknown"),
        ),
        BixiSensorEntityDescription(
            key=f"{station_id}_docks",
            translation_key="docks",
            name=f"{station_id} Available docks",
            icon="mdi:locker",
            value_fn=lambda data: data.get("docks_available", 0),
            state_class=SensorStateClass.MEASUREMENT,
        ),
        BixiSensorEntityDescription(
            key=f"{station_id}_bikes",
            translation_key="bikes",
            name=f"{station_id} Bikes",
            icon="mdi:bicycle",
            value_fn=lambda data: data.get("bikes_available", 0),
            state_class=SensorStateClass.MEASUREMENT,
        ),
        BixiSensorEntityDescription(
            key=f"{station_id}_e-bikes",
            translation_key="e-bikes",
            name=f"{station_id} E-bikes",
            icon="mdi:bicycle-electric",
            value_fn=lambda data: data.get("ebikes_available", 0),
            state_class=SensorStateClass.MEASUREMENT,
        ),
    )


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Sun sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    bixi_stations = entry.data["stations"]

    # Create all needed sensors for each stations
    sensors: list[BixiSensor] = []
    for station in bixi_stations:
        newitems = _create_station_sensors(coordinator, station, entry.entry_id)
        sensors.extend(newitems)

    async_add_entities(sensors)
    # async_add_entities(
    #     [
    #         BixiSensor(coordinator, bixi_stations, description, entry.entry_id)
    #         for description in SENSOR_TYPES
    #     ]
    # )


def _create_station_sensors(
    coordinator: any, station_name: str, entry_id: str
) -> list[BixiSensor]:
    return [
        BixiSensor(coordinator, station_name, description, entry_id)
        for description in _create_sensors_for_station(station_name)
    ]


class BixiSensor(CoordinatorEntity[BixiCoordinator], SensorEntity):
    """Representation of a Bixi Sensor."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    entity_description: BixiSensorEntityDescription

    def __init__(
        self,
        coordinator: BixiCoordinator,
        station_name: str,
        entity_description: BixiSensorEntityDescription,
        entry_id: str,
    ) -> None:
        """Initiate Bixi Sensor."""
        # Pass coordinator to CoordinatorEntity.
        super().__init__(coordinator)

        self.entity_description = entity_description
        self.entity_id = ENTITY_ID_SENSOR_FORMAT.format(entity_description.key)
        self._attr_unique_id = f"{entry_id}-{entity_description.key}"
        self.station_name = station_name
        self._attr_device_info = DeviceInfo(
            name=entry_id,
            identifiers={(DOMAIN, entry_id)},
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> int | str:
        """Return value of sensor."""
        return self.entity_description.value_fn(
            self.coordinator.data[self.station_name]
        )
