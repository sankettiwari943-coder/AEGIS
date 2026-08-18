from typing import List, Dict, Any, Optional
from app.models.schemas import SimulationRequest

class ScenarioBuilder:
    """
    Scenario Builder for What-If Disaster Simulation.
    Creates structured Baseline (Do Nothing), Single-Intervention, and Compound Strategies across 30m, 60m, 3h horizons.
    """
    def __init__(self):
        pass

    def build_baseline_scenario(self, time_horizon_minutes: int = 60) -> SimulationRequest:
        """Constructs the reference 'DO NOTHING' baseline scenario."""
        return SimulationRequest(
            scenario_id=f"scenario-baseline-{time_horizon_minutes}m",
            scenario_title="DO NOTHING (Unmitigated Baseline Projection)",
            time_horizon=time_horizon_minutes,
            time_horizon_minutes=time_horizon_minutes,
            base_scenario="do_nothing",
            perturbations=["road_14_blocked", "hospital_power_lost"],
            interventions=[]
        )

    def build_custom_scenario(
        self,
        title: str,
        perturbations: List[str],
        interventions: List[str],
        time_horizon_minutes: int = 60,
        scenario_id: Optional[str] = None
    ) -> SimulationRequest:
        """Constructs a custom scenario from user selections."""
        return SimulationRequest(
            scenario_id=scenario_id or f"scenario-custom-{time_horizon_minutes}m",
            scenario_title=title or "Custom What-If Scenario",
            time_horizon=time_horizon_minutes,
            time_horizon_minutes=time_horizon_minutes,
            base_scenario="do_nothing",
            perturbations=perturbations,
            interventions=interventions
        )

    def get_standard_comparison_scenarios(self, time_horizon_minutes: int = 60) -> List[SimulationRequest]:
        """
        Returns the standard 4 comparison scenarios for the signature AEGIS demo moment:
        Scenario A: Do Nothing
        Scenario B: Evacuate Zone 7
        Scenario C: Deploy Team R2
        Scenario D: Evacuate Zone 7 + Deploy Team R2
        """
        return [
            SimulationRequest(
                scenario_id="scenario-a-do-nothing",
                scenario_title="Scenario A: Do Nothing (Baseline)",
                time_horizon=time_horizon_minutes,
                time_horizon_minutes=time_horizon_minutes,
                base_scenario="do_nothing",
                perturbations=["road_14_blocked", "hospital_power_lost"],
                interventions=[]
            ),
            SimulationRequest(
                scenario_id="scenario-b-evacuate-z7",
                scenario_title="Scenario B: Evacuate Zone 7",
                time_horizon=time_horizon_minutes,
                time_horizon_minutes=time_horizon_minutes,
                base_scenario="do_nothing",
                perturbations=["road_14_blocked", "hospital_power_lost"],
                interventions=["evacuate_zone_7"]
            ),
            SimulationRequest(
                scenario_id="scenario-c-deploy-r2",
                scenario_title="Scenario C: Deploy Heavy Unit Delta-2",
                time_horizon=time_horizon_minutes,
                time_horizon_minutes=time_horizon_minutes,
                base_scenario="do_nothing",
                perturbations=["road_14_blocked", "hospital_power_lost"],
                interventions=["deploy_team_r2"]
            ),
            SimulationRequest(
                scenario_id="scenario-d-compound-optimal",
                scenario_title="Scenario D: Evacuate Zone 7 + Deploy Delta-2",
                time_horizon=time_horizon_minutes,
                time_horizon_minutes=time_horizon_minutes,
                base_scenario="do_nothing",
                perturbations=["road_14_blocked", "hospital_power_lost"],
                interventions=["evacuate_zone_7", "deploy_team_r2"]
            )
        ]

scenario_builder = ScenarioBuilder()
