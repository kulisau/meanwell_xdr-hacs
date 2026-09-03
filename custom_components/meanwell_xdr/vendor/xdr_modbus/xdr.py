"""The XDR power-supply device: composed sub-systems over one Modbus unit.

Construct ``XDRPowerSupply(unit)`` with a ``modbus_connection.ModbusUnit``,
call ``await device.async_update()``, then read its sub-systems as normal
Python objects::

    device.measurements.output_voltage
    device.status.fault_status_1
    device.statistics.latest_event
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from modbus_connection.model import ComponentGroup

from .components.configuration import Configuration
from .components.control import Control
from .components.measurements import Measurements
from .components.statistics import Statistics
from .components.status import Status
from .device_info import Identity, ScalingFactors
from .exceptions import XdrModelError
from .models import ModelDefinition, parse_model

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

__all__ = [
    "Configuration",
    "Control",
    "Identity",
    "Measurements",
    "ScalingFactors",
    "Statistics",
    "Status",
    "XDRPowerSupply",
    "XDRProbe",
]


@dataclass(frozen=True)
class XDRProbe:
    """What a safe setup probe learns about a device."""

    model_name: str | None
    serial_number: str | None
    firmware_version: str | None
    model_definition: ModelDefinition | None


class XDRPowerSupply:
    """A Mean Well XDR series power supply.

    The library never owns the transport: the caller injects a
    ``modbus_connection.ModbusUnit`` built from whichever backend they choose.
    """

    def __init__(
        self,
        unit: ModbusUnit,
        *,
        model: str | ModelDefinition | None = None,
    ) -> None:
        """Compose the sub-systems; ``model`` overrides detection from identity."""
        self.info = Identity(unit)
        self.scaling = ScalingFactors(unit)
        self.measurements = Measurements(unit)
        self.control = Control(unit)
        self.status = Status(unit)
        self.configuration = Configuration(unit)
        self.statistics = Statistics(unit)
        self._group = ComponentGroup(unit, self.components)
        if isinstance(model, ModelDefinition):
            self._model_override: ModelDefinition | None = model
        elif model is not None:
            self._model_override = parse_model(model)
        else:
            self._model_override = None
        self._refresh_model_definition()

    @property
    def components(self) -> tuple[Any, ...]:
        """Every sub-system, in pooled-read order."""
        return (
            self.info,
            self.scaling,
            self.measurements,
            self.control,
            self.status,
            self.configuration,
            self.statistics,
        )

    @property
    def model_definition(self) -> ModelDefinition | None:
        """Static capabilities of this unit, or None if the model is unknown."""
        if self._model_override is not None:
            return self._model_override
        model_name = self.info.model_name
        if not model_name:
            return None
        try:
            return parse_model(model_name)
        except XdrModelError:
            return None

    def _refresh_model_definition(self) -> None:
        """Push the detected model into the components that range-check writes."""
        self.control.set_model_definition(self.model_definition)

    @classmethod
    async def async_probe(cls, unit: ModbusUnit) -> XDRProbe:
        """Read the identity block only — a safe check that a device answers.

        No model knowledge is assumed, so probing an empty bus address fails
        with the connection error rather than a modelling error.
        """
        info = Identity(unit)
        await info.async_update()
        model_definition: ModelDefinition | None = None
        if info.model_name:
            try:
                model_definition = parse_model(info.model_name)
            except XdrModelError:
                model_definition = None
        return XDRProbe(
            model_name=info.model_name,
            serial_number=info.serial_number,
            firmware_version=info.firmware_version,
            model_definition=model_definition,
        )

    async def async_update(self) -> None:
        """Refresh every sub-system in pooled block reads."""
        await self._group.async_update()
        self._refresh_model_definition()

    async def async_update_info(self) -> None:
        """Refresh the identity and scaling-factor blocks only."""
        await self.info.async_update()
        await self.scaling.async_update()
        self._refresh_model_definition()

    async def async_update_measurements(self) -> None:
        """Refresh the measurement block only."""
        await self.measurements.async_update()

    async def async_update_control(self) -> None:
        """Refresh the output-control block only."""
        await self.control.async_update()

    async def async_update_status(self) -> None:
        """Refresh the status block only."""
        await self.status.async_update()

    async def async_update_configuration(self) -> None:
        """Refresh the configuration block only."""
        await self.configuration.async_update()

    async def async_update_statistics(self) -> None:
        """Refresh the statistics block only."""
        await self.statistics.async_update()

    async def async_set_output(self, on: bool) -> None:
        """Switch the DC output on or off (requires MOD_CTRL=1 to take effect)."""
        await self.control.write("operation", on)

    async def async_set_voltage(self, volts: float) -> None:
        """Set the output voltage setpoint; range-checked against the model."""
        await self.control.write("voltage_setpoint", volts)

    async def async_set_current(self, amps: float) -> None:
        """Set the output current limit; range-checked against the model."""
        await self.control.write("current_setpoint", amps)
