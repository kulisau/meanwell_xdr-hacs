"""Config flow for Mean Well XDR."""

from typing import Any

from . import vendor  # noqa: F401  # adds vendor/ to sys.path before xdr_modbus

from modbus_connection import ModbusError, ModbusTcpParams
from xdr_modbus import XDRPowerSupply, XDRProbe
import voluptuous as vol

from homeassistant.components.modbus import async_get_temporary_unit
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_UNIT_ID,
    DEFAULT_PORT,
    DEFAULT_UNIT_ID,
    DOMAIN,
    PORT_MAX,
    PORT_MIN,
    UNIT_ID_MAX,
    UNIT_ID_MIN,
)

STEP_USER = vol.Schema(
    {
        vol.Required(CONF_HOST): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
        vol.Required(CONF_PORT, default=DEFAULT_PORT): NumberSelector(
            NumberSelectorConfig(
                min=PORT_MIN, max=PORT_MAX, step=1, mode=NumberSelectorMode.BOX
            )
        ),
        vol.Required(CONF_UNIT_ID, default=DEFAULT_UNIT_ID): NumberSelector(
            NumberSelectorConfig(
                min=UNIT_ID_MIN, max=UNIT_ID_MAX, step=1, mode=NumberSelectorMode.BOX
            )
        ),
    }
)


class XDRConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mean Well XDR."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the link details, then read the model for the title."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if (probe := await self._async_probe(user_input)) is None:
                errors["base"] = "cannot_connect"
            else:
                host = user_input[CONF_HOST].strip().lower()
                port = int(user_input[CONF_PORT])
                unit_id = int(user_input[CONF_UNIT_ID])
                unique_id = probe.serial_number or f"{host}:{port}:{unit_id}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=probe.model_name or "Mean Well XDR",
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_UNIT_ID: unit_id,
                    },
                )
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(STEP_USER, user_input),
            errors=errors,
        )

    async def _async_probe(self, data: dict[str, Any]) -> XDRProbe | None:
        """Read the identity block, or None if the supply does not answer."""
        try:
            async with async_get_temporary_unit(
                self.hass,
                ModbusTcpParams(host=data[CONF_HOST], port=int(data[CONF_PORT])),
                int(data[CONF_UNIT_ID]),
            ) as unit:
                return await XDRPowerSupply.async_probe(unit)
        except (HomeAssistantError, ModbusError, OSError, ValueError):
            return None
