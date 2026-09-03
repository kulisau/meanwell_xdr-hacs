"""DataUpdateCoordinator that polls the XDR power supply."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from modbus_connection import ModbusError
from xdr_modbus import XDRPowerSupply

from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

type XDRConfigEntry = ConfigEntry[XDRCoordinator]


class XDRCoordinator(DataUpdateCoordinator[XDRPowerSupply]):
    """Refreshes every sub-system on a schedule.

    ``async_update`` fans out to each component (each reads only its own
    registers), so adding/removing entities never changes what is polled. The
    ``modbus`` integration owns the connection; this coordinator only reads.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry: XDRConfigEntry,
        device: XDRPowerSupply,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(
                seconds=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
        )
        self.device = device

    async def _async_update_data(self) -> XDRPowerSupply:
        try:
            await self.device.async_update()
        except ModbusError as err:
            raise UpdateFailed(
                f"Error communicating with XDR power supply: {err}"
            ) from err
        return self.device
