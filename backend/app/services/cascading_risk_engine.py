"""
Cascading Risk Engine Compatibility Adapter
Wraps the modular cascading risk service while maintaining backward compatibility.
"""
from typing import List, Optional
from app.models.schemas import ZoneCascadingRisk, Zone
from app.services.cascading.cascade_service import cascade_service, CascadeService
from app.services.cascading.cascade_engine import cascade_engine, CascadeEngine

class CascadingRiskEngine:
    """
    Backward-compatible adapter for legacy CascadingRiskEngine callers.
    """
    def __init__(self):
        self.service = cascade_service
        self.engine = cascade_engine
        self.graph = cascade_engine.dep_graph.graph

    def analyze_zone(self, zone: Zone) -> ZoneCascadingRisk:
        risks = self.service.get_all_cascading_risks([zone])
        return risks[0]

    def analyze_all_zones(self, zones: Optional[List[Zone]] = None) -> List[ZoneCascadingRisk]:
        return self.service.get_all_cascading_risks(zones)

cascading_risk_engine = CascadingRiskEngine()
