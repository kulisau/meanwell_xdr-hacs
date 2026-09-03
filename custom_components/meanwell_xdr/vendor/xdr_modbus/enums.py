"""Enumerations and bit fields of the Mean Well XDR series."""

from __future__ import annotations

from enum import IntEnum, IntFlag, StrEnum

__all__ = [
    "BaudRate",
    "EepConfig",
    "EventCode",
    "FaultStatus1",
    "FaultStatus2",
    "FrameFormat",
    "OlpType",
    "OperationInit",
    "OutputVoltage",
    "SystemConfig",
    "SystemStatus",
    "ProtectConfig",
]


class OutputVoltage(StrEnum):
    """Rated output voltage of an XDR variant."""

    VOLT_12 = "12"
    VOLT_24 = "24"
    VOLT_36 = "36"
    VOLT_48 = "48"


class EventCode(IntEnum):
    """Fault event codes of the event log (0x0921-0x0923)."""

    OUTPUT_OLP = 0x0001  # output overload protection
    OUTPUT_OVP = 0x0002  # output over-voltage protection
    OTP = 0x0003  # over-temperature protection
    COMM_ERROR = 0x0004  # communication error
    INPUT_AC_FAIL = 0x0005  # AC input abnormal
    OL_ALARM = 0x0006  # overload pre-alarm
    EEPROM_ERROR = 0x0007  # EEPROM data access error
    EMFP = 0x0009  # back-EMF protection


class BaudRate(IntEnum):
    """Modbus baud rate enumeration (MODBUS_BAUD, 0x0901)."""

    BPS_4800 = 0
    BPS_9600 = 1
    BPS_19200 = 2
    # The manual prints "37400" for this entry; 38400 is the plausible intent.
    BPS_38400 = 3
    BPS_57600 = 4
    BPS_115200 = 5


class FrameFormat(IntEnum):
    """Modbus frame format enumeration (MODBUS_FORMAT, 0x0902)."""

    NO_PARITY_2_STOP = 0
    NO_PARITY_1_STOP = 1
    ODD_PARITY_1_STOP = 2
    EVEN_PARITY_1_STOP = 3


class OperationInit(IntEnum):
    """Power-on behaviour of the OPERATION command (SYSTEM_CONFIG bits 1:2)."""

    OFF = 0b00  # pre-set OFF
    ON = 0b01  # pre-set ON (factory default)
    LAST = 0b10  # pre-set is the previous value


class OlpType(IntEnum):
    """Overload protection behaviour (PROTECT_CONFIG bits 0:1)."""

    CONSTANT_CURRENT = 0b01  # limiting with constant current (factory default)
    LATCH_OFF = 0b10  # immediate shutdown (latch-off)


class EepConfig(IntEnum):
    """EEPROM storage mode for setpoint writes (SYSTEM_CONFIG bits 8:9)."""

    IMMEDIATE = 0b00  # write to EEPROM immediately (factory default)
    DELAY_1_MIN = 0b01  # write if unchanged for 1 minute
    DELAY_10_MIN = 0b10  # write if unchanged for 10 minutes


class FaultStatus1(IntFlag):
    """Alarm bits of FAULT_STATUS_1 (0x0040)."""

    OTP = 1 << 1  # over-temperature protection (1 = protected)
    OVP = 1 << 2  # output over-voltage protection (1 = protected)
    OLP = 1 << 3  # output overload protection (1 = protected)
    AC_FAIL = 1 << 5  # AC input abnormal
    OP_OFF = 1 << 6  # DC output off (1 = DC off, 0 = DC on)
    HI_TEMP = 1 << 7  # internal high-temperature pre-alarm


class FaultStatus2(IntFlag):
    """Alarm bits of FAULT_STATUS_2 (0x0041)."""

    EMFP = 1 << 0  # back-EMF protection triggered
    OL_ALM = 1 << 8  # overload pre-alarm triggered


class SystemStatus(IntFlag):
    """Status bits of SYSTEM_STATUS (0x00C3)."""

    DC_OK = 1 << 1  # secondary DC output voltage status (1 = normal)
    INITIALIZED = 1 << 5  # device initialized
    EEPROM_ERROR = 1 << 6  # EEPROM data access error (unit shuts down)
    REMOTE_CONTROL = 1 << 8  # remote hardware control status (1 = ON)


class SystemConfig(IntFlag):
    """Configuration bits of SYSTEM_CONFIG (0x00C4).

    The individual writable bits are modelled as packed bit fields on the
    ``Configuration`` component; this flag type decodes whole-register reads.
    """

    MOD_CTRL = 1 << 0  # 1 = V/I/ON-OFF defined by Modbus (else SVR/potentiometer)
    OPERATION_INIT = 0b11 << 1  # power-on behaviour mask (see OperationInit)
    PEAK_EN = 1 << 3  # peak power / transient peak current enable
    EEP_CONFIG = 0b11 << 8  # EEPROM storage mode mask (see EepConfig)
    EEP_OFF = 1 << 10  # 1 = disable EEPROM save


class ProtectConfig(IntFlag):
    """Configuration bits of PROTECT_CONFIG (0x00C5)."""

    OLP_TYPE = 0b11 << 0  # overload protection behaviour mask (see OlpType)
    EMFP_EN = 1 << 8  # back-EMF protection enable (factory default 1)
