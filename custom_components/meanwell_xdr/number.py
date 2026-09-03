"""Number platform — setpoints and protection thresholds.

The voltage/current setpoint limits come from the detected model; the
threshold numbers use the fixed ranges from the manufacturer manual.
"""

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import XDRConfigEntry, XDRCoordinator
from .entity import XDREntity


@dataclass(frozen=True, kw_only=True)
class XDRNumberDescription(NumberEntityDescription):
    """Describes a number backed by one writable component field."""

    component: str
    attribute: str  # written with the same name on the component


# Setpoints whose limits are model-dependent (resolved at runtime).
_MODEL_NUMBERS: tuple[XDRNumberDescription, ...] = (
    XDRNumberDescription(
        key="control_voltage_setpoint",
        name="Voltage setpoint",
        component="control",
        attribute="voltage_setpoint",
        device_class=NumberDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        mode=NumberMode.BOX,
    ),
    XDRNumberDescription(
        key="control_current_setpoint",
        name="Current setpoint",
        component="control",
        attribute="current_setpoint",
        device_class=NumberDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        mode=NumberMode.BOX,
    ),
)

# Thresholds with fixed documented ranges.
_THRESHOLDS: tuple[XDRNumberDescription, ...] = (
    XDRNumberDescription(
        key="configuration_ac_fail_threshold",
        name="AC failover threshold",
        component="configuration",
        attribute="ac_fail_threshold",
        native_min_value=74.0,
        native_max_value=264.0,
        native_step=0.1,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        entity_category=EntityCategory.CONFIG,
        mode=NumberMode.BOX,
    ),
    XDRNumberDescription(
        key="configuration_ac_recover_threshold",
        name="AC recovery threshold",
        component="configuration",
        attribute="ac_recover_threshold",
        native_min_value=79.0,
        native_max_value=269.0,
        native_step=0.1,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        entity_category=EntityCategory.CONFIG,
        mode=NumberMode.BOX,
    ),
    XDRNumberDescription(
        key="configuration_dc_ok_threshold",
        name="DC OK threshold",
        component="configuration",
        attribute="dc_ok_threshold",
        native_min_value=70.0,
        native_max_value=95.0,
        native_step=0.01,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.CONFIG,
        mode=NumberMode.BOX,
    ),
    XDRNumberDescription(
        key="configuration_peak_current_limit",
        name="Peak current limit",
        component="configuration",
        attribute="peak_current_limit",
        native_min_value=125.0,
        native_max_value=600.0,
        native_step=1.0,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.CONFIG,
        mode=NumberMode.BOX,
    ),
    XDRNumberDescription(
        key="configuration_overload_alarm_level",
        name="Overload alarm level",
        component="configuration",
        attribute="overload_alarm_level",
        native_min_value=70.0,
        native_max_value=95.0,
        native_step=0.01,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.CONFIG,
        mode=NumberMode.BOX,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: XDRConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up XDR numbers."""
    coordinator = entry.runtime_data
    async_add_entities(
        [XDRNumber(coordinator, d, model_limits=None) for d in _THRESHOLDS]
        + [XDRNumber(coordinator, d, model_limits=True) for d in _MODEL_NUMBERS]
    )


class XDRNumber(XDREntity, NumberEntity):
    """A number writing one writable field of one component."""

    entity_description: XDRNumberDescription

    def __init__(
        self,
        coordinator: XDRCoordinator,
        description: XDRNumberDescription,
        *,
        model_limits: bool,
    ) -> None:
        """Initialize the number; ``model_limits`` takes min/max from the model."""
        super().__init__(coordinator, description.key, description.component)
        self.entity_description = description
        self._model_limits = model_limits

    @property
    def native_value(self) -> float | None:
        """Return the current setpoint/threshold value."""
        return getattr(self._subsystem, self.entity_description.attribute)

    @property
    def native_min_value(self) -> float:
        """The lower bound; from the model for the output setpoints."""
        if self._model_limits:
            definition = self.coordinator.device.model_definition
            if definition is not None:
                if self.entity_description.attribute == "voltage_setpoint":
                    return definition.vout_set_range[0]
                return definition.iout_set_range[0]
        return self.entity_description.native_min_value

    @property
    def native_max_value(self) -> float:
        """The upper bound; from the model for the output setpoints."""
        if self._model_limits:
            definition = self.coordinator.device.model_definition
            if definition is not None:
                if self.entity_description.attribute == "voltage_setpoint":
                    return definition.vout_set_range[1]
                return definition.iout_set_range[1]
        return self.entity_description.native_max_value

    async def async_set_native_value(self, value: float) -> None:
        """Write the new value; the library range-checks model limits."""
        await self._subsystem.write(self.entity_description.attribute, value)
        await self.coordinator.async_request_refresh()
