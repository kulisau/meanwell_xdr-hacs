"""Read and control Mean Well XDR series power supplies over Modbus.

Construct ``XDRPowerSupply(unit)`` with a ``modbus_connection.ModbusUnit``,
call ``await device.async_update()``, then read its sub-systems as normal
Python objects::

    device.measurements.output_voltage
    device.status.fault_status_1
    device.configuration.baud_rate
    device.statistics.latest_event
"""

from .components.configuration import Configuration
from .components.control import Control
from .components.measurements import Measurements
from .components.statistics import Statistics
from .components.status import Status
from .device_info import Identity, ScalingFactors
from .enums import (
    BaudRate,
    EepConfig,
    EventCode,
    FaultStatus1,
    FaultStatus2,
    FrameFormat,
    OlpType,
    OperationInit,
    OutputVoltage,
    ProtectConfig,
    SystemConfig,
    SystemStatus,
)
from .exceptions import XdrError, XdrModelError, XdrValueValidationError
from .metadata import DatapointMetadata, metadata_for, require_metadata_for
from .models import ModelDefinition, models, parse_model
from .xdr import XDRPowerSupply, XDRProbe

__all__ = [
    "BaudRate",
    "Configuration",
    "Control",
    "DatapointMetadata",
    "EepConfig",
    "EventCode",
    "FaultStatus1",
    "FaultStatus2",
    "FrameFormat",
    "Identity",
    "Measurements",
    "ModelDefinition",
    "OlpType",
    "OperationInit",
    "OutputVoltage",
    "ProtectConfig",
    "ScalingFactors",
    "Statistics",
    "Status",
    "SystemConfig",
    "SystemStatus",
    "XDRPowerSupply",
    "XDRProbe",
    "XdrError",
    "XdrModelError",
    "XdrValueValidationError",
    "metadata_for",
    "models",
    "parse_model",
    "require_metadata_for",
]
