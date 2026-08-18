from datetime import datetime
from typing import List, Dict, Any
from app.services.ingestion.connectors.base_connector import BaseConnector
from app.services.ingestion.models import DisasterObservation, DataSourceType, HazardType
from app.services.ingestion.normalizer import normalizer

class SatelliteConnector(BaseConnector):
    """
    Ingests Synthetic Aperture Radar (SAR) flood inundation polygons and optical earth observation metadata.
    """
    def __init__(self):
        super().__init__(name="SAR Satellite & Earth Observation Feed", source_type=DataSourceType.OFFICIAL)

    def fetch_observations(self) -> List[DisasterObservation]:
        self.last_sync = datetime.utcnow().isoformat() + "Z"
        return [
            normalizer.normalize_raw_telemetry(
                source="Copernicus Sentinel-1 SAR Overpass",
                hazard_type="FLOOD_DEPTH",
                value=95.0,
                unit="cm",
                lat=28.6145,
                lng=77.2085,
                zone_id="zone-7",
                source_type=DataSourceType.OFFICIAL,
                confidence=0.91,
                metadata={
                    "satellite": "Sentinel-1B C-Band SAR",
                    "polarization": "VV+VH",
                    "inundated_area_sq_km": 4.8,
                    "cloud_penetration": "100% (Radar Synthetic Aperture)"
                }
            ),
            normalizer.normalize_raw_telemetry(
                source="Disaster Constellation Multi-Spectral Optical",
                hazard_type="STRUCTURAL_DAMAGE",
                value=0.75,
                unit="damage_index",
                lat=28.5820,
                lng=77.1920,
                zone_id="zone-4",
                source_type=DataSourceType.OFFICIAL,
                confidence=0.85,
                metadata={
                    "resolution_m": 0.5,
                    "damaged_roofs_detected": 42,
                    "submerged_structures": 118
                }
            )
        ]

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": "ESA Copernicus / Planet Disaster Constellation SAR Adapter",
            "status": "HEALTHY",
            "source_type": self.source_type.value,
            "polling_interval_sec": 300,
            "last_sync": self.last_sync
        }
