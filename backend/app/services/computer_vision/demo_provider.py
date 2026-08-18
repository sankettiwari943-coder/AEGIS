from typing import List, Dict, Any, Optional
from datetime import datetime
from app.services.computer_vision.cv_models import (
    CVAnalysisResult, DetectedObject, GeoDamagePolygon, CVAnalysisRequest
)

DEMO_SCANS_CATALOG: Dict[str, Dict[str, Any]] = {
    "SCAN-Z07-DRONE-01": {
        "scan_id": "SCAN-Z07-DRONE-01",
        "title": "Zone 7 Corridor 14 Arterial Bridge Drone Recon Scan",
        "target_zone_id": "zone-7",
        "target_zone_name": "Zone 7 — River Bend Lowlands",
        "sensor_modality": "DRONE_OPTICAL_RGB",
        "source_image_name": "corridor14_aerial_ortho_t0.webp",
        "flood_extent_percent": 78,
        "damaged_structures_count": 14,
        "blocked_roads_count": 2,
        "trapped_clusters_count": 3,
        "overall_confidence": 0.94,
        "operational_takeaway": "Corridor 14 bridge approach is submerged under 70cm water. 3 civilian vehicle clusters stranded on elevated roadway berm.",
        "detections": [
            {
                "id": "det-01",
                "label": "submerged_vehicle",
                "confidence": 0.96,
                "bbox": [0.42, 0.35, 0.58, 0.48],
                "geo_coordinates": [77.2125, 28.6162],
                "severity": "HIGH"
            },
            {
                "id": "det-02",
                "label": "flooded_road",
                "confidence": 0.98,
                "bbox": [0.30, 0.15, 0.75, 0.85],
                "geo_coordinates": [77.2130, 28.6170],
                "severity": "CRITICAL"
            },
            {
                "id": "det-03",
                "label": "damaged_roof",
                "confidence": 0.88,
                "bbox": [0.65, 0.70, 0.82, 0.88],
                "geo_coordinates": [77.2140, 28.6150],
                "severity": "MODERATE"
            },
            {
                "id": "det-04",
                "label": "trapped_individual",
                "confidence": 0.91,
                "bbox": [0.45, 0.38, 0.52, 0.44],
                "geo_coordinates": [77.2127, 28.6163],
                "severity": "CRITICAL"
            }
        ],
        "damage_polygons": [
            {
                "id": "poly-01",
                "label": "flood_inundation_mask",
                "confidence": 0.95,
                "coordinates": [
                    [77.208, 28.614],
                    [77.215, 28.618],
                    [77.218, 28.612],
                    [77.210, 28.610]
                ]
            }
        ],
        "metadata": {
            "altitude_m": 120.0,
            "ground_sampling_distance_cm": 2.5,
            "flight_duration_min": 18,
            "operator": "Tactical Drone Unit Echo-2"
        }
    },
    "SCAN-Z04-SAR-01": {
        "scan_id": "SCAN-Z04-SAR-01",
        "title": "Zone 4 Riverside Informal Settlement SAR Inundation Scan",
        "target_zone_id": "zone-4",
        "target_zone_name": "Zone 4 — Riverside Slums",
        "sensor_modality": "SATELLITE_SAR",
        "source_image_name": "sentinel1_sar_zone4_flood.webp",
        "flood_extent_percent": 65,
        "damaged_structures_count": 42,
        "blocked_roads_count": 4,
        "trapped_clusters_count": 8,
        "overall_confidence": 0.89,
        "operational_takeaway": "Severe structural inundation detected despite ZERO cellular SOS calls. Confirms Silent Crisis conditions.",
        "detections": [
            {
                "id": "det-11",
                "label": "damaged_roof",
                "confidence": 0.92,
                "bbox": [0.22, 0.30, 0.45, 0.55],
                "geo_coordinates": [77.1910, 28.5815],
                "severity": "CRITICAL"
            },
            {
                "id": "det-12",
                "label": "flooded_road",
                "confidence": 0.94,
                "bbox": [0.10, 0.10, 0.85, 0.40],
                "geo_coordinates": [77.1900, 28.5800],
                "severity": "HIGH"
            }
        ],
        "damage_polygons": [
            {
                "id": "poly-02",
                "label": "flood_inundation_mask",
                "confidence": 0.91,
                "coordinates": [
                    [77.185, 28.578],
                    [77.195, 28.585],
                    [77.198, 28.580],
                    [77.188, 28.575]
                ]
            }
        ],
        "metadata": {
            "orbit": "Descending 144",
            "band": "C-Band Synthetic Aperture",
            "resolution_m": 10.0,
            "operator": "ESA Copernicus / Space Agency Relay"
        }
    },
    "SCAN-Z02-AERIAL-01": {
        "scan_id": "SCAN-Z02-AERIAL-01",
        "title": "Zone 2 District Hospital Corridor Aerial Recon Scan",
        "target_zone_id": "zone-2",
        "target_zone_name": "Zone 2 — Memorial Hospital Corridor",
        "sensor_modality": "HELICOPTER_FLIR",
        "source_image_name": "hospital_flir_thermal_recon.webp",
        "flood_extent_percent": 32,
        "damaged_structures_count": 3,
        "blocked_roads_count": 1,
        "trapped_clusters_count": 0,
        "overall_confidence": 0.96,
        "operational_takeaway": "Hospital main entrance clear of standing water. Generator yard flood bund holds at 45cm margin.",
        "detections": [
            {
                "id": "det-21",
                "label": "debris_blockage",
                "confidence": 0.89,
                "bbox": [0.55, 0.40, 0.70, 0.60],
                "geo_coordinates": [77.2050, 28.6050],
                "severity": "MODERATE"
            }
        ],
        "damage_polygons": [],
        "metadata": {
            "thermal_sensor": "FLIR Vue Pro 640",
            "operator": "Air Rescue Wing Falcon-1"
        }
    }
}

class DemoCVProvider:
    """
    Deterministic Computer Vision provider.
    Delivers model-agnostic bounding boxes, flood masks, and damage diagnostics
    for emergency management without external GPU requirements.
    """
    def __init__(self):
        pass

    def analyze(self, req: CVAnalysisRequest) -> CVAnalysisResult:
        # Match scan by ID or zone
        scan_id = req.scan_id
        if not scan_id or scan_id not in DEMO_SCANS_CATALOG:
            # Match by zone
            target_zone = req.target_zone_id or "zone-7"
            matched_key = next(
                (k for k, v in DEMO_SCANS_CATALOG.items() if v["target_zone_id"] == target_zone),
                "SCAN-Z07-DRONE-01"
            )
            data = DEMO_SCANS_CATALOG[matched_key]
        else:
            data = DEMO_SCANS_CATALOG[scan_id]

        detections = [DetectedObject(**d) for d in data["detections"]]
        polygons = [GeoDamagePolygon(**p) for p in data["damage_polygons"]]

        return CVAnalysisResult(
            scan_id=data["scan_id"],
            title=data["title"],
            target_zone_id=data["target_zone_id"],
            target_zone_name=data["target_zone_name"],
            sensor_modality=data["sensor_modality"],
            analysis_label="DEMO CV ANALYSIS",
            timestamp=datetime.utcnow().isoformat() + "Z",
            flood_extent_percent=data["flood_extent_percent"],
            damaged_structures_count=data["damaged_structures_count"],
            blocked_roads_count=data["blocked_roads_count"],
            trapped_clusters_count=data["trapped_clusters_count"],
            detections=detections,
            damage_polygons=polygons,
            overall_confidence=data["overall_confidence"],
            source_image_name=data["source_image_name"],
            operational_takeaway=data["operational_takeaway"],
            metadata=data["metadata"]
        )

    def list_scans(self) -> List[Dict[str, Any]]:
        return [
            {
                "scan_id": v["scan_id"],
                "title": v["title"],
                "target_zone_id": v["target_zone_id"],
                "target_zone_name": v["target_zone_name"],
                "sensor_modality": v["sensor_modality"],
                "flood_extent_percent": v["flood_extent_percent"],
                "overall_confidence": v["overall_confidence"]
            }
            for v in DEMO_SCANS_CATALOG.values()
        ]

demo_cv_provider = DemoCVProvider()
