"""Statistics registers — run times, protection counters and the event log."""

from __future__ import annotations

from ..addresses import (
    ACOVP_CNT,
    ACUVP_CNT,
    EVENT_0,
    EVENT_1,
    EVENT_2,
    OLP_CNT,
    OTP_CNT,
    OVP_CNT,
    PSON_TIME,
    TOTAL_PSON_TIME,
)
from ..data_model import XDRComponent, enum, integer, uint32
from ..enums import EventCode


class Statistics(XDRComponent):
    """Non-volatile statistics of the power supply.

    The manual does not document the unit of the run-time counters; they are
    exposed as raw 32-bit values.
    """

    total_runtime = uint32(
        TOTAL_PSON_TIME,
        command="TOTAL_PSON_TIME",
        description="Total run time (non-volatile, unit not documented)",
    )
    """Total run time since manufacture (32-bit)."""

    session_runtime = uint32(
        PSON_TIME,
        command="PSON_TIME",
        description="Run time since AC ON (cleared at AC ON, unit not documented)",
    )
    """Run time of the current AC session (32-bit)."""

    overvoltage_protection_count = integer(
        OVP_CNT, command="OVP_CNT", description="OVP trigger counter"
    )
    """Output over-voltage protection trigger counter."""

    overload_protection_count = integer(
        OLP_CNT, command="OLP_CNT", description="OLP trigger counter"
    )
    """Output overload protection trigger counter."""

    overheat_protection_count = integer(
        OTP_CNT, command="OTP_CNT", description="OTP trigger counter"
    )
    """Over-temperature protection trigger counter."""

    ac_undervoltage_protection_count = integer(
        ACUVP_CNT, command="ACUVP_CNT", description="ACUVP trigger counter"
    )
    """AC under-voltage protection trigger counter."""

    ac_overvoltage_protection_count = integer(
        ACOVP_CNT, command="ACOVP_CNT", description="ACOVP trigger counter"
    )
    """AC over-voltage protection trigger counter."""

    latest_event = enum(
        EVENT_0, EventCode, command="EVENT_0", description="Most recent fault event"
    )
    """Most recent fault event code."""

    previous_event = enum(
        EVENT_1,
        EventCode,
        command="EVENT_1",
        description="Second-most recent fault event",
    )
    """Second-most recent fault event code."""

    oldest_event = enum(
        EVENT_2,
        EventCode,
        command="EVENT_2",
        description="Third-most recent fault event",
    )
    """Third-most recent fault event code."""
