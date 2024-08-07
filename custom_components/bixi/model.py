"""Bixi data model."""

from dataclasses import dataclass

type BixiStationList = dict[str, BixiStation]


@dataclass(frozen=True)
class BixiStation:
    """Bixi station data."""

    name: str
    docks_available: int
    bikes_available: int
    ebikes_available: int
