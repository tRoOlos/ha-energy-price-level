"""Config flow for Energy Price Level integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .const import CONF_SOURCE_SENSOR, DOMAIN

_LOGGER = logging.getLogger(__name__)


class EnergyPriceLevelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Energy Price Level."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            source_sensor = user_input[CONF_SOURCE_SENSOR]

            # Validate that the sensor exists
            entity_registry = async_get_entity_registry(self.hass)
            if source_sensor not in entity_registry.entities:
                # Check if it exists in states
                state = self.hass.states.get(source_sensor)
                if state is None:
                    errors[CONF_SOURCE_SENSOR] = "sensor_not_found"
                else:
                    # Sensor exists in states, proceed
                    await self.async_set_unique_id(f"{DOMAIN}_{source_sensor}")
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"Energy Price Level ({source_sensor})",
                        data=user_input,
                    )
            else:
                # Sensor exists in registry
                await self.async_set_unique_id(f"{DOMAIN}_{source_sensor}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Energy Price Level ({source_sensor})",
                    data=user_input,
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_SOURCE_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor"),
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
