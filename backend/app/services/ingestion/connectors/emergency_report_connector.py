from datetime import datetime
from typing import List, Dict, Any
from app.services.ingestion.connectors.base_connector import BaseConnector
from app.services.ingestion.models import DisasterObservation, DataSourceType, HazardType
from app.services.ingestion.normalizer import normalizer

class EmergencyReportConnector(BaseConnector):
    """
    Ingests 911 / emergency CAD dispatch reports, citizen SOS mobile signals, and social media distress calls.
    """
    def __init__(self):
        super().__init__(name="Emergency CAD & Citizen SOS Feed", source_type=DataSourceType.CIVILIAN)

    def fetch_observations(self) -> List[DisasterObservation]:
        self.last_sync = datetime.utcnow().isoformat() + "Z"
        return [
            normalizer.normalize_raw_telemetry(
                source="Emergency Dispatch CAD #911-2026-8812",
                hazard_type="CIVILIAN_SOS",
                value=12.0,
                unit="trapped_individuals",
                lat=28.6140,
                lng=77.2070,
                zone_id="zone-7",
                source_type=DataSourceType.CIVILIAN,
                confidence=0.88,
                metadata={
                    "urgency": "HIGH",
                    "medical_needs": "3 elderly with oxygen dependency",
                    "floor_level": "2nd floor rising water",
                    "caller_status": "VERIFIED_RESIDENT"
                }
            ),
            normalizer.normalize_raw_telemetry(
                source="Citizen Mobile App SOS Beacon",
                hazard_type="CIVILIAN_SOS",
                value=4.0,
                unit="trapped_individuals",
                lat=28.6110,
                lng=77.2130,
                zone_id="zone-7",
                source_type=DataSourceType.CIVILIAN,
                confidence=0.82,
                metadata={
                    "gps_accuracy_m": 8.5,
                    "battery_level": 14,
                    "notes": "Corridor 14 bridge submerged, vehicle stranded"
                }
            )
        ]

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": "Municipal CAD 911 / Citizen SOS Gateway",
            "status": "HEALTHY",
            "source_type": self.source_type.value,
            "polling_interval_sec": 15,
            "last_sync": self.last_sync
        }
