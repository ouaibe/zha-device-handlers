"""ZHA Quirk (v2) for Stello HT402.

Adds manufacturer attributes:
- 0x4001: Outdoor temperature (°C or °F, read/write)
- 0x4008: Instant power (W)
- 0x4009: Cumulative energy (Wh)
- 0x4105: Peak demand event icon (uint16, read/write)
"""

from zigpy.quirks import CustomCluster
from zigpy.quirks.v2 import (
    NumberDeviceClass,
    QuirkBuilder,
    ReportingConfig,
    SensorDeviceClass,
    SensorStateClass,
)
from zigpy.quirks.v2.homeassistant import (
    EntityType,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
import zigpy.types as t
from zigpy.zcl.clusters.hvac import Thermostat
from zigpy.zcl.foundation import ZCLAttributeDef

# ──────────────────────────────────────────────────────────────
# Custom Thermostat cluster
# ──────────────────────────────────────────────────────────────


class AlliaThermostatCluster(Thermostat, CustomCluster):
    """Thermostat cluster extended with Stello/Allia manufacturer attributes."""

    class AttributeDefs(Thermostat.AttributeDefs):
        """Vendor-specific attributes added to the Thermostat cluster.

        - 0x4001: Outdoor temperature (°C or °F, read/write)
        - 0x4008: Instant power (W)
        - 0x4009: Cumulative energy (Wh)
        - 0x4105: Peak demand event icon (uint16, read/write)
        """

        # 0x4001: Outdoor temperature (int16, read/write)
        outdoor_temperature = ZCLAttributeDef(
            id=0x4001,
            type=t.int16s,
            access="rpw",
        )
        # 0x4008: Instant power in Watts (uint16)
        power_w = ZCLAttributeDef(id=0x4008, type=t.uint16_t, access="rp")
        # 0x4009: Cumulative energy in Watt-hours (uint32)
        energy_wh = ZCLAttributeDef(id=0x4009, type=t.uint32_t, access="rp")
        # 0x4105: Peak demand event icon, read/write
        peak_demand_event_icon = ZCLAttributeDef(
            id=0x4105, type=t.uint16_t, access="rpw"
        )


(
    QuirkBuilder("Stello", "HT402")
    .applies_to("Stello", "STLO-34")
    .replaces(AlliaThermostatCluster, endpoint_id=25)
    # Local temperature
    .sensor(
        attribute_name=AlliaThermostatCluster.AttributeDefs.local_temperature.name,
        cluster_id=AlliaThermostatCluster.cluster_id,
        endpoint_id=25,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit=UnitOfTemperature.CELSIUS,
        reporting_config=ReportingConfig(
            min_interval=5, max_interval=300, reportable_change=1
        ),
        multiplier=0.01,
        fallback_name="Temperature",
    )
    # Instant Power
    .sensor(
        attribute_name=AlliaThermostatCluster.AttributeDefs.power_w.name,
        cluster_id=AlliaThermostatCluster.cluster_id,
        endpoint_id=25,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        unit=UnitOfPower.WATT,
        reporting_config=ReportingConfig(
            min_interval=5, max_interval=300, reportable_change=1
        ),
        fallback_name="Power",
    )
    # Energy (cumulative)
    .sensor(
        attribute_name=AlliaThermostatCluster.AttributeDefs.energy_wh.name,
        cluster_id=AlliaThermostatCluster.cluster_id,
        endpoint_id=25,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit=UnitOfEnergy.WATT_HOUR,
        reporting_config=ReportingConfig(
            min_interval=30, max_interval=3600, reportable_change=10
        ),
        fallback_name="Energy",
    )
    # Outdoor Temperature (0x4001) — read/write
    .number(
        attribute_name=AlliaThermostatCluster.AttributeDefs.outdoor_temperature.name,
        cluster_id=AlliaThermostatCluster.cluster_id,
        endpoint_id=25,
        min_value=-3200,
        max_value=19900,
        step=0.1,
        unit=UnitOfTemperature.CELSIUS,
        multiplier=0.01,
        entity_type=EntityType.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        translation_key="outdoor_temperature",
        fallback_name="Outdoor temperature",
    )
    # Peak demand event icon display time
    .number(
        attribute_name=AlliaThermostatCluster.AttributeDefs.peak_demand_event_icon.name,
        cluster_id=AlliaThermostatCluster.cluster_id,
        endpoint_id=25,
        min_value=0,
        max_value=64800,
        unit=UnitOfTime.SECONDS,
        entity_type=EntityType.CONFIG,
        translation_key="peak_demand_event_icon",
        fallback_name="Peak demand event display time",
    )
    .add_to_registry()
)
