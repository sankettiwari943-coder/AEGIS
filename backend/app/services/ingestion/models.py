from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime, timezone

class DataSourceType(str, Enum):
    LIVE = "LIVE"
    SIMULATED = "SIMULATED"
    SENSOR = "SENSOR"
    OFFICIAL = "OFFICIAL"
    CIVILIAN = "CIVILIAN"
    AI_INFERRED = "AI-INFERRED"
    RAG = "RAG"
    DEMO_CV = "DEMO CV"


class HazardType(str, Enum):
    FLOOD_DEPTH = "FLOOD_DEPTH"
    RAINFALL_RATE = "RAINFALL_RATE"
    RIVER_LEVEL = "RIVER_LEVEL"
    ROAD_BLOCKAGE = "ROAD_BLOCKAGE"
    TELECOM_OUTAGE = "TELECOM_OUTAGE"
    POWER_OUTAGE = "POWER_OUTAGE"
    DAM_OVERFLOW = "DAM_OVERFLOW"
    STRUCTURAL_DAMAGE = "STRUCTURAL_DAMAGE"
    CIVILIAN_SOS = "CIVILIAN_SOS"

class DisasterObservation(BaseModel):
    """
    Unified normalized schema for multi-source disaster telemetry and hazard signals.
    """
    id: str = Field(..., description="Unique observation identifier")
    source: str = Field(..., description="Name of source provider, sensor id, or agency")
    source_type: DataSourceType = Field(default=DataSourceType.SIMULATED, description="Provenance classification")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")

    zone_id: Optional[str] = Field(None, description="Matched AEGIS zone identifier")
    hazard_type: HazardType = Field(..., description="Hazard classification category")
    value: float = Field(..., description="Measured quantitative value")
    unit: str = Field(..., description="Measurement unit (e.g. 'cm', 'mm/h', 'm', '%', 'count')")
    severity: float = Field(default=0.5, ge=0.0, le=1.0, description="Normalized severity score 0.0-1.0")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="Data trust/confidence metric 0.0-1.0")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary provider-specific metadata")

class IngestionStatus(BaseModel):
    """
    Operational status of the ingestion pipeline and connected adapters.
    """
    pipeline_status: str = "OPERATIONAL"
    mode: str = "DEMO / SAFE MODE"
    active_connectors_count: int = 5
    total_observations_ingested: int = 0
    last_ingestion_timestamp: str = ""
    connectors: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    active_simulator_running: bool = False
    simulation_step: int = 0
    total_simulation_steps: int = 5

class LiveFeedStepEvent(BaseModel):
    """
    Telemetry event generated during live feed simulation progression.
    """
    step: int
    title: str
    description: str
    target_zone: str
    hazard_type: HazardType
    delta_description: str
    observations: List[DisasterObservation] = Field(default_factory=list)
    impacted_engines: List[str] = Field(default_factory=list)
