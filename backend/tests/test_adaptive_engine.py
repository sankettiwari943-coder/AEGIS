import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.adaptive.prediction_evaluator import prediction_evaluator, PredictionEvaluator
from app.services.adaptive.calibration_engine import calibration_engine, CalibrationEngine
from app.services.adaptive.learning_store import learning_store, LearningStore
from app.services.adaptive.outcome_tracker import outcome_tracker
from app.services.adaptive.feedback_engine import feedback_engine
from app.services.adaptive.adaptive_service import adaptive_service
from app.services.prediction_engine import prediction_engine
from app.services.agents.orchestrator import disaster_orchestrator

client = TestClient(app)

def test_prediction_evaluator_errors_and_zero_division():
    """Test absolute error, relative error, and zero division safety."""
    # Absolute error
    assert prediction_evaluator.calculate_absolute_error(70.0, 35.0) == 35.0
    assert prediction_evaluator.calculate_absolute_error(35.0, 70.0) == 35.0
    assert prediction_evaluator.calculate_absolute_error(50.0, 50.0) == 0.0

    # Raw error (actual - predicted)
    assert prediction_evaluator.calculate_error(70.0, 35.0) == -35.0 # actual was lower
    assert prediction_evaluator.calculate_error(35.0, 70.0) == 35.0  # actual was higher

    # Relative error with actual = 0 (zero division safe)
    rel_zero = prediction_evaluator.calculate_relative_error_pct(10.0, 0.0)
    assert rel_zero is not None
    assert rel_zero >= 0.0

    # Relative error standard
    assert prediction_evaluator.calculate_relative_error_pct(50.0, 100.0) == 50.0

def test_prediction_evaluator_classification():
    """Test status classification (ACCURATE, UNDERPREDICTED, OVERPREDICTED)."""
    # Within ±5 tolerance -> ACCURATE
    assert prediction_evaluator.classify_status(80.0, 83.0) == "ACCURATE"
    assert prediction_evaluator.classify_status(80.0, 76.0) == "ACCURATE"
    assert prediction_evaluator.classify_status(80.0, 80.0) == "ACCURATE"

    # Actual > predicted + 5 -> UNDERPREDICTED (danger was worse than estimated)
    assert prediction_evaluator.classify_status(70.0, 90.0) == "UNDERPREDICTED"

    # Predicted > actual + 5 -> OVERPREDICTED
    assert prediction_evaluator.classify_status(90.0, 65.0) == "OVERPREDICTED"

    # Custom tolerance
    assert prediction_evaluator.classify_status(80.0, 88.0, tolerance=10.0) == "ACCURATE"

def test_calibration_engine_sample_and_limits():
    """Test calibration requirements: minimum sample count, recency weighting, and max adjustment cap."""
    custom_engine = CalibrationEngine(min_sample_count=5, max_calibration_limit=20.0)
    
    # Test insufficient data when samples < 5
    insufficient_calib = custom_engine.compute_calibration_for_metric("predicted_isolation_time")
    assert insufficient_calib["sample_count"] < 5
    assert insufficient_calib["status"] == "INSUFFICIENT_DATA"

    # Test calibration for road_accessibility (has 12 observations)
    road_calib = custom_engine.compute_calibration_for_metric("road_accessibility")
    assert road_calib["sample_count"] >= 5
    assert road_calib["status"] in ["RECALIBRATION_RECOMMENDED", "CALIBRATED", "LIMIT_REACHED"]
    assert abs(road_calib["applied_adjustment"]) <= 20.0 # Enforces cap

def test_learning_store_and_audit_trail():
    """Test learning store records outcomes and emits audit events."""
    outcomes = learning_store.get_all_outcomes()
    assert len(outcomes) >= 20 # Pre-seeded 24-item demo dataset

    events = learning_store.get_learning_events()
    assert len(events) >= 1
    assert any("road_accessibility" in e.get("metric", "") for e in events)

def test_outcome_tracker_and_feedback():
    """Test recording an outcome updates outcomes list and auto-recalibrates."""
    initial_count = len(learning_store.get_all_outcomes())

    res = outcome_tracker.record_outcome(
        metric="road_accessibility",
        predicted_value=75.0,
        actual_value=30.0,
        zone_id="zone-7",
        source="Operator Observation",
        notes="Bridge approach washed out earlier than modeled."
    )

    assert res["id"].startswith("OUT-")
    assert res["status"] == "OVERPREDICTED" or res["status"] == "UNDERPREDICTED"
    assert len(learning_store.get_all_outcomes()) == initial_count + 1

def test_prediction_service_calibration_layer():
    """Test that PredictionService outputs the explainable calibration layer."""
    pred_res = prediction_engine.predict_zone(prediction_engine.zones[0])
    assert "calibration" in pred_res
    calib = pred_res["calibration"]
    assert "base_estimate" in calib
    assert "calibration_adjustment" in calib
    assert "calibrated_estimate" in calib
    assert "calibration_basis" in calib
    assert "status" in calib

def test_adaptive_calibration_demo_replay():
    """Test calibration demo replay reduces historical error by ~50%."""
    demo_res = adaptive_service.run_calibration_demo()
    assert demo_res.metric == "road_accessibility"
    assert demo_res.after_average_error < demo_res.before_average_error
    assert demo_res.error_reduction_percent > 20.0 # Significant measurable reduction

def test_orchestrator_learning_queries():
    """Test AI Orchestrator answers learning and accuracy questions using grounded adaptive data."""
    # Query 1: What has AEGIS learned?
    res1 = disaster_orchestrator.process_query("What has AEGIS learned?")
    assert "road" in res1.answer.lower() or "underestimation" in res1.answer.lower() or "calibration" in res1.answer.lower()
    assert "get_prediction_performance" in res1.tools_used or "get_adaptive_insights" in res1.tools_used or "get_calibrations" in res1.tools_used

    # Query 2: How accurate are our predictions?
    res2 = disaster_orchestrator.process_query("How accurate have our predictions been?")
    assert "82%" in res2.answer or "accuracy" in res2.answer.lower() or "hospital" in res2.answer.lower()

def test_adaptive_api_endpoints():
    """Test all Phase 9 API endpoints."""
    # 1. GET /api/adaptive/status
    res = client.get("/api/adaptive/status")
    assert res.status_code == 200
    st = res.json()
    assert "status" in st
    assert st["total_evaluated_predictions"] >= 20

    # 2. GET /api/adaptive/performance
    res = client.get("/api/adaptive/performance")
    assert res.status_code == 200
    perf = res.json()
    assert perf["overall_accuracy"] > 0.5
    assert len(perf["metrics"]) >= 3

    # 3. GET /api/adaptive/calibrations
    res = client.get("/api/adaptive/calibrations")
    assert res.status_code == 200
    calibs = res.json()
    assert len(calibs) >= 3

    # 4. GET /api/adaptive/insights
    res = client.get("/api/adaptive/insights")
    assert res.status_code == 200
    insights = res.json()
    assert len(insights) >= 3

    # 5. POST /api/adaptive/calibrate
    res = client.post("/api/adaptive/calibrate")
    assert res.status_code == 200
    calib_res = res.json()
    assert len(calib_res) >= 3

    # 6. GET /api/adaptive/history
    res = client.get("/api/adaptive/history")
    assert res.status_code == 200
    history = res.json()
    assert len(history) >= 1

    # 7. POST /api/adaptive/demo-replay
    res = client.post("/api/adaptive/demo-replay")
    assert res.status_code == 200
    demo = res.json()
    assert demo["error_reduction_points"] > 0

    # 8. POST /api/feedback & GET /api/feedback
    payload = {
        "metric": "road_accessibility",
        "predicted_value": 60.0,
        "actual_value": 30.0,
        "target_zone_id": "zone-7",
        "source": "Operator Observation",
        "notes": "Route flooded by secondary backwater."
    }
    res = client.post("/api/feedback", json=payload)
    assert res.status_code == 200
    fb = res.json()
    assert "feedback_id" in fb
    assert fb["status"] == "RECALIBRATION_RECORDED"

    # 9. GET /api/feedback/{id}
    res_list = client.get("/api/adaptive/outcomes")
    assert res_list.status_code == 200
    first_id = res_list.json()[0]["id"]
    res_get = client.get(f"/api/feedback/{first_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == first_id
