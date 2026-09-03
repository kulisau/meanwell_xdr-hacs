"""Model definitions of the Mean Well XDR series.

The series spans the XDR-75/120/240/480/960 families in 12/24/36/48 V output
variants. Modbus communication is only available on the XDR-240/480/960
families; the smaller models are included so a device that reports such a
model string still gets a usable definition (``has_modbus`` is False).
"""

from __future__ import annotations

from dataclasses import dataclass

from .enums import OutputVoltage
from .exceptions import XdrModelError

# Factory output-voltage adjustment ranges (VOUT_SET limits) per output voltage.
VOUT_SET_LIMITS: dict[OutputVoltage, tuple[float, float]] = {
    OutputVoltage.VOLT_12: (12.0, 15.0),
    OutputVoltage.VOLT_24: (24.0, 29.0),
    OutputVoltage.VOLT_36: (36.0, 42.0),
    OutputVoltage.VOLT_48: (48.0, 55.0),
}

# (rated current in A, rated power in W) per family and output voltage.
# None = the variant does not exist (XDR-960 has no 12 V model).
_RATED: dict[int, dict[OutputVoltage, tuple[float, float] | None]] = {
    75: {
        OutputVoltage.VOLT_12: (6.24, 74.88),
        OutputVoltage.VOLT_24: (3.12, 74.88),
        OutputVoltage.VOLT_36: (2.08, 74.88),
        OutputVoltage.VOLT_48: (1.56, 74.88),
    },
    120: {
        OutputVoltage.VOLT_12: (10.0, 120.0),
        OutputVoltage.VOLT_24: (5.0, 120.0),
        OutputVoltage.VOLT_36: (3.33, 119.88),
        OutputVoltage.VOLT_48: (2.5, 120.0),
    },
    240: {
        OutputVoltage.VOLT_12: (20.0, 240.0),
        OutputVoltage.VOLT_24: (10.0, 240.0),
        OutputVoltage.VOLT_36: (6.66, 240.0),
        OutputVoltage.VOLT_48: (5.0, 240.0),
    },
    # The XDR-480-12 is a 360 W / 30 A variant, not 480 W.
    480: {
        OutputVoltage.VOLT_12: (30.0, 360.0),
        OutputVoltage.VOLT_24: (20.0, 480.0),
        OutputVoltage.VOLT_36: (13.3, 480.0),
        OutputVoltage.VOLT_48: (10.0, 480.0),
    },
    960: {
        OutputVoltage.VOLT_12: None,
        OutputVoltage.VOLT_24: (40.0, 960.0),
        OutputVoltage.VOLT_36: (26.6, 957.6),
        OutputVoltage.VOLT_48: (20.0, 960.0),
    },
}

# Families with Modbus communication (per the manual's feature list).
_MODBUS_FAMILIES = frozenset((240, 480, 960))

# IOUT_SET is adjustable to 20-125 % of the rated current.
_IOUT_SET_FRACTION = (0.20, 1.25)


@dataclass(frozen=True)
class ModelDefinition:
    """Static capabilities of one XDR variant, e.g. ``XDR-480-24``."""

    family: int  # 75, 120, 240, 480 or 960
    output_voltage: OutputVoltage
    rated_current: float  # A
    rated_power: float  # W
    has_modbus: bool

    @property
    def name(self) -> str:
        """The canonical model name, e.g. ``XDR-480-24``."""
        return f"XDR-{self.family}-{self.output_voltage.value}"

    @property
    def vout_set_range(self) -> tuple[float, float]:
        """Valid VOUT_SET range in volts."""
        return VOUT_SET_LIMITS[self.output_voltage]

    @property
    def iout_set_range(self) -> tuple[float, float]:
        """Valid IOUT_SET range in amps (20-125 % of rated current)."""
        low, high = _IOUT_SET_FRACTION
        return (round(self.rated_current * low, 2), round(self.rated_current * high, 2))

    @property
    def peak_current(self) -> float:
        """Transient peak current (200 % of rated, 5 s)."""
        return round(self.rated_current * 2, 2)

    @property
    def peak_power(self) -> float:
        """Peak power during the 5 s transient (200 % of rated)."""
        return round(self.rated_power * 2, 2)


def models() -> dict[str, ModelDefinition]:
    """Every XDR variant keyed by its canonical model name."""
    return {
        definition.name: definition
        for family, variants in _RATED.items()
        for output_voltage, rated in variants.items()
        if rated is not None
        for definition in (
            ModelDefinition(
                family=family,
                output_voltage=output_voltage,
                rated_current=rated[0],
                rated_power=rated[1],
                has_modbus=family in _MODBUS_FAMILIES,
            ),
        )
    }


def parse_model(model_string: str) -> ModelDefinition:
    """Map a device-reported model string (e.g. ``"XDR-480-24"``) to a definition.

    Raises ``XdrModelError`` for strings that are not a known XDR variant.
    """
    normalized = model_string.strip().upper()
    for separator in ("-", "_", " "):
        normalized = normalized.replace(separator, "")
    # "XDR48024" -> family 480, output voltage "24".
    if not normalized.startswith("XDR"):
        raise XdrModelError(f"Not an XDR model string: {model_string!r}")
    rest = normalized.removeprefix("XDR")
    catalog = models()
    for family in sorted(_RATED, reverse=True):
        if rest.startswith(str(family)):
            candidate = f"XDR-{family}-{rest.removeprefix(str(family))}"
            if candidate in catalog:
                return catalog[candidate]
    raise XdrModelError(f"Unknown XDR model: {model_string!r}")
