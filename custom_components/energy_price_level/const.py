"""Constants for the Energy Price Level integration."""

DOMAIN = "energy_price_level"
CONF_SOURCE_SENSOR = "source_sensor"

# Price levels
LEVEL_VERY_CHEAP = "zeer_goedkoop"
LEVEL_CHEAP = "goedkoop"
LEVEL_NORMAL = "normaal"
LEVEL_EXPENSIVE = "duur"
LEVEL_VERY_EXPENSIVE = "zeer_duur"

# Thresholds (percentage of daily average)
THRESHOLD_VERY_CHEAP = 60
THRESHOLD_CHEAP = 90
THRESHOLD_NORMAL_LOW = 90
THRESHOLD_NORMAL_HIGH = 115
THRESHOLD_EXPENSIVE = 140
