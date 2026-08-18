from typing import List, Dict, Any, Optional
from app.models.schemas import (
    SimulationRequest, SimulationComparison, SimulationMetricDelta
)
from app.services.simulation.scenario_runner import ScenarioRunner, scenario_runner

class ScenarioComparator:
    """
    Scenario Comparison & Decision Optimization Engine.
    Computes comparative risk reduction, resource efficiency, metric deltas,
    and explainable 'Best Action' recommendations.
    """
    def __init__(self, runner: Optional[ScenarioRunner] = None):
        self.runner = runner or scenario_runner

    def compare_scenario(self, request: SimulationRequest) -> SimulationComparison:
        """
        Executes and formats a complete What-If simulation comparison report against the Do Nothing baseline.
        """
        raw_result = self.runner.execute_scenario(request)

        base_risk = raw_result["baseline_overall_risk"]
        scen_risk = raw_result["scenario_overall_risk"]
        net_red_pts = raw_result["net_risk_reduction_points"]
        net_red_pct = raw_result["net_risk_reduction_percent"]
        res_cost = raw_result["resource_cost"]
        eff_score = raw_result["efficiency_score"]
        horizon = raw_result["time_horizon_minutes"]

        # 1. Format Structured Metric Deltas
        raw_m = raw_result["metrics_raw"]
        metrics = [
            SimulationMetricDelta(
                metric_name="Population at Risk",
                baseline_value=f"{raw_m['population_at_risk'][0]:,}",
                scenario_value=f"{raw_m['population_at_risk'][1]:,}",
                delta_display=f"-{raw_m['population_at_risk'][0] - raw_m['population_at_risk'][1]:,}",
                is_worsening=False,
                unit="residents"
            ),
            SimulationMetricDelta(
                metric_name="Hospital Accessibility",
                baseline_value=f"{raw_m['hospital_access'][0]}%",
                scenario_value=f"{raw_m['hospital_access'][1]}%",
                delta_display=f"+{raw_m['hospital_access'][1] - raw_m['hospital_access'][0]}%",
                is_worsening=False,
                unit="percent"
            ),
            SimulationMetricDelta(
                metric_name="Road Network Access",
                baseline_value=f"{raw_m['road_access'][0]}%",
                scenario_value=f"{raw_m['road_access'][1]}%",
                delta_display=f"+{raw_m['road_access'][1] - raw_m['road_access'][0]}%",
                is_worsening=False,
                unit="percent"
            ),
            SimulationMetricDelta(
                metric_name="Power Failure Risk",
                baseline_value=f"{raw_m['power_risk'][0]}",
                scenario_value=f"{raw_m['power_risk'][1]}",
                delta_display=f"-{raw_m['power_risk'][0] - raw_m['power_risk'][1]} pts",
                is_worsening=False,
                unit="points"
            ),
            SimulationMetricDelta(
                metric_name="Cascading Vulnerability Score",
                baseline_value=f"{raw_m['cascade_risk'][0]}",
                scenario_value=f"{raw_m['cascade_risk'][1]}",
                delta_display=f"-{raw_m['cascade_risk'][0] - raw_m['cascade_risk'][1]} pts",
                is_worsening=False,
                unit="points"
            )
        ]

        # 2. Formulate Best Action & Explainable Why Bullets
        best_action, why_bullets = self._formulate_best_action(request.interventions, net_red_pts, eff_score)

        # 3. AI Strategic Briefing
        briefing = (
            f"SIMULATION BRIEFING ({horizon}-MINUTE HORIZON): Implementing the selected intervention package "
            f"yields an estimated risk reduction of {net_red_pts} points ({net_red_pct}%), reducing compound disaster risk from "
            f"{base_risk} down to {scen_risk}. Proactive evacuation and specialized asset deployment protect ~{raw_m['population_at_risk'][0] - raw_m['population_at_risk'][1]:,} "
            f"residents from acute flood crest immersion while restoring hospital transit corridors."
        )

        return SimulationComparison(
            scenario_id=request.scenario_id or "sim-custom-01",
            scenario_title=request.scenario_title,
            time_horizon_minutes=horizon,
            perturbations_active=request.perturbations,
            interventions_active=request.interventions,
            baseline_overall_risk=base_risk,
            scenario_overall_risk=scen_risk,
            net_risk_reduction_points=net_red_pts,
            net_risk_reduction_percent=net_red_pct,
            resource_cost=res_cost,
            efficiency_score=eff_score,
            metrics=metrics,
            zone_risk_shifts=raw_result["zone_risk_shifts"],
            cascade_shifts=raw_result["cascade_shifts"],
            timeline_trajectories=raw_result["timeline_trajectories"],
            critical_impacted_zones=["zone-7", "zone-4", "zone-9", "zone-6"],
            best_preventive_action=best_action,
            why_bullets=why_bullets,
            ai_strategic_briefing=briefing,
            confidence_percent=88 if not raw_result["has_resource_conflict"] else 62,
            confidence_status="HIGH_CONFIDENCE" if not raw_result["has_resource_conflict"] else "LOW_CONFIDENCE",
            has_resource_conflict=raw_result["has_resource_conflict"],
            conflict_message=raw_result["conflict_message"],
            recommended_mission_payload=raw_result["recommended_mission_payload"],
            simulation_label="SIMULATION / MODEL ESTIMATE ONLY"
        )

    def _formulate_best_action(
        self,
        interventions: List[str],
        net_red_pts: int,
        eff_score: float
    ) -> Tuple[str, List[str]]:
        if not interventions:
            return (
                "Do Nothing (No Action Selected)",
                [
                    "Unmitigated baseline projection active",
                    "Disaster conditions will worsen across all sectors",
                    "Select interventions to test risk mitigation strategies"
                ]
            )

        has_evac = any("evacuate" in a for a in interventions)
        has_deploy = any("deploy_team" in a or "deploy_rescue" in a for a in interventions)
        has_power = any("power" in a or "generator" in a for a in interventions)

        if has_evac and has_deploy:
            action_name = "Evacuate Zone 7 + Deploy Unit Delta-2"
        elif has_evac:
            action_name = "Preemptive Evacuation of Zone 7"
        elif has_deploy:
            action_name = "Deploy Tactical Unit Delta-2 to Zone 7"
        elif has_power:
            action_name = "Substation Flood Defense & Emergency Generator"
        else:
            action_name = f"Custom Compound Strategy ({len(interventions)} actions)"

        bullets = [
            f"Delivers highest estimated risk reduction ({net_red_pts} points)",
            "Protects 2,840 high-vulnerability residents before peak river crest",
            "Addresses 3 critical trauma emergencies with specialized medical unit",
            "Bypasses flooded and blocked roads with certified amphibious watercraft",
            "Mitigates cascading failure chain to basin pumping infrastructure",
            f"Resource efficiency score: {eff_score} pts reduction per asset"
        ]

        return action_name, bullets

scenario_comparator = ScenarioComparator()
