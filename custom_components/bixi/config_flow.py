"""Config flow for Bixi integration."""

from __future__ import annotations

from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.helpers.selector import selector

from .bixi_helper import CannotConnectError, fetch_bixi_station_names
from .const import (
    CONF_STATIONS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)


class BixiConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bixi."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        errors: dict[str, str] = {}
        if user_input is not None:
            if (
                user_input.get(CONF_STATIONS, None) is None
                or len(user_input[CONF_STATIONS]) == 0
            ):
                errors[CONF_STATIONS] = "no_stations"
            if (
                user_input.get(CONF_SCAN_INTERVAL, None) is None
                or user_input[CONF_SCAN_INTERVAL] < MIN_SCAN_INTERVAL
                or user_input[CONF_SCAN_INTERVAL] > MAX_SCAN_INTERVAL
            ):
                errors[CONF_SCAN_INTERVAL] = "invalid_scan_interval"
            # Save config if everything seems fine
            if len(errors) == 0:
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
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=DEFAULT_SCAN_INTERVAL,  # type: ignore  # noqa: PGH003
                ): cv.positive_int,
            }
        except CannotConnectError:
            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=errors
        )
