import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_health():
    """Test GET /api/health returns operational status for all 7 engines."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"
    assert data["mode"] == "DEMO / SIMULATION"
    services = data["services"]
    assert services["prediction"] == "healthy"
    assert services["cascade"] == "healthy"
    assert services["evidence"] == "healthy"
    assert services["missions"] == "healthy"
    assert services["simulation"] == "healthy"
    assert services["adaptive"] == "healthy"
    assert services["ai"] == "healthy"

def test_api_demo_reset():
    """Test POST /api/demo/reset cleanly resets all dynamic state."""
    res = client.post("/api/demo/reset")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "RESET_SUCCESSFUL"
    assert data["timeline_step"] == "T+0"
    assert data["active_zones_count"] >= 7
    assert data["available_teams_count"] >= 3

def test_api_demo_state():
    """Test GET /api/demo/state returns timeline horizons (T+0, T+30, T+60, T+180)."""
    res = client.get("/api/demo/state")
    assert res.status_code == 200
    data = res.json()
    assert data["event_id"] == "EVT-2026-FL-001"
    steps = data["timeline_steps"]
    assert len(steps) == 4
    times = [s["time"] for s in steps]
    assert times == ["T+0", "T+30", "T+60", "T+180"]
    # Check Zone 7 escalation progression
    assert steps[0]["zone7_risk"] == 86
    assert steps[1]["zone7_risk"] == 89
    assert steps[2]["zone7_risk"] == 93
    assert steps[3]["zone7_risk"] == 97
