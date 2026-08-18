import pytest
from app.services.ingestion import (
    situation_store, live_feed_simulator, normalizer, DataSourceType, HazardType
)

def test_observation_normalization():
    obs = normalizer.normalize_raw_telemetry(
        source="Test USGS Gauge",
        hazard_type="RIVER_LEVEL",
        value=7.5,
        unit="m",
        lat=28.62,
        lng=77.21,
        zone_id="zone-7",
        confidence=0.95
    )
    assert obs.id.startswith("obs-")
    assert obs.hazard_type == HazardType.RIVER_LEVEL
    assert obs.value == 7.5
    assert obs.confidence == 0.95
    assert 0.0 <= obs.severity <= 1.0

def test_situation_state_store_connectors_and_telemetry():
    status = situation_store.get_status()
    assert status.pipeline_status == "OPERATIONAL"
    assert status.active_connectors_count == 5
    assert len(situation_store.observations) > 0

    # Test zone telemetry query
    telemetry = situation_store.get_zone_telemetry("zone-7")
    assert telemetry["zone_id"] == "zone-7"
    assert "current_flood_depth_cm" in telemetry
    assert "rainfall_rate_mmh" in telemetry

def test_live_feed_simulator_steps_and_reset():
    live_feed_simulator.reset()
    st = live_feed_simulator.get_status()
    assert st["current_step"] == 0
    assert not st["is_running"]

    # Advance step 1
    event1 = live_feed_simulator.step()
    assert event1.step == 1
    assert event1.hazard_type == HazardType.RAINFALL_RATE
    assert len(event1.observations) > 0

    # Advance step 2
    event2 = live_feed_simulator.step()
    assert event2.step == 2
    assert event2.hazard_type == HazardType.FLOOD_DEPTH

    # Reset
    res = live_feed_simulator.reset()
    assert res["status"] == "RESET_SUCCESSFUL"
    assert live_feed_simulator.current_step == 0
