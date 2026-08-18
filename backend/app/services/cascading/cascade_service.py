"""
Cascading Risk Service
Orchestrates cascading intelligence across all zones, infrastructure components,
and API endpoints.
"""
from typing import List, Optional, Dict, Any
from app.models.schemas import (
    Zone, Infrastructure, RoadSegment,
    ZoneCascadingRisk, ZoneCascadeDetailResponse, ZoneCascadeGraphResponse,
    CascadeChain, CascadeAlert
)
from app.data.flood_dataset import ZONES_DATA, INFRASTRUCTURE_DATA, ROADS_DATA
from app.services.cascading.cascade_engine import cascade_engine

class CascadeService:
    """
    High-level orchestrator service for cascading risk intelligence.
    """
    def __init__(
        self,
        zones: Optional[List[Zone]] = None,
        infrastructure: Optional[List[Infrastructure]] = None,
        roads: Optional[List[RoadSegment]] = None
    ):
        self.zones = zones or ZONES_DATA
        self.infrastructure = infrastructure or INFRASTRUCTURE_DATA
        self.roads = roads or ROADS_DATA
        self.engine = cascade_engine

    def _find_zone(self, zone_id: str) -> Optional[Zone]:
        for z in self.zones:
            if z.id == zone_id or z.code.lower() == zone_id.lower():
                return z
        return None

    def get_all_cascading_risks(self, zones: Optional[List[Zone]] = None) -> List[ZoneCascadingRisk]:
        """
        Returns backward-compatible ZoneCascadingRisk models for all zones.
        """
        target_zones = zones or self.zones
        results = []
        for z in target_zones:
            sec_risks, _ = self.engine.evaluate_zone_secondary_risks(z, self.infrastructure, self.roads)
            detail = self.engine.analyze_zone(z, self.infrastructure, self.roads)
            critical_chain = [step.node_name for step in detail.top_chains[0].steps] if detail.top_chains else [
                f"Rainfall ({z.rainfall_rate_mmh} mm/h)",
                f"Surface Flooding ({z.current_flood_depth_cm} cm)",
                f"Road Degradation ({z.road_accessibility_percent}%)",
                f"Hospital Delay ({z.hospital_accessibility_percent}%)"
            ]

            results.append(ZoneCascadingRisk(
                zone_id=z.id,
                zone_name=z.name,
                primary_flood_risk=z.primary_risk_score,
                power_failure_risk=sec_risks.get("power_failure", int(z.primary_risk_score * 0.85)),
                medical_access_risk=sec_risks.get("hospital_accessibility", int(z.primary_risk_score * 0.92)),
                water_contamination_risk=sec_risks.get("water_contamination", int(z.primary_risk_score * 0.75)),
                communication_loss_risk=sec_risks.get("communication_loss", 20),
                road_isolation_risk=sec_risks.get("road_isolation", int((100 - z.road_accessibility_percent) * 0.95)),
                combined_cascading_score=detail.cascading_risk,
                critical_chain=critical_chain,
                narrative_explanation=detail.narrative
            ))
        return results

    def get_all_cascade_details(self, zones: Optional[List[Zone]] = None) -> List[ZoneCascadeDetailResponse]:
        """
        Returns full detailed cascade assessment for all zones.
        """
        target_zones = zones or self.zones
        return [self.engine.analyze_zone(z, self.infrastructure, self.roads) for z in target_zones]

    def get_zone_cascade_detail(self, zone_id: str) -> Optional[ZoneCascadeDetailResponse]:
        """
        Returns detailed cascade assessment for a specific zone.
        """
        zone = self._find_zone(zone_id)
        if not zone:
            return None
        return self.engine.analyze_zone(zone, self.infrastructure, self.roads)

    def get_zone_cascade_graph(self, zone_id: str) -> Optional[ZoneCascadeGraphResponse]:
        """
        Returns interactive directed graph topology and node states for a specific zone.
        """
        zone = self._find_zone(zone_id)
        if not zone:
            return None
        sec_risks, _ = self.engine.evaluate_zone_secondary_risks(zone, self.infrastructure, self.roads)
        return self.engine.get_zone_graph(zone, sec_risks)

    def get_top_cascading_threats(self, limit: int = 6) -> List[CascadeChain]:
        """
        Returns top ranked cascading threat chains across all zones.
        """
        all_chains: List[CascadeChain] = []
        for z in self.zones:
            sec_risks, _ = self.engine.evaluate_zone_secondary_risks(z, self.infrastructure, self.roads)
            top_chains = self.engine.build_zone_top_chains(z, sec_risks)
            all_chains.extend(top_chains)

        # Sort by priority score descending
        all_chains.sort(key=lambda c: c.priority_score, reverse=True)
        return all_chains[:limit]

    def get_all_cascade_alerts(self) -> List[CascadeAlert]:
        """
        Returns all active operational cascade alerts across the system.
        """
        all_alerts: List[CascadeAlert] = []
        for z in self.zones:
            sec_risks, _ = self.engine.evaluate_zone_secondary_risks(z, self.infrastructure, self.roads)
            alerts = self.engine.generate_zone_alerts(z, sec_risks)
            all_alerts.extend(alerts)
        
        # Sort by secondary risk score descending
        all_alerts.sort(key=lambda a: a.secondary_risk_score, reverse=True)
        return all_alerts

cascade_service = CascadeService()
