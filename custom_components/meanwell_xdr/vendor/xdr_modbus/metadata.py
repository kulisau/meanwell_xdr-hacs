"""Neutral datapoint metadata attached to every field.

The metadata describes a field without any framework or automation-platform
types: how it is scaled, what unit it carries, and — for writable values —
the valid range. UI layers can translate it 1:1 into their own controls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


def step_from_digits(digits: int) -> float:
    """The step implied by a decimal precision (0 -> 1, else 10^-digits)."""
    return 1 if digits <= 0 else 10**-digits


@dataclass(frozen=True)
class NumberMetadata:
    """Scaling and range of a numeric datapoint (user-space values)."""

    min: float | None
    max: float | None
    step: float
    digits: int
    unit: str | None
    raw_min: int | None = None  # register-space counterpart of ``min``
    raw_max: int | None = None  # register-space counterpart of ``max``


@dataclass(frozen=True)
class EnumMetadata:
    """An enumerated datapoint; members are ``(name, register value)`` pairs."""

    options: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class FlagMetadata:
    """A bit-field datapoint; members are ``(name, bit mask)`` pairs."""

    members: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class DatapointMetadata:
    """Everything a generic UI needs to render one datapoint."""

    value_kind: Literal["number", "enum", "boolean", "flags", "string"]
    command: str  # the manufacturer's command name, e.g. "VOUT_SET"
    description: str
    writable: bool
    number: NumberMetadata | None = None
    enum: EnumMetadata | None = None
    flags: FlagMetadata | None = None


def attach_metadata(field: object, metadata: DatapointMetadata) -> object:
    """Attach metadata to a framework field (it has no own metadata slot)."""
    field.xdr_metadata = metadata
    return field


def metadata_for(field: object) -> DatapointMetadata | None:
    """The metadata attached to a field, or None."""
    return getattr(field, "xdr_metadata", None)


def require_metadata_for(field: object) -> DatapointMetadata:
    """The metadata attached to a field, raising if there is none."""
    metadata = metadata_for(field)
    if metadata is None:
        msg = f"Field {field!r} has no XDR metadata attached"
        raise ValueError(msg)
    return metadata
