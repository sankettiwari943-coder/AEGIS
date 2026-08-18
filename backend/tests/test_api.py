import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "OPERATIONAL"

def test_get_current_event():
    response = client.get("/api/event/current")
    assert response.status_code == 200
    data = response.json()
    assert data["disaster_type"] == "URBAN FLOOD"
    assert data["status"] == "ESCALATING"

def test_get_zones():
    response = client.get("/api/zones")
    assert response.status_code == 200
    zones = response.json()
    assert len(zones) == 12

def test_get_predictions():
    response = client.get("/api/predictions")
    assert response.status_code == 200
    data = response.json()
    assert "zone_predictions" in data
    assert data["escalation_countdown_minutes"] > 0

def test_get_silent_risks():
    response = client.get("/api/silent-risks")
    assert response.status_code == 200
    silent_risks = response.json()
    assert len(silent_risks) == 12
    assert silent_risks[0]["silent_crisis_score_percent"] >= 80

def test_mission_optimize_endpoint():
    response = client.post("/api/missions/optimize?target_zone_id=zone-7&victim_count=12&medical_emergencies=3")
    assert response.status_code == 200
    data = response.json()
    assert data["target_zone_id"] == "zone-7"
    assert data["recommended_team"]["total_mission_score"] > 80

def test_simulation_run_endpoint():
    payload = {
        "scenario_title": "Test Scenario",
        "perturbations": ["road_14_blocked", "hospital_power_lost"],
        "interventions": ["deploy_team_r4"]
    }
    response = client.post("/api/simulations/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "best_preventive_action" in data

def test_feedback_endpoint():
    payload = {
        "mission_id": "mission-01",
        "target_zone_id": "zone-7",
        "predicted_eta_minutes": 10,
        "actual_eta_minutes": 17,
        "predicted_road_access_pct": 70,
        "actual_road_access_pct": 35,
        "observations": "Bridge overtopping caused 7 min delay"
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["eta_error_minutes"] == 7
    assert data["road_access_error_pct"] == -35

def test_ai_assistant_chat():
    payload = {
        "query": "Why is Zone 7 becoming critical in 42 minutes?"
    }
    response = client.post("/api/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Zone 7" in data["answer"]
    assert data["confidence_score"] > 70
