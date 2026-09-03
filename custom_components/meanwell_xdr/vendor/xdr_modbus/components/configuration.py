"""Configuration registers — thresholds, communication and command registers.

Writable packed-bit fields read the register back and merge, so changing one
setting never clobbers the other bits in the same register.
"""

from __future__ import annotations

from ..addresses import (
    AC_FAIL_LL_SET,
    AC_OK_LL_SET,
    CLEAR_LOG,
    DC_OK_SET,
    MODBUS_BAUD,
    MODBUS_FORMAT,
    MODBUS_ID,
    OL_ALARM_LEVEL,
    PEAK_SET,
    PROTECT_CONFIG,
    RESET_DEFAULT,
    SYSTEM_CONFIG,
    UNIT_ID_RANGE,
)
from ..data_model import XDRComponent, bit, bits, command_field, enum, gauge, integer
from ..enums import BaudRate, FrameFormat
from ..exceptions import XdrValueValidationError


class Configuration(XDRComponent):
    """Read/write configuration of the power supply."""

    ##### system configuration (SYSTEM_CONFIG, 0x00C4)

    modbus_control = bit(
        SYSTEM_CONFIG,
        0,
        writable=True,
        command="SYSTEM_CONFIG.MOD_CTRL",
        description=(
            "Control V/I/ON-OFF over Modbus (1) or SVR/potentiometer (0); "
            "effective after AC restore"
        ),
    )
    """Modbus vs. potentiometer control source."""

    power_on_behavior = bits(
        SYSTEM_CONFIG,
        1,
        2,
        writable=True,
        command="SYSTEM_CONFIG.OPERATION_INIT",
        description="Power-on behaviour: 0=OFF, 1=ON, 2=previous value",
    )
    """Power-on behaviour of the output (0=OFF, 1=ON, 2=previous)."""

    peak_enable = bit(
        SYSTEM_CONFIG,
        3,
        writable=True,
        command="SYSTEM_CONFIG.PEAK_EN",
        description=(
            "Enable peak power / transient peak current "
            "(requires TC pin shorted to GND)"
        ),
    )
    """Peak power function enable."""

    eeprom_mode = bits(
        SYSTEM_CONFIG,
        8,
        2,
        writable=True,
        command="SYSTEM_CONFIG.EEP_CONFIG",
        description="EEPROM storage: 0=immediate, 1=1 min delay, 2=10 min delay",
    )
    """EEPROM storage mode for setpoint writes (0/1/2)."""

    eeprom_off = bit(
        SYSTEM_CONFIG,
        10,
        writable=True,
        command="SYSTEM_CONFIG.EEP_OFF",
        description="Disable saving to EEPROM (protects limited write cycles)",
    )
    """EEPROM save on/off."""

    ##### protection configuration (PROTECT_CONFIG, 0x00C5)

    overload_protection = bits(
        PROTECT_CONFIG,
        0,
        2,
        writable=True,
        command="PROTECT_CONFIG.OLP_TYPE",
        description=(
            "Overload behaviour: 1=constant current, 2=immediate shutdown (latch-off)"
        ),
    )
    """Overload protection behaviour (1=constant current, 2=latch-off)."""

    back_emf_protection = bit(
        PROTECT_CONFIG,
        8,
        writable=True,
        command="PROTECT_CONFIG.EMFP_EN",
        description="Enable back-EMF protection",
    )
    """Back-EMF protection enable."""

    ##### protection thresholds

    ac_fail_threshold = gauge(
        AC_FAIL_LL_SET,
        0.1,
        unit="V",
        writable=True,
        min_value=74.0,
        max_value=264.0,
        digits=1,
        command="AC_Fail_LL_SET",
        description="AC low-line failover threshold",
    )
    """AC low-line failover threshold in volts."""

    ac_recover_threshold = gauge(
        AC_OK_LL_SET,
        0.1,
        unit="V",
        writable=True,
        min_value=79.0,
        max_value=269.0,
        digits=1,
        command="AC_OK_LL_SET",
        description="AC low-line recovery threshold",
    )
    """AC low-line recovery threshold in volts."""

    dc_ok_threshold = gauge(
        DC_OK_SET,
        0.01,
        unit="%",
        writable=True,
        min_value=70.0,
        max_value=95.0,
        command="DC_OK_SET",
        description="DC OK threshold in % of output voltage",
    )
    """DC OK threshold, percent of output voltage."""

    peak_current_limit = gauge(
        PEAK_SET,
        0.01,
        unit="%",
        writable=True,
        min_value=125.0,
        max_value=600.0,
        digits=0,
        command="PEAK_SET",
        description="Peak output current limit in % of rated current",
    )
    """Peak output current limit, percent of rated current."""

    overload_alarm_level = gauge(
        OL_ALARM_LEVEL,
        0.01,
        unit="%",
        writable=True,
        min_value=70.0,
        max_value=95.0,
        command="OL_ALARM_LEVEL",
        description="Overload pre-alarm threshold in %",
    )
    """Overload pre-alarm threshold, percent."""

    ##### communication settings

    modbus_id = integer(
        MODBUS_ID,
        writable=True,
        command="MODBUS_ID",
        description="Modbus slave address (0x80-0xBF); requires AC restart",
    )
    """Modbus slave address."""

    baud_rate = enum(
        MODBUS_BAUD,
        BaudRate,
        writable=True,
        command="MODBUS_BAUD",
        description="Modbus baud rate",
    )
    """Modbus baud rate."""

    frame_format = enum(
        MODBUS_FORMAT,
        FrameFormat,
        writable=True,
        command="MODBUS_FORMAT",
        description="Modbus frame format (parity/stop bits)",
    )
    """Modbus frame format."""

    ##### command registers

    reset_defaults = command_field(
        RESET_DEFAULT,
        command="RESET_DEFAULT",
        description="Write 0xAA to restore factory settings; the unit restarts",
    )
    """Factory reset command (write 0xAA)."""

    clear_event_log = command_field(
        CLEAR_LOG,
        command="CLEAR_LOG",
        description="Write 0xAA to clear the fault event log; restart required",
    )
    """Clear the fault event log (write 0xAA)."""

    async def write(self, field: str, value: object) -> None:
        """Write a field; the slave address is range-checked here."""
        if field == "modbus_id":
            low, high = UNIT_ID_RANGE
            if not low <= int(value) <= high:  # type: ignore[arg-type]
                msg = (
                    f"MODBUS_ID accepts {low}..{high} "
                    f"(0x{low:02X}-0x{high:02X}), got {value}"
                )
                raise XdrValueValidationError(msg)
        await super().write(field, value)
