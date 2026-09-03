"""Switch platform — output power and the Modbus control source."""

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import XDRConfigEntry, XDRCoordinator
from .entity import XDREntity


@dataclass(frozen=True, kw_only=True)
class XDRSwitchDescription(SwitchEntityDescription):
    """Describes a switch backed by one writable component field."""

    component: str
    attribute: str  # bool field on the component; written with the same name


_SWITCHES: tuple[XDRSwitchDescription, ...] = (
    XDRSwitchDescription(
        key="control_operation",
        name="Output power",
        component="control",
        attribute="operation",
    ),
    XDRSwitchDescription(
        key="configuration_modbus_control",
        name="Modbus control",
        component="configuration",
        attribute="modbus_control",
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: XDRConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up XDR switches."""
    coordinator = entry.runtime_data
    async_add_entities(XDRSwitch(coordinator, d) for d in _SWITCHES)


class XDRSwitch(XDREntity, SwitchEntity):
    """A switch writing one writable field of one component."""

    entity_description: XDRSwitchDescription

    def __init__(
        self, coordinator: XDRCoordinator, description: XDRSwitchDescription
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, description.key, description.component)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return the current switch state."""
        return getattr(self._subsystem, self.entity_description.attribute)

    async def async_turn_on(self, **kwargs: object) -> None:
        """Turn the switch on."""
        await self._subsystem.write(self.entity_description.attribute, True)

    async def async_turn_off(self, **kwargs: object) -> None:
        """Turn the switch off."""
        await self._subsystem.write(self.entity_description.attribute, False)
