from datetime import datetime
from typing import List, Dict, Any
from app.services.ingestion.connectors.base_connector import BaseConnector
from app.services.ingestion.models import DisasterObservation, DataSourceType, HazardType
from app.services.ingestion.normalizer import normalizer

class SensorConnector(BaseConnector):
    """
    Ingests IoT telemetry: ultrasonic river water level gauges, submerged road pressure sensors,
    telecom tower battery/ping status, and substation power meters.
    """
    def __init__(self):
        super().__init__(name="IoT Sensor Grid & Critical Infrastructure Telemetry", source_type=DataSourceType.SENSOR)

    def fetch_observations(self) -> List[DisasterObservation]:
        self.last_sync = datetime.utcnow().isoformat() + "Z"
        return [
            normalizer.normalize_raw_telemetry(
                source="Corridor 14 Road Water Depth Sensor #RD-14-B",
                hazard_type="ROAD_BLOCKAGE",
                value=1.0,
                unit="status",
                lat=28.6160,
                lng=77.2120,
                zone_id="zone-7",
                source_type=DataSourceType.SENSOR,
                confidence=0.97,
                metadata={
                    "water_depth_over_road_cm": 68.0,
                    "passability_pct": 29,
                    "flow_velocity_mps": 2.4
                }
            ),
            normalizer.normalize_raw_telemetry(
                source="Cellular Tower Node Delta-4 Telemetry",
                hazard_type="TELECOM_OUTAGE",
                value=85.0,
                unit="%_loss",
                lat=28.5810,
                lng=77.1890,
                zone_id="zone-4",
                source_type=DataSourceType.SENSOR,
                confidence=0.99,
                metadata={
                    "status": "OFFLINE",
                    "backup_battery_hours_remaining": 0.0,
                    "active_connected_devices": 0,
                    "alarm": "SILENT_CRISIS_INDICATOR"
                }
            ),
            normalizer.normalize_raw_telemetry(
                source="Substation #2 Flood Intrusion Alarm",
                hazard_type="POWER_OUTAGE",
                value=0.0, # Currently still powered, but warning
                unit="status",
                lat=28.6220,
                lng=77.2180,
                zone_id="zone-7",
                source_type=DataSourceType.SENSOR,
                confidence=0.95,
                metadata={
                    "bund_water_margin_cm": 15.0,
                    "generator_backup": "ONLINE",
                    "alert": "CASCADE_THREAT"
                }
            )
        ]

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": "Municipal SCADA / IoT LoRaWAN Sensor Network",
            "status": "HEALTHY",
            "source_type": self.source_type.value,
            "polling_interval_sec": 10,
            "last_sync": self.last_sync
        }
