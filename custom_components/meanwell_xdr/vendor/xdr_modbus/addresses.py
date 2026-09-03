"""Register addresses of the Mean Well XDR series (manual XDR-75~960-E, §6).

All addresses are zero-based protocol addresses, exactly as they appear on the
wire (the manual documents them in hexadecimal, e.g. VOUT_SET at ``0x0020``).
The device answers function codes 0x03 (read holding), 0x04 (read input) and
0x06 (write single holding register) only — there are no coils.
"""

from __future__ import annotations

# -- Input registers (FC 0x04, read-only) --------------------------------------

READ_VIN = 0x0050  # 80: AC input voltage, factor 0.1 (default), in V
READ_VOUT = 0x0060  # 96: output voltage, factor 0.01 (default), in V
READ_IOUT = 0x0061  # 97: output current, factor 0.01 (default), in A
READ_TEMPERATURE_1 = 0x0062  # 98: internal ambient temperature, factor 0.1, in °C
READ_POUT = 0x0063  # 99: output power, factor 1 (default), in W

# Readable input-register ranges (inclusive); keeps block reads inside what the
# device actually answers.
INPUT_RANGES: tuple[tuple[int, int], ...] = (
    (READ_VIN, READ_VIN),
    (READ_VOUT, READ_POUT),
)

# -- Holding registers (FC 0x03 read / 0x06 write) ------------------------------

OPERATION = 0x0000  # 0: output ON/OFF — 0x0000 OFF, 0x0001 ON (default ON)
VOUT_SET = 0x0020  # 32: output voltage setpoint, factor 0.01, in V
IOUT_SET = 0x0030  # 48: output current limit setpoint, factor 0.01, in A
FAULT_STATUS_1 = 0x0040  # 64: alarm bit field 1
FAULT_STATUS_2 = 0x0041  # 65: alarm bit field 2

MFR_ID = 0x0080  # 128-133: manufacturer name, 12 ASCII chars ("MEAN WELL")
MFR_MODEL = 0x0086  # 134-139: model name, 12 ASCII chars (e.g. "XDR-240-24")
MFR_REVISION = 0x008C  # 140-142: firmware revision, one byte per MCU
MFR_LOCATION = 0x008F  # 143-144: manufacturer place, 4 ASCII chars
MFR_DATE = 0x0091  # 145-147: manufacture date, 6 ASCII chars (YYMMDD)
MFR_SERIAL = 0x0094  # 148-153: serial number, 12 ASCII chars

SCALING_FACTOR = 0x00C0  # 192-194: live scaling-factor report, 3 registers
SYSTEM_STATUS = 0x00C3  # 195: system status bit field
SYSTEM_CONFIG = 0x00C4  # 196: control-source and EEPROM configuration
PROTECT_CONFIG = 0x00C5  # 197: protection behaviour configuration
RESET_DEFAULT = 0x00C6  # 198: write 0xAA to restore factory settings

AC_FAIL_LL_SET = 0x00E0  # 224: AC low-line failover threshold, factor 0.1, in V
AC_OK_LL_SET = 0x00E2  # 226: AC low-line recovery threshold, factor 0.1, in V

DC_OK_SET = 0x00F0  # 240: DC OK threshold, factor 0.01, in % of output voltage
PEAK_SET = 0x00F1  # 241: peak output current limit, factor 0.01, in % of rated
OL_ALARM_LEVEL = 0x00F3  # 243: overload pre-alarm threshold, factor 0.01, in %

MODBUS_ID = 0x0900  # 2304: slave address 0x80-0xBF (default 0x83)
MODBUS_BAUD = 0x0901  # 2305: baud rate enum
MODBUS_FORMAT = 0x0902  # 2306: frame format enum

CLEAR_LOG = 0x0910  # 2320: write 0xAA to clear the event log

TOTAL_PSON_TIME = 0x0913  # 2323-2324: total run time (non-volatile), uint32
PSON_TIME = 0x0915  # 2325-2326: run time since AC ON, uint32

OVP_CNT = 0x0919  # 2329: output over-voltage protection trigger counter
OLP_CNT = 0x091A  # 2330: output overload protection trigger counter
OTP_CNT = 0x091B  # 2331: over-temperature protection trigger counter
ACUVP_CNT = 0x091C  # 2332: AC under-voltage protection trigger counter
ACOVP_CNT = 0x091D  # 2333: AC over-voltage protection trigger counter

EVENT_0 = 0x0921  # 2337: most recent fault event code
EVENT_1 = 0x0922  # 2338: second-most recent fault event code
EVENT_2 = 0x0923  # 2339: third-most recent fault event code

# Readable holding-register ranges (inclusive). The map is sparse: addresses
# between these ranges are undocumented and must not be read.
HOLDING_RANGES: tuple[tuple[int, int], ...] = (
    (OPERATION, OPERATION),
    (VOUT_SET, VOUT_SET),
    (IOUT_SET, IOUT_SET),
    (FAULT_STATUS_1, FAULT_STATUS_2),
    (MFR_ID, MFR_SERIAL + 5),
    (SCALING_FACTOR, RESET_DEFAULT),
    (AC_FAIL_LL_SET, AC_FAIL_LL_SET),
    (AC_OK_LL_SET, AC_OK_LL_SET),
    (DC_OK_SET, PEAK_SET),
    (OL_ALARM_LEVEL, OL_ALARM_LEVEL),
    (MODBUS_ID, MODBUS_FORMAT),
    (CLEAR_LOG, CLEAR_LOG),
    (TOTAL_PSON_TIME, PSON_TIME + 1),
    (OVP_CNT, ACOVP_CNT),
    (EVENT_0, EVENT_2),
)

DEFAULT_UNIT_ID = 0x83  # 131: the factory-default slave address
UNIT_ID_RANGE: tuple[int, int] = (0x80, 0xBF)

# Value that triggers the command registers.
COMMAND_KEY = 0xAA
