import pytest
from app.services.cascading_risk_engine import cascading_risk_engine
from app.services.silent_risk_engine import silent_risk_engine
from app.services.mission_optimizer import mission_optimizer
from app.services.simulation_engine import simulation_engine
from app.models.schemas import SimulationRequest

def test_cascading_risk_engine():
    risks = cascading_risk_engine.analyze_all_zones()
    assert len(risks) == 12
    z7 = next(r for r in risks if r.zone_id == "zone-7")
    assert z7.combined_cascading_score >= 85
    assert len(z7.critical_chain) > 3

def test_silent_risk_engine():
    silent_risks = silent_risk_engine.get_all_silent_risks()
    z4 = next(s for s in silent_risks if s.zone_id == "zone-4")
    assert z4.silent_crisis_score_percent == 91
    assert z4.requires_physical_recon is True
    assert z4.connectivity_status == "LOST"

def test_mission_optimizer():
    rec = mission_optimizer.optimize_mission("zone-7", victim_count=12, medical_emergencies=3)
    assert rec.target_zone_id == "zone-7"
    assert rec.recommended_team.team_id in ["team-r2", "team-r4"]
    assert rec.recommended_team.total_mission_score > 80
    assert rec.recommended_team.score_breakdown is not None

def test_what_if_simulation():
    req = SimulationRequest(
        scenario_title="Demo Compound Shock",
        perturbations=["road_14_blocked", "hospital_power_lost", "rainfall_intensifies"],
        interventions=["deploy_team_r4", "activate_shelter_b", "deploy_emergency_generator"]
    )
    result = simulation_engine.run_simulation(req)
    assert result.net_risk_reduction_points > 0
    assert len(result.metrics) == 5
    assert len(result.critical_impacted_zones) >= 3
