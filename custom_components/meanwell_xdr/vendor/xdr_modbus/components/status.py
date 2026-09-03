"""Status registers — fault and system status bit fields."""

from __future__ import annotations

from ..addresses import FAULT_STATUS_1, FAULT_STATUS_2, SYSTEM_STATUS
from ..data_model import XDRComponent, flags
from ..enums import FaultStatus1, FaultStatus2, SystemStatus


class Status(XDRComponent):
    """Fault and operational status of the power supply."""

    fault_status_1 = flags(
        FAULT_STATUS_1,
        FaultStatus1,
        command="FAULT_STATUS_1",
        description="Abnormal status 1 (OTP/OVP/OLP/AC fail/DC off/high temp)",
    )
    """Alarm bit field 1."""

    fault_status_2 = flags(
        FAULT_STATUS_2,
        FaultStatus2,
        command="FAULT_STATUS_2",
        description="Abnormal status 2 (back-EMF, overload pre-alarm)",
    )
    """Alarm bit field 2."""

    system_status = flags(
        SYSTEM_STATUS,
        SystemStatus,
        command="SYSTEM_STATUS",
        description="System operational status (DC OK, initialized, EEPROM, remote)",
    )
    """System operational status."""
