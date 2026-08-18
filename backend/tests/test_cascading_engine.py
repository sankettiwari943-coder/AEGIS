"""
Unit and Integration Tests for Phase 4 Cascading Risk Intelligence
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.data.flood_dataset import ZONES_DATA
from app.services.cascading.graph import canonical_graph
from app.services.cascading.risk_propagation import risk_propagation_model
from app.services.cascading.cascade_engine import cascade_engine
from app.services.cascading.cascade_service import cascade_service

client = TestClient(app)

def test_direct_cascade():
    """Verify direct edge connection and propagation between Flood and Road Blockage."""
    edge = canonical_graph.get_edge_data("flood", "road_blockage")
    assert edge is not None
    assert edge["relationship"] == "causes"
    assert edge["impact"] >= 0.80

    # Risk propagation from parent 80 to child
    child_risk, conf = risk_propagation_model.compute_direct_child_risk(
        parent_risk=80,
        edge_impact=edge["impact"],
        edge_confidence=edge["confidence"]
    )
    assert 50 <= child_risk <= 100
    assert 50 <= conf <= 100

def test_multi_step_cascade():
    """Verify multi-step chain propagation: Flood -> Road -> Hospital -> Medical Delay -> Victim Risk."""
    edges = [
        canonical_graph.get_edge_data("flood", "road_blockage"),
        canonical_graph.get_edge_data("road_blockage", "hospital_isolation"),
        canonical_graph.get_edge_data("hospital_isolation", "medical_delay"),
        canonical_graph.get_edge_data("medical_delay", "victim_risk")
    ]
    assert all(e is not None for e in edges)
    
    steps = risk_propagation_model.propagate_chain(
        root_risk=86,
        edges_sequence=edges,
        initial_confidence=0.95
    )
    assert len(steps) == 4
    # All step risks should be bounded
    for step in steps:
        assert 0 <= step["step_risk"] <= 100
        assert 0 <= step["confidence"] <= 100
        assert step["action_state"] in ["INITIATING", "SURGING", "CRITICAL", "ELEVATED", "MODERATE"]

def test_risk_propagation_monotonicity():
    """Verify higher parent risk leads to equal or higher downstream risk."""
    edge = canonical_graph.get_edge_data("flood", "road_blockage")
    low_risk, _ = risk_propagation_model.compute_direct_child_risk(30, edge["impact"], edge["confidence"])
    high_risk, _ = risk_propagation_model.compute_direct_child_risk(90, edge["impact"], edge["confidence"])
    assert high_risk > low_risk

def test_confidence_decay():
    """Verify confidence decays realistically along multi-hop chains."""
    edges = [
        {"impact": 0.9, "confidence": 0.9, "relationship": "causes"},
        {"impact": 0.85, "confidence": 0.85, "relationship": "delays"},
        {"impact": 0.8, "confidence": 0.8, "relationship": "amplifies"}
    ]
    steps = risk_propagation_model.propagate_chain(80, edges, initial_confidence=0.95)
    assert steps[0]["confidence"] >= steps[1]["confidence"]
    assert steps[1]["confidence"] >= steps[2]["confidence"]

def test_cycle_detection_and_termination():
    """Verify feedback loops (Flood -> Power -> Pump -> Flood) are detected without causing infinite loops."""
    cycles = cascade_engine.detect_cycles()
    assert len(cycles) > 0
    # Search paths bounded by max_depth
    chains = cascade_engine.discover_chains("flood", "victim_risk")
    assert len(chains) > 0
    for chain in chains:
        assert len(chain) <= cascade_engine.max_depth + 1

def test_secondary_risk_categories():
    """Verify all 5 secondary risk categories are calculated for Zone 7."""
    z7 = next(z for z in ZONES_DATA if z.id == "zone-7")
    sec_risks, category_scores = cascade_engine.evaluate_zone_secondary_risks(z7)
    
    # 5 standard categories
    assert "infrastructure" in category_scores
    assert "medical" in category_scores
    assert "communication" in category_scores
    assert "population" in category_scores
    assert "environmental" in category_scores

    # Specific secondary risks
    assert sec_risks["road_isolation"] >= 70
    assert sec_risks["hospital_accessibility"] >= 60
    assert sec_risks["power_failure"] >= 65

def test_silent_crisis_integration():
    """Verify communication loss in Zone 4 generates elevated silent crisis blindspot risk."""
    z4 = next(z for z in ZONES_DATA if z.id == "zone-4")
    sec_risks, _ = cascade_engine.evaluate_zone_secondary_risks(z4)
    assert sec_risks["communication_loss"] >= 90
    assert sec_risks["reporting_blackout"] >= 90

    top_chains = cascade_engine.build_zone_top_chains(z4, sec_risks)
    silent_chain = next((c for c in top_chains if "Silent Crisis" in c.title or "Reporting" in c.title), None)
    assert silent_chain is not None
    assert silent_chain.priority_score >= 80

def test_zone_cascade_graph_response():
    """Verify complete zone graph generation structure."""
    graph = cascade_service.get_zone_cascade_graph("zone-7")
    assert graph is not None
    assert graph.zone_id == "zone-7"
    assert len(graph.nodes) >= 15
    assert len(graph.edges) >= 15
    assert len(graph.top_chains) >= 2
    assert len(graph.contributors) >= 4
    assert graph.cascading_risk >= 80

def test_api_cascades_endpoints():
    """Verify FastAPI endpoints return 200 and expected models."""
    # 1. GET /api/cascades
    res = client.get("/api/cascades")
    assert res.status_code == 200
    cascades = res.json()
    assert len(cascades) == 12

    # 2. GET /api/cascades/top
    res = client.get("/api/cascades/top")
    assert res.status_code == 200
    top = res.json()
    assert len(top) > 0
    assert top[0]["priority_score"] >= 80

    # 3. GET /api/cascades/alerts
    res = client.get("/api/cascades/alerts")
    assert res.status_code == 200
    alerts = res.json()
    assert len(alerts) > 0

    # 4. GET /api/cascades/zone-7
    res = client.get("/api/cascades/zone-7")
    assert res.status_code == 200
    z7_detail = res.json()
    assert z7_detail["primary_risk"] == 82
    assert z7_detail["cascading_risk"] >= 85

    # 5. GET /api/cascades/zone-7/graph
    res = client.get("/api/cascades/zone-7/graph")
    assert res.status_code == 200
    z7_graph = res.json()
    assert len(z7_graph["nodes"]) > 0
    assert len(z7_graph["edges"]) > 0

    # 6. GET /api/risks (backward compatibility)
    res = client.get("/api/risks")
    assert res.status_code == 200
    risks = res.json()
    assert len(risks) == 12
