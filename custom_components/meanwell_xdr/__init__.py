"""The Mean Well XDR integration.

XDR is a Modbus device. This integration does not own its connection: it
borrows a ``ModbusUnit`` from a ``modbus_connection`` config entry (chosen in
the config flow) and hands it to the ``xdr_modbus`` library. The
``modbus_connection`` entry owns the connection lifecycle; this integration
reloads when the connection drops so it re-borrows on the rebuilt connection.
"""

from . import vendor  # noqa: F401  # adds vendor/ to sys.path before xdr_modbus

from xdr_modbus import XDRPowerSupply

from homeassistant.components.modbus_connection import async_get_unit
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_CONNECTION, CONF_UNIT_ID
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

    ``async_get_unit`` raises ``ConnectionNotReady`` (a ``ConfigEntryNotReady``)
    if the shared connection is missing or not loaded; letting it propagate
    gives Home Assistant's setup retry.
    """
    unit = async_get_unit(
        hass, entry.data[CONF_CONNECTION], int(entry.data[CONF_UNIT_ID])
    )
    device = XDRPowerSupply(unit)
    coordinator = XDRCoordinator(hass, entry, device)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    # The borrowed unit is bound to modbus_connection's current connection. When
    # that connection drops, modbus_connection rebuilds it; reload so we re-borrow
    # a unit on the fresh connection instead of holding a dead one.
    entry.async_on_unload(
        unit.on_connection_lost(
            lambda: hass.config_entries.async_schedule_reload(entry.entry_id)
        )
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: XDRConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
