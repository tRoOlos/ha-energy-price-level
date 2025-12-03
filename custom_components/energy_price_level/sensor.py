"""Sensor platform for Energy Price Level integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CONF_SOURCE_SENSOR,
    DOMAIN,
    LEVEL_CHEAP,
    LEVEL_EXPENSIVE,
    LEVEL_NORMAL,
    LEVEL_VERY_CHEAP,
    LEVEL_VERY_EXPENSIVE,
    THRESHOLD_CHEAP,
    THRESHOLD_EXPENSIVE,
    THRESHOLD_NORMAL_HIGH,
    THRESHOLD_VERY_CHEAP,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Energy Price Level sensor from a config entry."""
    source_sensor = config_entry.data[CONF_SOURCE_SENSOR]

    async_add_entities([EnergyPriceLevelSensor(hass, source_sensor, config_entry.entry_id)])


class EnergyPriceLevelSensor(RestoreEntity, SensorEntity):
    """Representation of an Energy Price Level sensor."""

    _attr_has_entity_name = True
    _attr_translation_key = "price_level"

    def __init__(self, hass: HomeAssistant, source_sensor: str, entry_id: str) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._source_sensor = source_sensor
        self._attr_unique_id = f"{DOMAIN}_{entry_id}"
        self._attr_device_info = None
        self._state = None
        self._attributes: dict[str, Any] = {}
        self._unsub_state_changed = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Price Level"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return self._attributes

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        # Restore previous state
        if (last_state := await self.async_get_last_state()) is not None:
            self._state = last_state.state
            self._attributes = dict(last_state.attributes)

        # Subscribe to source sensor changes
        self._unsub_state_changed = async_track_state_change_event(
            self.hass, [self._source_sensor], self._async_source_sensor_changed
        )

        # Initial update
        await self._async_update_from_source()

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from hass."""
        if self._unsub_state_changed:
            self._unsub_state_changed()

    @callback
    async def _async_source_sensor_changed(self, event) -> None:
        """Handle source sensor state changes."""
        await self._async_update_from_source()

    async def _async_update_from_source(self) -> None:
        """Update sensor from source sensor."""
        source_state = self.hass.states.get(self._source_sensor)

        if source_state is None:
            _LOGGER.warning("Source sensor %s not found", self._source_sensor)
            return

        try:
            # Get daily average from source sensor state
            daily_average = float(source_state.state)
        except (ValueError, TypeError):
            _LOGGER.warning(
                "Source sensor %s has invalid state: %s",
                self._source_sensor,
                source_state.state,
            )
            return

        # Get hourly prices from attributes
        # Common attribute names for hourly prices in different integrations
        hourly_prices = None
        for attr_name in ["raw_today", "today", "prices_today", "hourly_prices"]:
            if attr_name in source_state.attributes:
                hourly_prices = source_state.attributes[attr_name]
                break

        if hourly_prices is None:
            _LOGGER.warning(
                "No hourly prices found in source sensor %s attributes",
                self._source_sensor,
            )
            return

        # Calculate price levels for each hour
        price_levels = {}
        current_hour = datetime.now().hour

        for i, price_data in enumerate(hourly_prices):
            # Extract price value (handle different data formats)
            if isinstance(price_data, dict):
                price = price_data.get("value") or price_data.get("price")
            else:
                price = price_data

            if price is None:
                continue

            try:
                price = float(price)
            except (ValueError, TypeError):
                _LOGGER.warning("Invalid price data at index %s: %s", i, price_data)
                continue

            # Calculate percentage relative to daily average
            if daily_average > 0:
                percentage = (price / daily_average) * 100
            else:
                percentage = 100

            # Determine price level
            level = self._get_price_level(percentage)

            # Store with hour as key
            hour_key = f"{i:02d}:00"
            price_levels[hour_key] = {
                "level": level,
                "price": price,
                "percentage": round(percentage, 1),
            }

            # Update current state if this is the current hour
            if i == current_hour:
                self._state = level

        # Update attributes
        self._attributes = {
            "source_sensor": self._source_sensor,
            "daily_average": daily_average,
            "price_levels": price_levels,
            "current_hour": current_hour,
        }

        self.async_write_ha_state()

    def _get_price_level(self, percentage: float) -> str:
        """Determine price level based on percentage of daily average."""
        if percentage <= THRESHOLD_VERY_CHEAP:
            return LEVEL_VERY_CHEAP
        elif percentage <= THRESHOLD_CHEAP:
            return LEVEL_CHEAP
        elif percentage < THRESHOLD_NORMAL_HIGH:
            return LEVEL_NORMAL
        elif percentage < THRESHOLD_EXPENSIVE:
            return LEVEL_EXPENSIVE
        else:
            return LEVEL_VERY_EXPENSIVE
