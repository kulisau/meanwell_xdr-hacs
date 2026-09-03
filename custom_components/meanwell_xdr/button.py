"""Button platform — one-shot device commands.

Both commands write the 0xAA command key the protocol requires and take
effect after the power supply restarts.
"""

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import vendor  # noqa: F401  # adds vendor/ to sys.path before xdr_modbus
from .const import COMMAND_KEY
from .coordinator import XDRConfigEntry, XDRCoordinator
from .entity import XDREntity

_BUTTONS: tuple[ButtonEntityDescription, ...] = (
    ButtonEntityDescription(
        key="configuration_reset_defaults",
        name="Factory reset (restarts the power supply)",
        entity_category=EntityCategory.CONFIG,
    ),
    ButtonEntityDescription(
        key="configuration_clear_event_log",
        name="Clear event log",
        entity_category=EntityCategory.CONFIG,
    ),
)

# The command registers pair with the configuration component fields.
_COMPONENT = "configuration"
_ATTRIBUTES = {
    "configuration_reset_defaults": "reset_defaults",
    "configuration_clear_event_log": "clear_event_log",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: XDRConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up XDR command buttons."""
    coordinator = entry.runtime_data
    async_add_entities(XDRButton(coordinator, d) for d in _BUTTONS)


class XDRButton(XDREntity, ButtonEntity):
    """A button writing the 0xAA command key to one command register."""

    entity_description: ButtonEntityDescription

    def __init__(
        self, coordinator: XDRCoordinator, description: ButtonEntityDescription
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, description.key, _COMPONENT)
        self.entity_description = description

    async def async_press(self) -> None:
        """Send the command; the device restarts to apply it."""
        await self._subsystem.write(
            _ATTRIBUTES[self.entity_description.key], COMMAND_KEY
        )
