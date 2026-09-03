"""Sensor platform — measurements, statistics and scaling factors.

Live measurements are the primary entities; run-time counters, protection
counters, the event log and the reported scaling factors are diagnostic.
"""

from dataclasses import dataclass
from enum import IntEnum

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from xdr_modbus import EventCode

from .coordinator import XDRConfigEntry, XDRCoordinator
from .entity import XDREntity

_EVENT_OPTIONS = [event.name.lower() for event in EventCode]


@dataclass(frozen=True, kw_only=True)
class XDRSensorDescription(SensorEntityDescription):
    """Describes a sensor reading one attribute of one component."""

    component: str
    attribute: str


def _measurement(
    attribute: str,
    name: str,
    device_class: SensorDeviceClass,
    unit: str,
) -> XDRSensorDescription:
    return XDRSensorDescription(
        key=f"measurements_{attribute}",
        name=name,
        component="measurements",
        attribute=attribute,
        device_class=device_class,
        native_unit_of_measurement=unit,
        state_class=SensorStateClass.MEASUREMENT,
    )


def _counter(component: str, attribute: str, name: str) -> XDRSensorDescription:
    return XDRSensorDescription(
        key=f"{component}_{attribute}",
        name=name,
        component=component,
        attribute=attribute,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
    )


_MEASUREMENTS: tuple[XDRSensorDescription, ...] = (
    _measurement(
        "input_voltage",
        "Input voltage",
        SensorDeviceClass.VOLTAGE,
        UnitOfElectricPotential.VOLT,
    ),
    _measurement(
        "output_voltage",
        "Output voltage",
        SensorDeviceClass.VOLTAGE,
        UnitOfElectricPotential.VOLT,
    ),
    _measurement(
        "output_current",
        "Output current",
        SensorDeviceClass.CURRENT,
        UnitOfElectricCurrent.AMPERE,
    ),
    _measurement(
        "internal_temperature",
        "Internal temperature",
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
    ),
    _measurement(
        "output_power", "Output power", SensorDeviceClass.POWER, UnitOfPower.WATT
    ),
)

_COUNTERS: tuple[XDRSensorDescription, ...] = (
    _counter("statistics", "total_runtime", "Total runtime"),
    _counter("statistics", "session_runtime", "Session runtime"),
    _counter("statistics", "overvoltage_protection_count", "OVP trigger count"),
    _counter("statistics", "overload_protection_count", "OLP trigger count"),
    _counter("statistics", "overheat_protection_count", "OTP trigger count"),
    _counter("statistics", "ac_undervoltage_protection_count", "ACUVP trigger count"),
    _counter("statistics", "ac_overvoltage_protection_count", "ACOVP trigger count"),
)

_EVENTS: tuple[XDRSensorDescription, ...] = tuple(
    XDRSensorDescription(
        key=f"statistics_{attribute}",
        name=name,
        component="statistics",
        attribute=attribute,
        device_class=SensorDeviceClass.ENUM,
        options=_EVENT_OPTIONS,
        entity_category=EntityCategory.DIAGNOSTIC,
    )
    for attribute, name in (
        ("latest_event", "Latest event"),
        ("previous_event", "Previous event"),
        ("oldest_event", "Oldest event"),
    )
)

_SCALING: tuple[XDRSensorDescription, ...] = tuple(
    XDRSensorDescription(
        key=f"scaling_{attribute}",
        name=name,
        component="scaling",
        attribute=attribute,
        entity_category=EntityCategory.DIAGNOSTIC,
    )
    for attribute, name in (
        ("output_voltage_factor", "Output voltage factor"),
        ("output_current_factor", "Output current factor"),
        ("input_voltage_factor", "Input voltage factor"),
        ("temperature_factor", "Temperature factor"),
    )
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: XDRConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up XDR sensors."""
    coordinator = entry.runtime_data
    descriptions = (*_MEASUREMENTS, *_COUNTERS, *_EVENTS, *_SCALING)
    async_add_entities(XDRSensor(coordinator, d) for d in descriptions)


class XDRSensor(XDREntity, SensorEntity):
    """A single value read from a component attribute."""

    entity_description: XDRSensorDescription

    def __init__(
        self, coordinator: XDRCoordinator, description: XDRSensorDescription
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key, description.component)
        self.entity_description = description

    @property
    def native_value(self) -> object:
        """Return the current value, mapping enums to their lowercase name."""
        value = getattr(self._subsystem, self.entity_description.attribute)
        if isinstance(value, IntEnum):
            return value.name.lower()
        return value
