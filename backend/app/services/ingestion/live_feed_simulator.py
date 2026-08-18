from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.ingestion.models import (
    LiveFeedStepEvent, DisasterObservation, DataSourceType, HazardType
)
from app.services.ingestion.normalizer import normalizer
from app.services.ingestion.situation_store import situation_store

class LiveFeedSimulator:
    """
    AEGIS Live Incident Feed Simulator.
    Simulates dynamic, evolving disaster conditions across time-horizons,
    driving realistic telemetry updates into the Situation Store and intelligence engines.
    """
    def __init__(self):
        self.is_running: bool = False
        self.current_step: int = 0
        self.total_steps: int = 5
        self.history: List[LiveFeedStepEvent] = []

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "total_events_dispatched": len(self.history),
            "last_step_event": self.history[-1] if self.history else None,
            "mode": "DEMO / LIVE FEED SIMULATOR",
            "active_scenario": "Monsoon Flood — River Basin Deterioration"
        }

    def start(self) -> Dict[str, Any]:
        self.is_running = True
        return self.get_status()

    def stop(self) -> Dict[str, Any]:
        self.is_running = False
        return self.get_status()

    def reset(self) -> Dict[str, Any]:
        self.is_running = False
        self.current_step = 0
        self.history.clear()
        situation_store.reset_state()
        return {
            "status": "RESET_SUCCESSFUL",
            "message": "Live Feed Simulator reset to baseline T+0.",
            "current_step": 0
        }

    def step(self) -> LiveFeedStepEvent:
        """Advances the simulation by one progression step."""
        self.current_step = (self.current_step % self.total_steps) + 1
        event = self._generate_step_event(self.current_step)
        
        # Ingest observations into situation store
        for obs in event.observations:
            situation_store.ingest_observation(obs)
            
        self.history.append(event)
        return event

    def _generate_step_event(self, step: int) -> LiveFeedStepEvent:
        if step == 1:
            # Step 1: Heavy Rainfall Spike
            obs = [
                normalizer.normalize_raw_telemetry(
                    source="Doppler Weather Radar (Station NX-4)",
                    hazard_type="RAINFALL_RATE",
                    value=62.0,
                    unit="mm/h",
                    lat=28.6139,
                    lng=77.2090,
                    zone_id="zone-7",
                    source_type=DataSourceType.SENSOR,
                    confidence=0.96,
                    metadata={"rainfall_spike_pct": "+28%", "mesoscale_convective_system": True}
                )
            ]
            situation_store.apply_zone_override("zone-7", {"rainfall_rate_mmh": 62.0})
            return LiveFeedStepEvent(
                step=1,
                title="Rainfall Intensity Surge (+28%)",
                description="Doppler radar detects severe storm cell over River Bend Lowlands. Rainfall rate reaches 62 mm/h.",
                target_zone="Zone 7 (River Bend)",
                hazard_type=HazardType.RAINFALL_RATE,
                delta_description="Rainfall +28% • Storm Surge Warning",
                observations=obs,
                impacted_engines=["Prediction Engine", "Evidence Engine"]
            )

        elif step == 2:
            # Step 2: River Basin Inundation Rise
            obs = [
                normalizer.normalize_raw_telemetry(
                    source="Basin Hydrological River Gauge #8",
                    hazard_type="RIVER_LEVEL",
                    value=8.45,
                    unit="m",
                    lat=28.6250,
                    lng=77.2150,
                    zone_id="zone-7",
                    source_type=DataSourceType.SENSOR,
                    confidence=0.98,
                    metadata={"crest_increase_cm": "+60cm", "overflow_rate_cumecs": 1400}
                ),
                normalizer.normalize_raw_telemetry(
                    source="Ultrasonic Inundation Sensor #Z7-02",
                    hazard_type="FLOOD_DEPTH",
                    value=185.0,
                    unit="cm",
                    lat=28.6150,
                    lng=77.2110,
                    zone_id="zone-7",
                    source_type=DataSourceType.SENSOR,
                    confidence=0.95,
                    metadata={"flood_depth_cm": 185.0}
                )
            ]
            situation_store.apply_zone_override("zone-7", {
                "river_level_meters": 8.45,
                "current_flood_depth_cm": 185.0
            })
            return LiveFeedStepEvent(
                step=2,
                title="River Crest Spike & Flood Depth Surge",
                description="River gauge records 8.45m level (+60cm rise). Sector flood depth surges to 185cm.",
                target_zone="Zone 7 (River Bend)",
                hazard_type=HazardType.FLOOD_DEPTH,
                delta_description="Flood depth +40cm -> 185cm",
                observations=obs,
                impacted_engines=["Prediction Engine", "Cascading Risk Engine", "Simulation Engine"]
            )

        elif step == 3:
            # Step 3: Road 14 Arterial Submersion
            obs = [
                normalizer.normalize_raw_telemetry(
                    source="Corridor 14 Road Submersion Gauge #RD-14-A",
                    hazard_type="ROAD_BLOCKAGE",
                    value=1.0,
                    unit="blocked",
                    lat=28.6170,
                    lng=77.2130,
                    zone_id="zone-7",
                    source_type=DataSourceType.SENSOR,
                    confidence=0.99,
                    metadata={"passability_pct": 18, "status": "BLOCKED", "critical_hospital_route": True}
                )
            ]
            situation_store.apply_road_override("road-14", {
                "status": "blocked",
                "passability_percent": 18
            })
            return LiveFeedStepEvent(
                step=3,
                title="Corridor 14 Arterial Route Cutoff",
                description="Corridor 14 approach road fully submerged under 75cm rapid current. Vehicular access severed.",
                target_zone="Zone 7 (River Bend)",
                hazard_type=HazardType.ROAD_BLOCKAGE,
                delta_description="Road 14: OPEN -> BLOCKED (18% Passability)",
                observations=obs,
                impacted_engines=["Cascading Risk Engine", "Rescue Mission Optimizer"]
            )

        elif step == 4:
            # Step 4: Telecom Tower Failure & Silent Crisis
            obs = [
                normalizer.normalize_raw_telemetry(
                    source="Cellular Tower Delta-4 Telemetry",
                    hazard_type="TELECOM_OUTAGE",
                    value=95.0,
                    unit="%_loss",
                    lat=28.5810,
                    lng=77.1890,
                    zone_id="zone-4",
                    source_type=DataSourceType.SENSOR,
                    confidence=0.99,
                    metadata={"connected_devices": 0, "silent_crisis_alert": True}
                )
            ]
            return LiveFeedStepEvent(
                step=4,
                title="Cellular Tower Outage & Silent Risk Escalation",
                description="Cellular Tower Delta-4 backup battery depleted. 2,300 residents enter complete communications blackout.",
                target_zone="Zone 4 (Riverside Slums)",
                hazard_type=HazardType.TELECOM_OUTAGE,
                delta_description="Telecom Outage 95% • Zero SOS Anomaly",
                observations=obs,
                impacted_engines=["Silent Risk Engine", "Evidence Engine", "AI Orchestrator"]
            )

        else:
            # Step 5: Substation #2 Critical Threat
            obs = [
                normalizer.normalize_raw_telemetry(
                    source="Substation #2 SCADA Intrusion Detector",
                    hazard_type="POWER_OUTAGE",
                    value=1.0,
                    unit="warning",
                    lat=28.6220,
                    lng=77.2180,
                    zone_id="zone-7",
                    source_type=DataSourceType.SENSOR,
                    confidence=0.97,
                    metadata={"water_over_bund_cm": 12.0, "cascade_pumps_impacted": ["Pump #1", "Pump #2"]}
                )
            ]
            return LiveFeedStepEvent(
                step=5,
                title="Substation #2 Flood Intrusion Alert",
                description="Flood waters breach flood barrier at Substation #2. Automatic trip threatens Basin Drainage Pumps.",
                target_zone="Zone 7 (River Bend)",
                hazard_type=HazardType.POWER_OUTAGE,
                delta_description="Substation #2 Barrier Breached • Multi-Hop Cascade",
                observations=obs,
                impacted_engines=["Cascading Risk Engine", "AI Disaster Orchestrator", "Simulation Engine"]
            )

live_feed_simulator = LiveFeedSimulator()
