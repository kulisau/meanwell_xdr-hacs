"""Output control — on/off switch and voltage/current setpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..addresses import IOUT_SET, OPERATION, VOUT_SET
from ..data_model import XDRComponent, boolean, gauge, validate_range

if TYPE_CHECKING:
    from ..models import ModelDefinition


class Control(XDRComponent):
    """Control of the DC output.

    Note the device only honours these registers when SYSTEM_CONFIG.MOD_CTRL
    is set (and an AC power cycle has occurred); otherwise the potentiometer
    (SVR) defines voltage, current and on/off.
    """

    operation = boolean(
        OPERATION, writable=True, command="OPERATION", description="Output ON/OFF"
    )
    """Output on/off. Requires MOD_CTRL=1 to take effect."""

    voltage_setpoint = gauge(
        VOUT_SET,
        0.01,
        unit="V",
        writable=True,
        command="VOUT_SET",
        description="Output voltage setpoint",
    )
    """Output voltage setpoint in volts; range depends on the model."""

    current_setpoint = gauge(
        IOUT_SET,
        0.01,
        unit="A",
        writable=True,
        command="IOUT_SET",
        description="Output current limit setpoint",
    )
    """Output current limit setpoint in amps; 20-125 % of the rated current."""

    def __init__(
        self, unit: Any, model_definition: ModelDefinition | None = None
    ) -> None:
        """Initialize the component; ``model_definition`` enables range checks."""
        super().__init__(unit)
        self._model_definition = model_definition

    def set_model_definition(self, definition: ModelDefinition | None) -> None:
        """Update the model used for setpoint range validation."""
        self._model_definition = definition

    async def write(self, field: str, value: Any) -> None:
        """Write a field, rejecting setpoints outside the model's range."""
        if self._model_definition is not None:
            if field == "voltage_setpoint":
                validate_range(
                    "VOUT_SET", float(value), self._model_definition.vout_set_range
                )
            elif field == "current_setpoint":
                validate_range(
                    "IOUT_SET", float(value), self._model_definition.iout_set_range
                )
        await super().write(field, value)
