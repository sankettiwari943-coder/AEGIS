import pytest
from app.services.simulation.simulation_engine import simulation_engine, SimulationEngine
from app.services.simulation.scenario_builder import scenario_builder
from app.services.simulation.scenario_runner import scenario_runner
from app.services.simulation.scenario_comparator import scenario_comparator
from app.services.simulation.intervention_engine import intervention_engine
from app.services.simulation.simulation_service import simulation_service
from app.models.schemas import SimulationRequest

def test_baseline_do_nothing_future_state():
    """
    Test Baseline (Do Nothing) produces an unmitigated, worsening future state across 30m, 60m, 3h.
    """
    req_30m = scenario_builder.build_baseline_scenario(time_horizon_minutes=30)
    req_60m = scenario_builder.build_baseline_scenario(time_horizon_minutes=60)
    req_180m = scenario_builder.build_baseline_scenario(time_horizon_minutes=180)

    res_30m = simulation_engine.run_simulation(req_30m)
    res_60m = simulation_engine.run_simulation(req_60m)
    res_180m = simulation_engine.run_simulation(req_180m)

    assert res_30m.net_risk_reduction_points == 0
    assert res_60m.net_risk_reduction_points == 0
    # Risk worsens as time horizon extends
    assert res_180m.baseline_overall_risk >= res_60m.baseline_overall_risk
    assert res_60m.baseline_overall_risk >= res_30m.baseline_overall_risk

def test_single_intervention_reduces_risk():
    """
    Test applying a single intervention (Evacuate Zone 7) reduces overall risk and population exposure.
    """
    req = SimulationRequest(
        scenario_title="Evacuate Zone 7 Only",
        time_horizon_minutes=60,
        perturbations=["road_14_blocked", "hospital_power_lost"],
        interventions=["evacuate_zone_7"]
    )
    result = simulation_engine.run_simulation(req)
    
    assert result.net_risk_reduction_points >= 14
    assert result.scenario_overall_risk < result.baseline_overall_risk
    
    # Check population metric delta
    pop_metric = next((m for m in result.metrics if "Population" in m.metric_name), None)
    assert pop_metric is not None
    assert "-" in pop_metric.delta_display

def test_compound_interventions_optimal_strategy():
    """
    Test compound strategy (Evacuate Zone 7 + Deploy Team R2) yields maximum risk reduction (~27 points).
    """
    req = SimulationRequest(
        scenario_title="Scenario D: Evacuate Z7 + Deploy Delta-2",
        time_horizon_minutes=60,
        perturbations=["road_14_blocked", "hospital_power_lost"],
        interventions=["evacuate_zone_7", "deploy_team_r2"]
    )
    result = simulation_engine.run_simulation(req)
    
    assert result.net_risk_reduction_points >= 23
    assert result.scenario_overall_risk <= 68
    assert result.efficiency_score > 0
    assert len(result.why_bullets) >= 4

def test_resource_conflict_detection():
    """
    Test that exceeding live resource inventory (e.g. 2 medical units when only 1 is available)
    flags resource conflict and lowers confidence.
    """
    # Catalog has 1 medical unit available
    req = SimulationRequest(
        scenario_title="Excess Medical Demands",
        time_horizon_minutes=60,
        perturbations=[],
        interventions=["deploy_medical_unit", "deploy_medical_unit"] # Requires 2 medical units
    )
    result = simulation_engine.run_simulation(req)
    
    assert result.has_resource_conflict is True
    assert result.conflict_message is not None
    assert "RESOURCE CONFLICT" in result.conflict_message
    assert result.confidence_status == "LOW_CONFIDENCE"

def test_cascade_link_mitigation():
    """
    Test that positive interventions (e.g. redirect traffic, emergency generator)
    mitigate downstream cascade links in the cascade before/after visualization.
    """
    req = SimulationRequest(
        scenario_title="Cascade Breaker Scenario",
        time_horizon_minutes=60,
        perturbations=["road_14_blocked", "hospital_power_lost"],
        interventions=["redirect_traffic", "deploy_emergency_generator"]
    )
    result = simulation_engine.run_simulation(req)
    
    assert len(result.cascade_shifts) >= 2
    mitigated_shifts = [c for c in result.cascade_shifts if c.mitigated]
    assert len(mitigated_shifts) >= 2
    assert any("Traffic diversion" in s.explanation for s in mitigated_shifts)

def test_mission_optimizer_integration():
    """
    Test that deploying a rescue team resolves asset details through the Phase 6 Mission Optimizer.
    """
    req = SimulationRequest(
        scenario_title="Deploy Team Integration",
        time_horizon_minutes=60,
        perturbations=["road_14_blocked"],
        interventions=["deploy_team_r2"]
    )
    result = simulation_engine.run_simulation(req)
    
    assert result.recommended_mission_payload is not None
    assert result.recommended_mission_payload["target_zone_id"] == "zone-7"
    assert "Delta-2" in result.recommended_mission_payload["team_callsign"]

def test_multi_scenario_comparison_and_ranking():
    """
    Test comparing Scenarios A, B, C, D properly ranks Scenario D at the top.
    """
    ranking_res = simulation_engine.compare_multiple_scenarios(time_horizon_minutes=60)
    
    assert len(ranking_res.scenarios) == 4
    # Scenario D should be ranked #1
    best = ranking_res.best_scenario
    assert best is not None
    assert best.rank == 1
    assert "Scenario D" in best.title or "Evacuate" in best.title
    assert best.risk_reduction_points >= ranking_res.scenarios[-1].risk_reduction_points

def test_deterministic_reproducibility():
    """
    Test that identical simulation requests produce identical, reproducible results.
    """
    req1 = SimulationRequest(
        scenario_title="Deterministic Test",
        time_horizon_minutes=60,
        perturbations=["road_14_blocked", "hospital_power_lost"],
        interventions=["evacuate_zone_7", "deploy_team_r2"]
    )
    req2 = SimulationRequest(
        scenario_title="Deterministic Test",
        time_horizon_minutes=60,
        perturbations=["road_14_blocked", "hospital_power_lost"],
        interventions=["evacuate_zone_7", "deploy_team_r2"]
    )
    
    res1 = simulation_engine.run_simulation(req1)
    res2 = simulation_engine.run_simulation(req2)
    
    assert res1.baseline_overall_risk == res2.baseline_overall_risk
    assert res1.scenario_overall_risk == res2.scenario_overall_risk
    assert res1.net_risk_reduction_points == res2.net_risk_reduction_points
    assert res1.efficiency_score == res2.efficiency_score

def test_apply_to_mission_plan_bridge():
    """
    Test that apply_to_mission_plan creates a staged mission recommendation in the Mission Service.
    """
    resp = simulation_service.apply_to_mission_plan("sim-default-demo-01")
    assert resp["status"] == "APPLIED_TO_MISSION_PLAN"
    assert "mission_id" in resp
    assert resp["target_zone_id"] == "zone-7"
