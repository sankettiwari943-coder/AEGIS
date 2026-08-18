from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.schemas import (
    SimulationRequest, SimulationComparison, MultiScenarioComparisonResponse,
    InterventionItem, ResourceInventory
)
from app.services.simulation.simulation_engine import SimulationEngine, simulation_engine
from app.services.missions.mission_service import mission_service

class SimulationService:
    """
    Simulation Lifecycle & History Orchestrator.
    Manages running scenarios, historical simulation records, and bridging recommended actions to Mission Control.
    """
    def __init__(self, engine: Optional[SimulationEngine] = None):
        self.engine = engine or simulation_engine
        self.history: List[SimulationComparison] = []
        self._init_default_history()

    def _init_default_history(self):
        # Seed initial comparison run
        default_req = SimulationRequest(
            scenario_id="sim-default-demo-01",
            scenario_title="Evacuate Zone 7 + Deploy Delta-2 (Demo Compound)",
            time_horizon_minutes=60,
            perturbations=["road_14_blocked", "hospital_power_lost"],
            interventions=["evacuate_zone_7", "deploy_team_r2"]
        )
        res = self.engine.run_simulation(default_req)
        self.history.append(res)

    def run_simulation(self, request: SimulationRequest) -> SimulationComparison:
        """Executes simulation, caches into history, and returns full comparison."""
        res = self.engine.run_simulation(request)
        # Update or append history
        self.history = [h for h in self.history if h.scenario_id != res.scenario_id]
        self.history.insert(0, res)
        if len(self.history) > 15:
            self.history = self.history[:15]
        return res

    def get_history(self) -> List[SimulationComparison]:
        return self.history

    def get_simulation_by_id(self, scenario_id: str) -> Optional[SimulationComparison]:
        for h in self.history:
            if h.scenario_id == scenario_id:
                return h
        # On-demand fallback
        req = SimulationRequest(
            scenario_id=scenario_id,
            scenario_title=f"Scenario {scenario_id}",
            time_horizon_minutes=60,
            perturbations=["road_14_blocked"],
            interventions=["deploy_team_r2"]
        )
        return self.run_simulation(req)

    def compare_scenarios(
        self,
        time_horizon_minutes: int = 60,
        scenario_requests: Optional[List[SimulationRequest]] = None
    ) -> MultiScenarioComparisonResponse:
        return self.engine.compare_multiple_scenarios(
            scenario_requests=scenario_requests,
            time_horizon_minutes=time_horizon_minutes
        )

    def get_interventions(self) -> List[InterventionItem]:
        return self.engine.interventions.get_all_interventions()

    def get_resource_inventory(self) -> ResourceInventory:
        return self.engine.interventions.get_current_inventory()

    def apply_to_mission_plan(self, scenario_id: str) -> Dict[str, Any]:
        """
        Bridges the recommended intervention strategy from the What-If Simulator
        directly to the Mission Center for human authorization.
        """
        sim = self.get_simulation_by_id(scenario_id)
        target_zone_id = "zone-7"
        team_id = "team-r2"

        if sim and sim.recommended_mission_payload:
            target_zone_id = sim.recommended_mission_payload.get("target_zone_id", "zone-7")
            team_id = sim.recommended_mission_payload.get("team_id", "team-r2")

        # Stage recommendation in Mission Service
        mission_rec = mission_service.optimize_mission(
            target_zone_id=target_zone_id,
            victim_count=12,
            medical_emergencies=3
        )

        return {
            "status": "APPLIED_TO_MISSION_PLAN",
            "scenario_id": scenario_id,
            "mission_id": mission_rec.mission_id,
            "target_zone_id": target_zone_id,
            "team_id": team_id,
            "message": f"Simulated best action applied to Mission Center. Mission {mission_rec.mission_id} staged for operator approval."
        }

    def reset(self):
        """Resets simulation history back to the default demo state."""
        self.history.clear()
        self._init_default_history()

simulation_service = SimulationService()

