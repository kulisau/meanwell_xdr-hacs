"""Smoke tests for the vendored xdr_modbus device library.

These tests import the library exactly the way the integration does (through
the ``vendor`` sys-path shim) and drive it with the in-memory mock backend —
no Home Assistant imports, so they run with plain pytest.
"""

import asyncio
import sys
from pathlib import Path

import pytest

VENDOR = Path(__file__).parent.parent / "custom_components" / "meanwell_xdr" / "vendor"
if str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

from modbus_connection.mock import MockModbusConnection, MockModbusUnit  # noqa: E402

from xdr_modbus import XDRPowerSupply, XdrValueValidationError  # noqa: E402


def _ascii_words(text: str, start: int) -> dict[int, int]:
    padded = text.ljust(6)[:6]
    return {
        start + offset: (ord(padded[2 * offset]) << 8) | ord(padded[2 * offset + 1])
        for offset in range(3)
    }


@pytest.fixture
def unit() -> MockModbusUnit:
    """A seeded mock unit-131 XDR-480-24."""
    connection = MockModbusConnection()
    unit = connection.for_unit(131)
    unit.input.update({80: 2301, 96: 2400, 97: 500, 98: 355, 99: 120})
    unit.holding.update(
        {
            0: 1,
            32: 2400,
            48: 2000,
            64: 0x0006,
            65: 0x0101,
            195: 0x0122,
            **_ascii_words("MEANWE", 128),
            **_ascii_words("LL", 131),
            **_ascii_words("XDR-48", 134),
            **_ascii_words("0-24", 137),
            140: 0xFE69,
            141: 0xFFFF,
            142: 0xFFFF,
            **_ascii_words("251201", 148),
            **_ascii_words("000001", 151),
            2305: 5,
        }
    )
    return unit


def test_vendored_library_reads_and_writes(unit: MockModbusUnit) -> None:
    """The vendored copy updates, detects the model and writes setpoints."""

    async def run() -> None:
        device = XDRPowerSupply(unit)
        await device.async_update()
        assert device.info.model_name == "XDR-480-24"
        assert device.measurements.output_voltage == 24.0
        await device.async_set_voltage(26.5)
        assert unit.holding[32] == 2650

    asyncio.run(run())


def test_vendored_library_validates_against_model(unit: MockModbusUnit) -> None:
    """The vendored copy enforces the model's setpoint ranges."""

    async def run() -> None:
        device = XDRPowerSupply(unit)
        await device.async_update()
        with pytest.raises(XdrValueValidationError):
            await device.async_set_voltage(45.0)

    asyncio.run(run())
