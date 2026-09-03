"""Constants for the Mean Well XDR integration."""

from typing import Final

DOMAIN: Final = "meanwell_xdr"

COMMAND_KEY: Final = 0xAA  # the only value command registers accept

CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_UNIT_ID: Final = "unit_id"

DEFAULT_PORT: Final = 502
DEFAULT_SCAN_INTERVAL: Final = 10  # seconds
DEFAULT_UNIT_ID: Final = 131  # 0x83, the XDR factory-default slave address
PORT_MIN: Final = 1
PORT_MAX: Final = 65535
# A power supply changes fast, but the device only answers one request at a
# time, so keep the floor conservative; several supplies on one link share it.
SCAN_INTERVAL_MIN: Final = 5  # seconds
SCAN_INTERVAL_MAX: Final = 3600  # seconds
UNIT_ID_MIN: Final = 0x80
UNIT_ID_MAX: Final = 0xBF
