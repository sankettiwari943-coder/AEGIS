from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class DetectedObject(BaseModel):
    id: str
    label: str # "submerged_vehicle", "damaged_roof", "flooded_road", "trapped_individual", "debris_blockage"
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: List[float] = Field(..., description="[ymin, xmin, ymax, xmax] normalized 0-1")
    geo_coordinates: Optional[List[float]] = Field(None, description="[lng, lat]")
    severity: str = "HIGH"

class GeoDamagePolygon(BaseModel):
    id: str
    label: str # "flood_inundation_mask", "critical_debris_field"
    confidence: float
    coordinates: List[List[float]] # [[lng, lat], ...]

class CVAnalysisRequest(BaseModel):
    scan_id: Optional[str] = None
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    target_zone_id: Optional[str] = "zone-7"
    sensor_modality: Optional[str] = "DRONE_OPTICAL" # "DRONE_OPTICAL", "SATELLITE_SAR", "HELICOPTER_FLIR"

class CVAnalysisResult(BaseModel):
    scan_id: str
    title: str
    target_zone_id: str
    target_zone_name: str
    sensor_modality: str
    analysis_label: str = "DEMO CV ANALYSIS"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    flood_extent_percent: int
    damaged_structures_count: int
    blocked_roads_count: int
    trapped_clusters_count: int
    detections: List[DetectedObject] = Field(default_factory=list)
    damage_polygons: List[GeoDamagePolygon] = Field(default_factory=list)
    overall_confidence: float = 0.92
    source_image_name: str
    operational_takeaway: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
