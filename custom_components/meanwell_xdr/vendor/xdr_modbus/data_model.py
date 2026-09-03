"""Field factories and the component base class for XDR devices.

The factories wrap the ``modbus_connection.model`` field types, attach neutral
:class:`~xdr_modbus.metadata.DatapointMetadata` to every field, and turn
``min_value``/``max_value`` into write validators so out-of-range writes are
rejected before they reach the wire.
"""

from __future__ import annotations

from enum import IntEnum, IntFlag
from typing import Any

from modbus_connection.model import (
    Component,
    bit as _modbus_bit,
    bits as _modbus_bits,
    boolean as _modbus_boolean,
    enum as _modbus_enum,
    flags as _modbus_flags,
    gauge as _modbus_gauge,
    integer as _modbus_integer,
    raw_register as _modbus_raw_register,
    string as _modbus_string,
    uint32 as _modbus_uint32,
)
from modbus_connection.model.fields import (
    NumberField,
    RawField,
    StringField,
)

from .addresses import COMMAND_KEY, HOLDING_RANGES
from .exceptions import XdrValueValidationError
from .metadata import (
    DatapointMetadata,
    EnumMetadata,
    FlagMetadata,
    NumberMetadata,
    attach_metadata,
    step_from_digits,
)

__all__ = [
    "XDRComponent",
    "bit",
    "bits",
    "boolean",
    "command_field",
    "enum",
    "flags",
    "gauge",
    "integer",
    "raw_register",
    "string",
    "uint32",
    "validate_range",
]


class XDRComponent(Component):
    """Base class for every XDR sub-system.

    ``register_ranges`` constrains block planning to the addresses the device
    actually answers, so a pooled read never crosses an undocumented gap.
    """

    register_ranges = HOLDING_RANGES
    # Ranges are declared; merging across gaps inside a range is still allowed.
    max_gap = 16


def validate_range(command: str, value: float, limits: tuple[float, float]) -> None:
    """Raise ``XdrValueValidationError`` if ``value`` is outside ``limits``.

    The bounds are inclusive within half a step of tolerance, so a value that
    lands exactly on the boundary after float scaling is accepted.
    """
    low, high = limits
    if not low - 1e-9 <= value <= high + 1e-9:
        raise XdrValueValidationError(f"{command} accepts {low}..{high}, got {value}")


def _number_validator(
    command: str, min_value: float | None, max_value: float | None, digits: int
) -> Any:
    """A write validator enforcing a user-space range, or True if unbounded."""
    if min_value is None and max_value is None:
        return True
    tolerance = step_from_digits(digits) / 2

    def validate(value: Any) -> Any:
        number = float(value)
        low = number if min_value is None else min_value
        high = number if max_value is None else max_value
        if not low - tolerance <= number <= high + tolerance:
            msg = f"{command} accepts {low}..{high}, got {number}"
            raise XdrValueValidationError(msg)
        return value

    return validate


def _number_metadata(
    scale: float,
    unit: str | None,
    min_value: float | None,
    max_value: float | None,
    digits: int,
) -> NumberMetadata:
    def raw(value: float | None) -> int | None:
        return None if value is None else round(value / scale)

    return NumberMetadata(
        min=min_value,
        max=max_value,
        step=step_from_digits(digits),
        digits=digits,
        unit=unit,
        raw_min=raw(min_value),
        raw_max=raw(max_value),
    )


def gauge(
    address: int,
    scale: float,
    *,
    unit: str | None = None,
    writable: bool = False,
    min_value: float | None = None,
    max_value: float | None = None,
    digits: int = 2,
    command: str = "",
    description: str = "",
) -> NumberField[float]:
    """A scaled numeric register field (factory default scaling factors)."""
    field = _modbus_gauge(
        address,
        scale,
        signed=False,
        unit=unit,
        writable=_number_validator(command, min_value, max_value, digits)
        if writable
        else False,
    )
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="number",
            command=command,
            description=description,
            writable=writable,
            number=_number_metadata(scale, unit, min_value, max_value, digits),
        ),
    )


def integer(
    address: int,
    *,
    writable: bool = False,
    unit: str | None = None,
    command: str = "",
    description: str = "",
) -> NumberField[int]:
    """An unsigned 16-bit counter/register field."""
    field = _modbus_integer(address, signed=False, unit=unit, writable=writable)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="number",
            command=command,
            description=description,
            writable=writable,
            number=_number_metadata(1, unit, None, None, 0),
        ),
    )


def uint32(
    address: int,
    *,
    unit: str | None = None,
    command: str = "",
    description: str = "",
) -> NumberField[int]:
    """An unsigned 32-bit value over two consecutive registers."""
    field = _modbus_uint32(address, unit=unit)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="number",
            command=command,
            description=description,
            writable=False,
            number=_number_metadata(1, unit, None, None, 0),
        ),
    )


def raw_register(
    address: int,
    *,
    writable: bool = False,
    command: str = "",
    description: str = "",
) -> RawField:
    """A raw register word (no scaling or sign handling)."""
    field = _modbus_raw_register(address, writable=writable)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="number",
            command=command,
            description=description,
            writable=writable,
        ),
    )


def command_field(
    address: int,
    *,
    command: str,
    description: str,
) -> RawField:
    """A command register that only accepts the 0xAA command key."""

    def validate(value: Any) -> int:
        if int(value) != COMMAND_KEY:
            msg = f"{command} only accepts writing 0x{COMMAND_KEY:02X}, got {value}"
            raise XdrValueValidationError(msg)
        return COMMAND_KEY

    field = _modbus_raw_register(address, writable=validate)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="number",
            command=command,
            description=description,
            writable=True,
        ),
    )


def boolean(
    address: int,
    *,
    writable: bool = False,
    command: str = "",
    description: str = "",
) -> NumberField[bool]:
    """A 16-bit 0/1 register (e.g. OPERATION)."""
    field = _modbus_boolean(address, writable=writable)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="boolean",
            command=command,
            description=description,
            writable=writable,
        ),
    )


def enum[E: IntEnum](
    address: int,
    enum_type: type[E],
    *,
    writable: bool = False,
    command: str = "",
    description: str = "",
) -> NumberField[E]:
    """A register field mapped to an IntEnum."""
    field = _modbus_enum(address, enum_type, writable=writable)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="enum",
            command=command,
            description=description,
            writable=writable,
            enum=EnumMetadata(
                options=tuple((member.name, int(member)) for member in enum_type)
            ),
        ),
    )


def flags[F: IntFlag](
    address: int,
    flag_type: type[F],
    *,
    command: str = "",
    description: str = "",
) -> NumberField[F]:
    """A read-only register field mapped to an IntFlag bit field."""
    field = _modbus_flags(address, flag_type)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="flags",
            command=command,
            description=description,
            writable=False,
            flags=FlagMetadata(
                members=tuple((member.name, int(member)) for member in flag_type)
            ),
        ),
    )


def bit(
    address: int,
    index: int,
    *,
    writable: bool = False,
    command: str = "",
    description: str = "",
) -> Any:
    """One writable bit of a configuration register (read-modify-write)."""
    field = _modbus_bit(address, index, writable=writable)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="boolean",
            command=command,
            description=description,
            writable=writable,
        ),
    )


def bits(
    address: int,
    start: int,
    width: int,
    *,
    writable: bool = False,
    command: str = "",
    description: str = "",
) -> Any:
    """A run of writable bits of a configuration register (read-modify-write)."""
    field = _modbus_bits(address, start, width, writable=writable)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="number",
            command=command,
            description=description,
            writable=writable,
        ),
    )


def string(
    address: int,
    length: int,
    *,
    command: str = "",
    description: str = "",
) -> StringField:
    """A fixed-length null-padded ASCII string over ``length`` registers."""
    field = _modbus_string(address, length)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="string",
            command=command,
            description=description,
            writable=False,
        ),
    )
