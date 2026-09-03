"""Binary-sensor platform — fault flags, DC status and output state."""

from dataclasses import dataclass
from enum import IntFlag

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from xdr_modbus import FaultStatus1, FaultStatus2, SystemStatus

from .coordinator import XDRConfigEntry, XDRCoordinator
from .entity import XDREntity


@dataclass(frozen=True, kw_only=True)
class XDRBinaryDescription(BinarySensorEntityDescription):
    """Describes a binary sensor reading one bit of a flags field."""

    attribute: str  # flags attribute on the status component
    flag: IntFlag
    inverted: bool = False  # True when the bit set means the sensor is OFF


def _alarm(
    attribute: str,
    flag: IntFlag,
    name: str,
) -> XDRBinaryDescription:
    return XDRBinaryDescription(
        key=f"{attribute.lower()}_{flag.name.lower()}",
        name=name,
        attribute=attribute,
        flag=flag,
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
    )


_STATUS: tuple[XDRBinaryDescription, ...] = (
    _alarm("fault_status_1", FaultStatus1.OTP, "Over-temperature protection"),
    _alarm("fault_status_1", FaultStatus1.OVP, "Over-voltage protection"),
    _alarm("fault_status_1", FaultStatus1.OLP, "Overload protection"),
    _alarm("fault_status_1", FaultStatus1.AC_FAIL, "AC input fail"),
    _alarm("fault_status_1", FaultStatus1.HI_TEMP, "High temperature"),
    _alarm("fault_status_2", FaultStatus2.EMFP, "Back-EMF protection"),
    _alarm("fault_status_2", FaultStatus2.OL_ALM, "Overload pre-alarm"),
    _alarm("system_status", SystemStatus.EEPROM_ERROR, "EEPROM error"),
    XDRBinaryDescription(
        key="system_status_dc_ok",
        name="DC OK",
        attribute="system_status",
        flag=SystemStatus.DC_OK,
        device_class=BinarySensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    XDRBinaryDescription(
        key="fault_status_1_output",
        name="Output",
        attribute="fault_status_1",
        flag=FaultStatus1.OP_OFF,
        device_class=BinarySensorDeviceClass.POWER,
        inverted=True,  # OP_OFF set means the DC output is off
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: XDRConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up XDR binary sensors."""
    coordinator = entry.runtime_data
    async_add_entities(XDRBinarySensor(coordinator, d) for d in _STATUS)


class XDRBinarySensor(XDREntity, BinarySensorEntity):
    """A single alarm/state bit read from a flags attribute."""

    entity_description: XDRBinaryDescription

    def __init__(
        self, coordinator: XDRCoordinator, description: XDRBinaryDescription
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, description.key, "status")
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return true if the flag is set (inverted for negative-logic bits)."""
        flags = getattr(self._subsystem, self.entity_description.attribute)
        if flags is None:
            return None
        bit = bool(flags & self.entity_description.flag)
        return not bit if self.entity_description.inverted else bit
