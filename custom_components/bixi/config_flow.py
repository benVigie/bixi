"""Config flow for Bixi integration."""

from __future__ import annotations

import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_TIMEOUT
from homeassistant.helpers.selector import selector

from .bixi_helper import CannotConnectError, fetch_bixi_station_names
from .const import CONF_STATIONS, DEFAULT_TIMEOUT, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BixiConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bixi."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if (
                user_input.get(CONF_STATIONS, None) is None
                or len(user_input[CONF_STATIONS]) == 0
            ):
                errors[CONF_STATIONS] = "no_stations"
            else:
                return self.async_create_entry(
                    title=f"Bixi Stations ({', '.join(user_input[CONF_STATIONS])})",
                    data=user_input,
                )

        # Retrieve stations to let the user choose the ones he wants to monitor
        stations: list[str] = []
        try:
            stations = await fetch_bixi_station_names(self.hass)
            data_schema = {
                CONF_STATIONS: selector(
                    {
                        "select": {
                            "options": stations,
                            "multiple": True,
                        }
                    }
                ),
                vol.Required(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,  # type: ignore  # noqa: PGH003
            }
        except CannotConnectError:
            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=errors
        )
