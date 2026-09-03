"""Device identity and live scaling factors (informational registers)."""

from __future__ import annotations

from .addresses import (
    MFR_DATE,
    MFR_ID,
    MFR_LOCATION,
    MFR_MODEL,
    MFR_REVISION,
    MFR_SERIAL,
    SCALING_FACTOR,
)
from .data_model import XDRComponent, raw_register, string

# SCALING_FACTOR nibble encoding -> multiplier (0x0 = unsupported).
FACTOR_NIBBLES: dict[int, float] = {
    0x4: 0.001,
    0x5: 0.01,
    0x6: 0.1,
    0x7: 1.0,
    0x8: 10.0,
    0x9: 100.0,
}

_NO_MCU = 0xFF  # revision byte value meaning "no MCU"


class Identity(XDRComponent):
    """Manufacturer information strings of the power supply."""

    _mfr_id_1 = string(
        MFR_ID, 3, command="MFR_ID_B0B5", description="Manufacturer name, chars 1-6"
    )
    _mfr_id_2 = string(
        MFR_ID + 3,
        3,
        command="MFR_ID_B6B11",
        description="Manufacturer name, chars 7-12",
    )
    _model_1 = string(
        MFR_MODEL, 3, command="MFR_MODEL_B0B5", description="Model name, chars 1-6"
    )
    _model_2 = string(
        MFR_MODEL + 3,
        3,
        command="MFR_MODEL_B6B11",
        description="Model name, chars 7-12",
    )
    _revision_1 = raw_register(
        MFR_REVISION, command="MFR_REVISION", description="Firmware revision, MCUs 1-2"
    )
    _revision_2 = raw_register(
        MFR_REVISION + 1,
        command="MFR_REVISION",
        description="Firmware revision, MCUs 3-4",
    )
    _revision_3 = raw_register(
        MFR_REVISION + 2,
        command="MFR_REVISION",
        description="Firmware revision, MCUs 5-6",
    )
    _location = string(
        MFR_LOCATION, 2, command="MFR_LOCATION", description="Manufacturer place"
    )
    _date = string(
        MFR_DATE, 3, command="MFR_DATE", description="Manufacture date (YYMMDD)"
    )
    _serial_1 = string(
        MFR_SERIAL, 3, command="MFR_SERIAL_B0B5", description="Serial number, chars 1-6"
    )
    _serial_2 = string(
        MFR_SERIAL + 3,
        3,
        command="MFR_SERIAL_B6B11",
        description="Serial number, chars 7-12",
    )

    @property
    def manufacturer(self) -> str | None:
        """The manufacturer name, e.g. ``MEAN WELL``."""
        return _join_strings(self._mfr_id_1, self._mfr_id_2)

    @property
    def model_name(self) -> str | None:
        """The model name, e.g. ``XDR-480-24``."""
        return _join_strings(self._model_1, self._model_2)

    @property
    def firmware_version(self) -> str | None:
        """Firmware revisions of the MCUs, e.g. ``R25.4, R10.5``.

        Each byte of the three revision words is one MCU: values 0x00-0xFE
        map to Rn.m (0xFE -> R25.4), 0xFF means no MCU.
        """
        words = (self._revision_1, self._revision_2, self._revision_3)
        if any(word is None for word in words):
            return None
        revisions = [
            f"R{byte // 10}.{byte % 10}"
            for word in words
            if word is not None
            for byte in ((word >> 8) & 0xFF, word & 0xFF)
            if byte != _NO_MCU
        ]
        return ", ".join(revisions) if revisions else None

    @property
    def location(self) -> str | None:
        """The manufacturer place."""
        return _clean(self._location)

    @property
    def manufacture_date(self) -> str | None:
        """The manufacture date as YYMMDD, e.g. ``251201``."""
        return _clean(self._date)

    @property
    def serial_number(self) -> str | None:
        """The serial number (manufacture date + sequence), e.g. ``251201000001``."""
        return _join_strings(self._serial_1, self._serial_2)


def _clean(value: str | None) -> str | None:
    """Strip padding from a device string; None stays None."""
    if value is None:
        return None
    cleaned = value.strip(" \x00")
    return cleaned or None


def _join_strings(*parts: str | None) -> str | None:
    """Join device string parts and strip padding; None if nothing was read."""
    if any(part is None for part in parts):
        return None
    return _clean("".join(part for part in parts if part is not None))


class ScalingFactors(XDRComponent):
    """Live scaling-factor report (SCALING_FACTOR, 0x00C0-0x00C2).

    The device reports which multiplier each measurement command uses; the
    factory defaults are VOUT/IOUT 0.01, VIN/temperature 0.1. The measurement
    fields themselves use these defaults — this component lets a caller
    verify them against the live report.

    The block is byte-oriented, one factor per byte: register 0x00C0 holds
    VOUT (bits 0-3) and IOUT (bits 4-7) in its low byte and VIN in its high
    byte; register 0x00C1 holds TEMPERATURE_1 in its low byte. A factor
    nibble of 0x0 means the relevant command is unsupported (the property
    then reads None).
    """

    _vout_iout_vin = raw_register(
        SCALING_FACTOR,
        command="SCALING_FACTOR",
        description="VOUT/IOUT (low byte) and VIN (high byte) scaling nibbles",
    )
    _temperature = raw_register(
        SCALING_FACTOR + 1,
        command="SCALING_FACTOR",
        description="TEMPERATURE_1 scaling nibble (low byte)",
    )

    @staticmethod
    def _factor(word: int | None, shift: int) -> float | None:
        """Decode one factor nibble; None if unsupported or not yet read."""
        if word is None:
            return None
        return FACTOR_NIBBLES.get((word >> shift) & 0xF)

    @property
    def output_voltage_factor(self) -> float | None:
        """Multiplier of READ_VOUT / VOUT_SET (factory default 0.01)."""
        return self._factor(self._vout_iout_vin, 0)

    @property
    def output_current_factor(self) -> float | None:
        """Multiplier of READ_IOUT / IOUT_SET (factory default 0.01)."""
        return self._factor(self._vout_iout_vin, 4)

    @property
    def input_voltage_factor(self) -> float | None:
        """Multiplier of READ_VIN (factory default 0.1)."""
        return self._factor(self._vout_iout_vin, 8)

    @property
    def temperature_factor(self) -> float | None:
        """Multiplier of READ_TEMPERATURE_1 (factory default 0.1)."""
        return self._factor(self._temperature, 0)
