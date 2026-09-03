"""Output measurements — the input-register block (FC 0x04)."""

from __future__ import annotations

from ..addresses import (
    INPUT_RANGES,
    READ_IOUT,
    READ_POUT,
    READ_TEMPERATURE_1,
    READ_VIN,
    READ_VOUT,
)
from ..data_model import XDRComponent, gauge


class Measurements(XDRComponent):
    """Live output measurements of the power supply.

    All fields use the factory-default scaling factors documented for the
    series (VIN 0.1, VOUT/IOUT 0.01, temperature 0.1, power 1.0); the device
    reports the active factors in ``ScalingFactors`` for verification.
    """

    register_space = "input"
    register_ranges = INPUT_RANGES

    input_voltage = gauge(
        READ_VIN,
        0.1,
        unit="V",
        digits=1,
        command="READ_VIN",
        description="AC input voltage",
    )
    """AC input voltage."""

    output_voltage = gauge(
        READ_VOUT, 0.01, unit="V", command="READ_VOUT", description="Output voltage"
    )
    """Output voltage."""

    output_current = gauge(
        READ_IOUT, 0.01, unit="A", command="READ_IOUT", description="Output current"
    )
    """Output current."""

    internal_temperature = gauge(
        READ_TEMPERATURE_1,
        0.1,
        unit="°C",
        digits=1,
        command="READ_TEMPERATURE_1",
        description="Internal ambient temperature",
    )
    """Internal ambient temperature."""

    output_power = gauge(
        READ_POUT,
        1,
        unit="W",
        digits=0,
        command="READ_POUT",
        description="Output power",
    )
    """Output power."""
