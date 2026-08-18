import pytest
from app.services.missions.mission_optimizer import mission_optimizer, MissionOptimizer
from app.services.missions.mission_scoring import mission_scorer, MissionScorer, MissionScoringConfig
from app.services.missions.mission_service import mission_service
from app.services.missions.route_estimator import route_estimator
from app.models.schemas import RescueTeam, Zone, GeoPolygon, ConnectivityStatus, MissionModifyRequest
from app.data.flood_dataset import ZONES_DATA, RESCUE_TEAMS_DATA

def test_closest_team_not_automatically_chosen():
    """
    Test core judge interaction:
    Team R1 is closer (2.4 km) but lacks medical capability.
    Team R4 is further (4.1 km) but has boat + medical.
    Zone 7 has 3 medical emergencies and deep flood water.
    Optimizer should select R4/R2 over R1 because of critical medical & flood capabilities.
    """
    rec = mission_optimizer.optimize_single_mission("zone-7", victim_count=12, medical_emergencies=3)
    
    assert rec.recommended_team.team_id in ["team-r4", "team-r2"]
    assert rec.recommended_team.medical_match_score == 100
    
    # Verify R1 is scored lower due to missing medical capability
    r1_cand = next((alt for alt in rec.alternate_teams if alt.team_id == "team-r1"), None)
    if not r1_cand:
        assert rec.recommended_team.team_id != "team-r1"
    else:
        assert r1_cand.distance_km < rec.recommended_team.distance_km
        assert r1_cand.total_mission_score < rec.recommended_team.total_mission_score
        assert r1_cand.medical_match_score < 50
    
    # Check 'Why not closest team?' explanation exists
    assert rec.closest_team_comparison is not None
    assert rec.closest_team_comparison.is_closest_team is False
    assert "lacks" in rec.closest_team_comparison.comparison_narrative.lower()

def test_medical_emergency_weighting():
    """
    When medical emergencies = 0, non-medical teams are competitive.
    When medical emergencies = 4, medical teams receive a massive boost.
    """
    z7 = next(z for z in ZONES_DATA if z.id == "zone-7")
    r1 = next(t for t in RESCUE_TEAMS_DATA if t.id == "team-r1") # no medical
    r4 = next(t for t in RESCUE_TEAMS_DATA if t.id == "team-r4") # medical

    # With zero medical emergencies
    score_r1_nomed = mission_scorer.score_candidate(r1, z7, victim_count=12, medical_emergencies=0)
    score_r4_nomed = mission_scorer.score_candidate(r4, z7, victim_count=12, medical_emergencies=0)

    # With 4 critical trauma emergencies
    score_r1_med = mission_scorer.score_candidate(r1, z7, victim_count=12, medical_emergencies=4)
    score_r4_med = mission_scorer.score_candidate(r4, z7, victim_count=12, medical_emergencies=4)

    assert score_r1_med.medical_match_score == 25
    assert score_r4_med.medical_match_score == 100
    assert (score_r4_med.total_mission_score - score_r1_med.total_mission_score) > (score_r4_nomed.total_mission_score - score_r1_nomed.total_mission_score)

def test_boat_requirement_for_deep_water():
    """
    In deep flood water (depth >= 80cm), teams without boats are penalized.
    """
    z7 = next(z for z in ZONES_DATA if z.id == "zone-7") # flood depth ~88cm
    r3 = next(t for t in RESCUE_TEAMS_DATA if t.id == "team-r3") # medical but NO boat
    r4 = next(t for t in RESCUE_TEAMS_DATA if t.id == "team-r4") # medical AND boat

    cand_r3 = mission_scorer.score_candidate(r3, z7, victim_count=12, medical_emergencies=3)
    cand_r4 = mission_scorer.score_candidate(r4, z7, victim_count=12, medical_emergencies=3)

    assert cand_r3.capability_match_score < cand_r4.capability_match_score
    assert cand_r3.travel_time_minutes > cand_r4.travel_time_minutes
    assert "Flood Rescue Boat" in cand_r4.team_capabilities[0] or any("Boat" in c for c in cand_r4.team_capabilities)

def test_future_risk_and_cascade_integration():
    """
    High predicted future risk increases the future risk component of the score.
    """
    z7 = next(z for z in ZONES_DATA if z.id == "zone-7")
    fut_score_z7 = mission_scorer.score_future_risk_priority(z7)
    
    # Zone 7 is escalating rapidly from 82 to 94 in 60m
    assert fut_score_z7 >= 70

def test_silent_risk_physical_recon_mission():
    """
    Silent crisis zones (Zone 4 & Zone 9) with communication loss should generate
    a PHYSICAL_RECON mission recommendation.
    """
    rec_z4 = mission_optimizer.optimize_single_mission("zone-4", victim_count=15, medical_emergencies=2)
    assert rec_z4.mission_type == "PHYSICAL_RECON"
    assert "SILENT CRISIS" in rec_z4.urgency_level or "RECON" in rec_z4.urgency_level
    assert rec_z4.confidence_status == "LOW_CONFIDENCE" or rec_z4.evidence_confidence_percent < 70

def test_multi_mission_fleet_conflict_prevention():
    """
    Simultaneous fleet optimizer allocates teams to multiple zones
    without assigning any single team to more than one active mission.
    """
    plan = mission_optimizer.optimize_multi_mission_fleet(
        target_zone_ids=["zone-7", "zone-4", "zone-9"]
    )
    
    assigned_team_ids = [m.recommended_team.team_id for m in plan.assigned_missions]
    # Check no duplicate team assignments
    assert len(assigned_team_ids) == len(set(assigned_team_ids))
    assert len(plan.assigned_missions) >= 3
    assert plan.conflicts_prevented >= 1

def test_mission_modification_recalculates_scores():
    """
    Modifying the assigned team dynamically recalculates scores and delta comparisons.
    """
    initial_rec = mission_service.optimize_mission("zone-7", victim_count=12, medical_emergencies=3)
    rec_team_id = initial_rec.recommended_team.team_id
    
    # Operator changes team to team-r1
    mod_req = MissionModifyRequest(team_id="team-r1")
    modified_rec = mission_service.modify_mission(initial_rec.mission_id, mod_req)
    
    assert modified_rec.recommended_team.team_id == "team-r1"
    assert modified_rec.recommended_team.total_mission_score < initial_rec.recommended_team.total_mission_score
    # R1 lack of medical trauma kit is surfaced in reasoning
    assert "lacks" in modified_rec.recommended_team.reasoning.lower() or modified_rec.recommended_team.medical_match_score < 50

def test_mission_approval_updates_simulation_state():
    """
    Approving a mission updates in-memory status to DISPATCHED — SIMULATION.
    """
    rec = mission_service.optimize_mission("zone-7", victim_count=12, medical_emergencies=3)
    resp = mission_service.approve_mission(rec.mission_id, team_id="team-r4")
    
    assert resp["status"] == "APPROVED"
    assert "SIMULATION" in resp["dispatch_status"]
    
    # Check team status updated
    r4 = next(t for t in RESCUE_TEAMS_DATA if t.id == "team-r4")
    assert r4.status == "dispatched"

def test_route_estimator_waypoints_and_speeds():
    """
    Route estimator provides waypoints and speed penalties.
    """
    z7 = next(z for z in ZONES_DATA if z.id == "zone-7")
    r1 = next(t for t in RESCUE_TEAMS_DATA if t.id == "team-r1")
    
    metrics = route_estimator.estimate_travel_metrics(r1, z7)
    assert metrics["distance_km"] > 0
    assert metrics["travel_time_minutes"] >= 4
    assert len(metrics["route_waypoints"]) >= 3
