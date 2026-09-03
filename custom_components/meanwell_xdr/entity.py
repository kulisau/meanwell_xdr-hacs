"""Base entity for Mean Well XDR.

Every entity belongs to the single power-supply device identified by its
config entry.
"""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import XDRCoordinator


class XDREntity(CoordinatorEntity[XDRCoordinator]):
    """Common identity + device-info for every XDR entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: XDRCoordinator, key: str, component: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._component = component
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        info = coordinator.device.info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer=info.manufacturer or "MEAN WELL",
            model=info.model_name,
            name=info.model_name,
            sw_version=info.firmware_version,
            serial_number=info.serial_number,
        )

    @property
    def _subsystem(self) -> object:
        """The library sub-system object this entity reads from."""
        return getattr(self.coordinator.device, self._component)
