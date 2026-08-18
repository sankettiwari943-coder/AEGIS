import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from app.services.ingestion.models import DisasterObservation, DataSourceType, HazardType

class ObservationNormalizer:
    """
    Validates, calibrates, and normalizes raw telemetry feeds into the standard
    DisasterObservation schema. Handles coordinate snapping, unit conversion, and bounding.
    """

    @staticmethod
    def normalize_raw_telemetry(
        source: str,
        hazard_type: str,
        value: float,
        unit: str,
        lat: float,
        lng: float,
        zone_id: Optional[str] = None,
        source_type: DataSourceType = DataSourceType.SIMULATED,
        confidence: float = 0.90,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DisasterObservation:
        """
        Converts raw provider telemetry into a validated DisasterObservation.
        """
        # Validate or snap hazard type enum
        try:
            h_type = HazardType(hazard_type.upper())
        except ValueError:
            h_type = HazardType.FLOOD_DEPTH

        # Standardize severity based on hazard type and value
        severity = ObservationNormalizer._calculate_severity(h_type, value, unit)

        return DisasterObservation(
            id=f"obs-{uuid.uuid4().hex[:8]}",
            source=source,
            source_type=source_type,
            timestamp=datetime.utcnow().isoformat() + "Z",
            latitude=round(lat, 5),
            longitude=round(lng, 5),
            zone_id=zone_id,
            hazard_type=h_type,
            value=round(value, 2),
            unit=unit,
            severity=round(severity, 2),
            confidence=round(max(0.1, min(1.0, confidence)), 2),
            metadata=metadata or {}
        )

    @staticmethod
    def _calculate_severity(hazard_type: HazardType, value: float, unit: str) -> float:
        """Heuristic severity normalization between 0.0 and 1.0."""
        if hazard_type == HazardType.FLOOD_DEPTH:
            # Assuming cm
            cm = value if unit.lower() == "cm" else value * 100.0 if unit.lower() == "m" else value
            return min(1.0, max(0.0, cm / 250.0))
        elif hazard_type == HazardType.RAINFALL_RATE:
            # mm/h
            return min(1.0, max(0.0, value / 120.0))
        elif hazard_type == HazardType.RIVER_LEVEL:
            # meters
            return min(1.0, max(0.0, (value - 2.0) / 8.0))
        elif hazard_type == HazardType.TELECOM_OUTAGE or hazard_type == HazardType.POWER_OUTAGE:
            # % outage or availability
            if unit == "%_loss" or unit == "%":
                return min(1.0, max(0.0, value / 100.0))
            return 0.5
        elif hazard_type == HazardType.ROAD_BLOCKAGE:
            # 1.0 if blocked, 0.0 if open
            return 1.0 if value >= 1.0 else 0.0
        return 0.5

normalizer = ObservationNormalizer()
