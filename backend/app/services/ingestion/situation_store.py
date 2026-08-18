from typing import List, Dict, Optional, Any
from datetime import datetime
from app.services.ingestion.models import DisasterObservation, IngestionStatus, DataSourceType, HazardType
from app.services.ingestion.connectors.weather_connector import WeatherConnector
from app.services.ingestion.connectors.hazard_connector import HazardConnector
from app.services.ingestion.connectors.satellite_connector import SatelliteConnector
from app.services.ingestion.connectors.emergency_report_connector import EmergencyReportConnector
from app.services.ingestion.connectors.sensor_connector import SensorConnector
from app.data.flood_dataset import ZONES_DATA, ROADS_DATA, INFRASTRUCTURE_DATA

class SituationStateStore:
    """
    AEGIS Unified Situation State Store.
    Maintains ingested real/simulated observations, aggregates zone-level telemetry,
    and updates dynamic incident variables.
    """
    def __init__(self):
        self.connectors = {
            "weather": WeatherConnector(),
            "hazard": HazardConnector(),
            "satellite": SatelliteConnector(),
            "emergency_report": EmergencyReportConnector(),
            "sensor": SensorConnector()
        }
        self.observations: List[DisasterObservation] = []
        self.zone_overrides: Dict[str, Dict[str, Any]] = {}
        self.road_overrides: Dict[str, Dict[str, Any]] = {}
        self._init_baseline_observations()

    def _init_baseline_observations(self):
        """Polls initial observations from all connectors on boot."""
        self.observations.clear()
        for name, conn in self.connectors.items():
            try:
                obs = conn.fetch_observations()
                self.observations.extend(obs)
            except Exception as e:
                print(f"[Ingestion] Warning: Failed to fetch from connector {name}: {e}")

    def ingest_observation(self, obs: DisasterObservation) -> DisasterObservation:
        """Adds a single observation into the state store."""
        self.observations.insert(0, obs)
        # Keep most recent 500 observations
        if len(self.observations) > 500:
            self.observations = self.observations[:500]
        return obs

    def poll_all_connectors(self) -> List[DisasterObservation]:
        """Polls all active connectors and appends new observations."""
        new_obs: List[DisasterObservation] = []
        for name, conn in self.connectors.items():
            try:
                obs_list = conn.fetch_observations()
                for o in obs_list:
                    self.ingest_observation(o)
                    new_obs.append(o)
            except Exception as e:
                print(f"[Ingestion] Error polling {name}: {e}")
        return new_obs

    def get_observations(
        self,
        zone_id: Optional[str] = None,
        hazard_type: Optional[str] = None,
        source_type: Optional[str] = None,
        limit: int = 50
    ) -> List[DisasterObservation]:
        """Returns filtered observations."""
        res = self.observations
        if zone_id:
            res = [o for o in res if o.zone_id == zone_id or (o.zone_id and o.zone_id.lower() == zone_id.lower())]
        if hazard_type:
            res = [o for o in res if o.hazard_type.value == hazard_type.upper() or o.hazard_type == hazard_type]
        if source_type:
            res = [o for o in res if o.source_type.value == source_type.upper() or o.source_type == source_type]
        return res[:limit]

    def get_zone_telemetry(self, zone_id: str) -> Dict[str, Any]:
        """Aggregates multi-source telemetry for a target zone."""
        obs = [o for o in self.observations if o.zone_id == zone_id]
        
        # Base zone fallback
        zone = next((z for z in ZONES_DATA if z.id == zone_id), None)
        flood_depth = zone.current_flood_depth_cm if zone else 45.0
        rainfall = zone.rainfall_rate_mmh if zone else 20.0
        river_level = zone.river_level_meters if zone else 4.5
        
        # Check overrides from live feed simulator
        if zone_id in self.zone_overrides:
            ov = self.zone_overrides[zone_id]
            flood_depth = ov.get("current_flood_depth_cm", flood_depth)
            rainfall = ov.get("rainfall_rate_mmh", rainfall)
            river_level = ov.get("river_level_meters", river_level)

        return {
            "zone_id": zone_id,
            "observations_count": len(obs),
            "current_flood_depth_cm": flood_depth,
            "rainfall_rate_mmh": rainfall,
            "river_level_meters": river_level,
            "recent_observations": obs[:5],
            "fused_confidence": 0.93 if obs else 0.85,
            "provenance": "FUSED (IoT Sensors + NOAA Radar + SAR Satellite)"
        }

    def apply_zone_override(self, zone_id: str, updates: Dict[str, Any]):
        """Allows live feed simulator to dynamically update zone attributes."""
        if zone_id not in self.zone_overrides:
            self.zone_overrides[zone_id] = {}
        self.zone_overrides[zone_id].update(updates)

    def apply_road_override(self, road_id: str, updates: Dict[str, Any]):
        if road_id not in self.road_overrides:
            self.road_overrides[road_id] = {}
        self.road_overrides[road_id].update(updates)

    def reset_state(self):
        """Resets all overrides and restores baseline observations."""
        self.zone_overrides.clear()
        self.road_overrides.clear()
        self._init_baseline_observations()

    def get_status(self) -> IngestionStatus:
        """Returns overall pipeline health and active connectors."""
        conn_statuses = {name: c.get_status() for name, c in self.connectors.items()}
        return IngestionStatus(
            pipeline_status="OPERATIONAL",
            mode="DEMO / SAFE MODE (Multi-Connector Ingestion)",
            active_connectors_count=len(self.connectors),
            total_observations_ingested=len(self.observations),
            last_ingestion_timestamp=datetime.utcnow().isoformat() + "Z",
            connectors=conn_statuses,
            active_simulator_running=False,
            simulation_step=0,
            total_simulation_steps=5
        )

situation_store = SituationStateStore()
