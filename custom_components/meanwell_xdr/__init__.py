"""The Mean Well XDR integration.

XDR is a Modbus device. This integration does not own its connection: the
``modbus`` integration hands out a ``ModbusUnit`` on a connection shared with
every other consumer of the same link, and reopens the link after a drop, so
setup never fails just because a device is powered down.
"""

from . import vendor  # noqa: F401  # adds vendor/ to sys.path before xdr_modbus

from xdr_modbus import XDRPowerSupply

from homeassistant.components.modbus import async_get_unit
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from modbus_connection import ModbusTcpParams

from .const import CONF_UNIT_ID
from .coordinator import XDRConfigEntry, XDRCoordinator

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: XDRConfigEntry) -> bool:
    """Set up Mean Well XDR from a config entry.

    Asking for a unit performs no I/O, so a powered-down supply does not stop
    setup; the first read opens the link, and a dropped link reopens on the
    next request.
    """
    unit = async_get_unit(
        hass,
        entry,
        ModbusTcpParams(host=entry.data[CONF_HOST], port=entry.data[CONF_PORT]),
        int(entry.data[CONF_UNIT_ID]),
    )
    device = XDRPowerSupply(unit)
    coordinator = XDRCoordinator(hass, entry, device)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: XDRConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
