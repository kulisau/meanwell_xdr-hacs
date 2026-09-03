"""Constants for the Mean Well XDR integration."""

from datetime import timedelta
from typing import Final

DOMAIN: Final = "meanwell_xdr"

CONF_UNIT_ID: Final = "unit_id"

DEFAULT_PORT: Final = 502
DEFAULT_UNIT_ID: Final = 131  # 0x83, the XDR factory-default slave address
PORT_MIN: Final = 1
PORT_MAX: Final = 65535
UNIT_ID_MIN: Final = 0x80
UNIT_ID_MAX: Final = 0xBF

# A power supply changes fast, but the device only answers one request at a
# time, so we poll conservatively and fixed.
SCAN_INTERVAL: Final = timedelta(seconds=10)
