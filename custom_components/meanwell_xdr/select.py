"""Select platform — communication and behaviour enumerations."""

from dataclasses import dataclass
from enum import IntEnum

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from xdr_modbus import BaudRate, EepConfig, FrameFormat, OlpType, OperationInit

from .coordinator import XDRConfigEntry, XDRCoordinator
from .entity import XDREntity


@dataclass(frozen=True, kw_only=True)
class XDRSelectDescription(SelectEntityDescription):
    """Describes a select backed by one writable enum/bit-run field."""

    component: str
    attribute: str  # int/enum field on the component; written with the same name
    enum_type: type[IntEnum]


_SELECTS: tuple[XDRSelectDescription, ...] = (
    XDRSelectDescription(
        key="configuration_baud_rate",
        name="Baud rate",
        component="configuration",
        attribute="baud_rate",
        enum_type=BaudRate,
        entity_category=EntityCategory.CONFIG,
    ),
    XDRSelectDescription(
        key="configuration_frame_format",
        name="Frame format",
        component="configuration",
        attribute="frame_format",
        enum_type=FrameFormat,
        entity_category=EntityCategory.CONFIG,
    ),
    XDRSelectDescription(
        key="configuration_power_on_behavior",
        name="Power-on behavior",
        component="configuration",
        attribute="power_on_behavior",
        enum_type=OperationInit,
        entity_category=EntityCategory.CONFIG,
    ),
    XDRSelectDescription(
        key="configuration_overload_protection",
        name="Overload protection",
        component="configuration",
        attribute="overload_protection",
        enum_type=OlpType,
        entity_category=EntityCategory.CONFIG,
    ),
    XDRSelectDescription(
        key="configuration_eeprom_mode",
        name="EEPROM mode",
        component="configuration",
        attribute="eeprom_mode",
        enum_type=EepConfig,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: XDRConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up XDR selects."""
    coordinator = entry.runtime_data
    async_add_entities(XDRSelect(coordinator, d) for d in _SELECTS)


class XDRSelect(XDREntity, SelectEntity):
    """A select writing one writable enum field of the configuration."""

    entity_description: XDRSelectDescription

    def __init__(
        self, coordinator: XDRCoordinator, description: XDRSelectDescription
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator, description.key, description.component)
        self.entity_description = description
        self._attr_options = [member.name.lower() for member in description.enum_type]

    @property
    def current_option(self) -> str | None:
        """Return the current enum member as a lowercase name."""
        value = getattr(self._subsystem, self.entity_description.attribute)
        if value is None:
            return None
        return self.entity_description.enum_type(int(value)).name.lower()

    async def async_select_option(self, option: str) -> None:
        """Write the selected enum member."""
        member = self.entity_description.enum_type[option.upper()]
        await self._subsystem.write(self.entity_description.attribute, int(member))
        await self.coordinator.async_request_refresh()
