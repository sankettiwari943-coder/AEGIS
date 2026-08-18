from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.schemas import (
    SimulationRequest, SimulationComparison, MultiScenarioComparisonResponse,
    MultiScenarioRankingItem
)
from app.services.simulation.scenario_builder import ScenarioBuilder, scenario_builder
from app.services.simulation.scenario_runner import ScenarioRunner, scenario_runner
from app.services.simulation.scenario_comparator import ScenarioComparator, scenario_comparator
from app.services.simulation.intervention_engine import InterventionEngine, intervention_engine

class SimulationEngine:
    """
    AEGIS What-If Disaster Simulation Engine.
    Coordinates scenario building, state execution, baseline comparison, and multi-scenario ranking.
    """
    def __init__(
        self,
        builder: Optional[ScenarioBuilder] = None,
        runner: Optional[ScenarioRunner] = None,
        comparator: Optional[ScenarioComparator] = None,
        interventions: Optional[InterventionEngine] = None
    ):
        self.builder = builder or scenario_builder
        self.runner = runner or scenario_runner
        self.comparator = comparator or scenario_comparator
        self.interventions = interventions or intervention_engine

    def run_simulation(self, request: SimulationRequest) -> SimulationComparison:
        """Runs a single scenario simulation comparison against the baseline."""
        return self.comparator.compare_scenario(request)

    def compare_multiple_scenarios(
        self,
        scenario_requests: Optional[List[SimulationRequest]] = None,
        time_horizon_minutes: int = 60
    ) -> MultiScenarioComparisonResponse:
        """
        Runs and ranks multiple scenarios (e.g. Scenarios A, B, C, D) across risk reduction,
        resource cost, efficiency score, and mission impact.
        """
        scenarios = scenario_requests or self.builder.get_standard_comparison_scenarios(time_horizon_minutes)
        ranked_items: List[MultiScenarioRankingItem] = []

        for idx, req in enumerate(scenarios):
            req.time_horizon_minutes = time_horizon_minutes
            comp = self.run_simulation(req)
            
            mission_impact = 98 if ("deploy_team_r2" in req.interventions or "deploy_team_r4" in req.interventions) else (85 if req.interventions else 20)
            
            item = MultiScenarioRankingItem(
                scenario_id=comp.scenario_id,
                title=comp.scenario_title,
                interventions=comp.interventions_active,
                overall_risk=comp.scenario_overall_risk,
                risk_reduction_points=comp.net_risk_reduction_points,
                risk_reduction_percent=comp.net_risk_reduction_percent,
                resource_cost=comp.resource_cost,
                efficiency_score=comp.efficiency_score,
                mission_impact=mission_impact,
                cascade_risk=comp.scenario_overall_risk,
                confidence_percent=comp.confidence_percent,
                rank=0
            )
            ranked_items.append(item)

        # Sort descending by risk reduction points, then efficiency score
        ranked_items.sort(key=lambda s: (s.risk_reduction_points, s.efficiency_score), reverse=True)
        for i, item in enumerate(ranked_items):
            item.rank = i + 1

        best = ranked_items[0] if ranked_items else None
        narrative = (
            f"Scenario Comparison across {len(ranked_items)} strategies indicates that '{best.title if best else 'Compound Strategy'}' "
            f"delivers the highest estimated survival impact, achieving a {best.risk_reduction_points if best else 0}-point risk reduction "
            f"with an efficiency rating of {best.efficiency_score if best else 0} pts/asset."
        )

        return MultiScenarioComparisonResponse(
            time_horizon_minutes=time_horizon_minutes,
            scenarios=ranked_items,
            best_scenario=best,
            recommendation_narrative=narrative,
            timestamp=datetime.now().isoformat()
        )

simulation_engine = SimulationEngine()
