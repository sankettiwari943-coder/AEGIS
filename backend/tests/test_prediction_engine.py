import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.prediction import (
    prediction_service, risk_model, escalation_model, RiskWeights
)
from app.services.prediction.risk_model import (
    HistoricalObservations, calculate_trend_velocity
)
from app.data.flood_dataset import ZONES_DATA

client = TestClient(app)

def test_risk_calculation_factors():
    # Verify increasing rainfall increases risk
    history = HistoricalObservations(
        river_level_history=[4.0, 4.5, 5.0],
        rainfall_history=[30.0, 45.0, 60.0],
        flood_depth_history=[20.0, 30.0, 40.0],
        road_access_history=[90, 80, 70]
    )
    low_rain = risk_model.compute_composite_risk(20.0, 5.0, 40.0, 10.0, 70, 0.5, history)
    high_rain = risk_model.compute_composite_risk(90.0, 5.0, 40.0, 10.0, 70, 0.5, history)
    assert high_rain["risk_score"] > low_rain["risk_score"]

    # Verify increasing river level increases risk
    low_river = risk_model.compute_composite_risk(60.0, 3.0, 40.0, 10.0, 70, 0.5, history)
    high_river = risk_model.compute_composite_risk(60.0, 8.5, 40.0, 10.0, 70, 0.5, history)
    assert high_river["risk_score"] > low_river["risk_score"]

    # Verify declining road accessibility increases operational risk
    good_roads = risk_model.compute_composite_risk(60.0, 5.0, 40.0, 10.0, 95, 0.5, history)
    bad_roads = risk_model.compute_composite_risk(60.0, 5.0, 40.0, 10.0, 15, 0.5, history)
    assert bad_roads["risk_score"] >= good_roads["risk_score"]

def test_trend_detection():
    rising_trend = calculate_trend_velocity([3.2, 3.6, 4.2])
    assert rising_trend > 0.05 # strictly positive rising velocity

    falling_trend = calculate_trend_velocity([4.2, 3.6, 3.2])
    assert falling_trend < -0.05 # negative falling velocity

def test_escalation_detection():
    # 82 -> 87 -> 94 crosses critical threshold (90)
    res = escalation_model.calculate_escalation_time(
        current_risk=82,
        predicted_risk_30m=87,
        predicted_risk_60m=94
    )
    assert res["escalation_detected"] is True
    assert 35 <= res["minutes_to_escalation"] <= 45 # ~42 minutes!

def test_operational_priority_scoring():
    top_items = prediction_service.get_top_predictions()
    assert len(top_items) >= 3
    # Top item must be Zone 7 with highest priority ~96
    assert top_items[0]["priority_score"] >= 90
    assert "Zone 7" in top_items[0]["target_entity"]
    assert top_items[1]["priority_score"] >= 85

def test_prediction_api_endpoints():
    # 1. Main predictions endpoint
    res = client.get("/api/predictions")
    assert res.status_code == 200
    data = res.json()
    assert "zone_predictions" in data
    assert "top_predictions" in data
    assert data["escalation_countdown_minutes"] == 42

    # 2. Top predictions endpoint
    res_top = client.get("/api/predictions/top")
    assert res_top.status_code == 200
    top_data = res_top.json()
    assert len(top_data) >= 3

    # 3. Horizon endpoint (30m, 60m, 180m)
    res_horizon = client.get("/api/predictions/horizon/60")
    assert res_horizon.status_code == 200
    horizon_data = res_horizon.json()
    assert len(horizon_data) == len(ZONES_DATA)
    assert horizon_data[0]["horizon_minutes"] == 60

    # 4. Zone specific endpoint
    res_z7 = client.get("/api/predictions/zone-7")
    assert res_z7.status_code == 200
    z7_data = res_z7.json()
    assert z7_data["zone_id"] == "zone-7"
    assert z7_data["current_risk"] == 82
    assert z7_data["predicted_risk_60m"] == 94
    assert len(z7_data["drivers"]) >= 4
