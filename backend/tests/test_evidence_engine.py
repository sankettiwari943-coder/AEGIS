"""
Tests for Evidence & Truth Intelligence Engine (Phase 5)
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import EvidenceType, EvidenceStatus, EvidenceItem
from app.services.evidence.confidence_engine import confidence_engine
from app.services.evidence.verification_engine import verification_engine
from app.services.evidence.evidence_service import evidence_service

client = TestClient(app)

def test_evidence_aggregation_increases_confidence():
    """Verify that multiple corroborating sources increase confidence score."""
    single_item = [
        EvidenceItem(
            id="test-1",
            type=EvidenceType.SENSOR,
            timestamp="2026-08-15T10:00:00Z",
            source="Gauge 1",
            location="Zone 7",
            claim="Flood rising",
            value="80cm",
            reliability=0.90,
            status=EvidenceStatus.SUPPORTED,
            minutes_ago=5
        )
    ]
    multi_items = single_item + [
        EvidenceItem(
            id="test-2",
            type=EvidenceType.SATELLITE_OBSERVATION,
            timestamp="2026-08-15T10:00:00Z",
            source="SAR Radar",
            location="Zone 7",
            claim="Surface anomaly",
            value="90%",
            reliability=0.88,
            status=EvidenceStatus.SUPPORTED,
            minutes_ago=10
        ),
        EvidenceItem(
            id="test-3",
            type=EvidenceType.OFFICIAL_REPORT,
            timestamp="2026-08-15T10:00:00Z",
            source="Dispatch Unit",
            location="Zone 7",
            claim="Road closed",
            value="Closed",
            reliability=0.95,
            status=EvidenceStatus.VERIFIED,
            minutes_ago=8
        )
    ]

    conf_single, _, _, _ = confidence_engine.evaluate_claim_confidence(single_item, [])
    conf_multi, _, _, _ = confidence_engine.evaluate_claim_confidence(multi_items, [])

    assert conf_multi > conf_single
    assert 0 <= conf_single <= 100
    assert 0 <= conf_multi <= 100

def test_contradictions_reduce_confidence_and_detect_conflict():
    """Verify that conflicting evidence penalizes confidence and triggers conflict detection."""
    supporting = [
        EvidenceItem(
            id="supp-1",
            type=EvidenceType.CITIZEN_REPORT,
            timestamp="2026-08-15T10:00:00Z",
            source="Crowd report",
            location="Zone 6",
            claim="Substation fire",
            value="Fire seen",
            reliability=0.70,
            status=EvidenceStatus.SUPPORTED,
            minutes_ago=5
        )
    ]
    conflicting = [
        EvidenceItem(
            id="conf-1",
            type=EvidenceType.SENSOR,
            timestamp="2026-08-15T10:00:00Z",
            source="SCADA Telemetry",
            location="Zone 6",
            claim="Grid energized normal",
            value="220kV active",
            reliability=0.90,
            status=EvidenceStatus.VERIFIED,
            is_contradicting=True,
            minutes_ago=2
        )
    ]

    conf_clean, _, _, _ = confidence_engine.evaluate_claim_confidence(supporting, [])
    conf_conflict, _, _, _ = confidence_engine.evaluate_claim_confidence(supporting, conflicting)

    assert conf_conflict < conf_clean

    status, requires_recon, conflict_obj, rec = verification_engine.determine_claim_status(conf_conflict, supporting, conflicting)
    assert status in [EvidenceStatus.CONFLICTING, EvidenceStatus.REJECTED]
    assert conflict_obj is not None
    assert conflict_obj.reconciliation_status == "RECON_REQUIRED"

def test_source_reliability_weighting():
    """Verify that high-reliability sources yield higher confidence than low-reliability ones."""
    official_item = [
        EvidenceItem(
            id="rel-1",
            type=EvidenceType.OFFICIAL_REPORT,
            timestamp="2026-08-15T10:00:00Z",
            source="Police Dispatch",
            location="Zone 7",
            claim="Major breach",
            value="Confirmed",
            reliability=0.95,
            status=EvidenceStatus.VERIFIED,
            minutes_ago=5
        )
    ]
    citizen_item = [
        EvidenceItem(
            id="rel-2",
            type=EvidenceType.CITIZEN_REPORT,
            timestamp="2026-08-15T10:00:00Z",
            source="Anonymous post",
            location="Zone 7",
            claim="Major breach",
            value="Report",
            reliability=0.70,
            status=EvidenceStatus.UNVERIFIED,
            minutes_ago=5
        )
    ]

    conf_official, _, _, _ = confidence_engine.evaluate_claim_confidence(official_item, [])
    conf_citizen, _, _, _ = confidence_engine.evaluate_claim_confidence(citizen_item, [])

    assert conf_official > conf_citizen

def test_recency_decay():
    """Verify that older evidence experiences recency decay."""
    fresh_factor = confidence_engine.calculate_recency_factor(minutes_ago=2)
    stale_factor = confidence_engine.calculate_recency_factor(minutes_ago=90)

    assert fresh_factor > stale_factor
    assert 0.0 < stale_factor < fresh_factor <= 1.0

def test_stale_evidence_downgrade():
    """Verify that evidence older than stale threshold is classified as STALE."""
    stale_items = [
        EvidenceItem(
            id="stale-1",
            type=EvidenceType.SENSOR,
            timestamp="2026-08-15T07:00:00Z",
            source="Old gauge",
            location="Zone 2",
            claim="Depth 50cm",
            value="50cm",
            reliability=0.90,
            status=EvidenceStatus.STALE,
            minutes_ago=150
        )
    ]

    conf, _, _, _ = confidence_engine.evaluate_claim_confidence(stale_items, [])
    status, requires_recon, _, rec = verification_engine.determine_claim_status(conf, stale_items, [])

    assert status == EvidenceStatus.STALE
    assert requires_recon is True
    assert "outdated" in rec.lower()

def test_insufficient_evidence_state():
    """Verify that uncorroborated claims trigger insufficient evidence state."""
    single_rumor = [
        EvidenceItem(
            id="rumor-1",
            type=EvidenceType.CITIZEN_REPORT,
            timestamp="2026-08-15T10:00:00Z",
            source="Anonymous SMS",
            location="North Basin",
            claim="Dam broken",
            value="Rumor",
            reliability=0.70,
            status=EvidenceStatus.UNVERIFIED,
            minutes_ago=4
        )
    ]
    conf, _, _, _ = confidence_engine.evaluate_claim_confidence(single_rumor, [])
    status, requires_recon, _, rec = verification_engine.determine_claim_status(conf, single_rumor, [])

    assert status == EvidenceStatus.UNVERIFIED
    assert requires_recon is True
    assert "INSUFFICIENT EVIDENCE" in rec

def test_decision_evidence_chain_traceability():
    """Verify that decisions trace back through Decision -> Risk -> Prediction -> Evidence."""
    trace = evidence_service.get_decision_evidence_chain("decision-zone-7-escalation")
    assert trace is not None
    assert trace.zone_id == "zone-7"
    assert len(trace.decision_chain) == 4
    
    levels = [step["level"] for step in trace.decision_chain]
    assert levels == ["DECISION", "RISK", "PREDICTION", "EVIDENCE"]
    assert len(trace.key_signals) >= 4
    assert len(trace.underlying_evidence) >= 1

def test_api_evidence_endpoints():
    """Verify all REST API endpoints for evidence intelligence."""
    # 1. GET /api/evidence
    res_ev = client.get("/api/evidence")
    assert res_ev.status_code == 200
    ev_list = res_ev.json()
    assert len(ev_list) >= 10

    # 2. GET /api/evidence/summary
    res_sum = client.get("/api/evidence/summary")
    assert res_sum.status_code == 200
    summary = res_sum.json()
    assert summary["total_claims_analyzed"] >= 10
    assert 0 <= summary["data_trust_index"] <= 100
    assert "source_reliability" in summary["trust_breakdown"]

    # 3. GET /api/evidence/claims
    res_claims = client.get("/api/evidence/claims")
    assert res_claims.status_code == 200
    claims = res_claims.json()
    assert len(claims) >= 5

    # 4. GET /api/evidence/claims/{claim_id}
    res_c1 = client.get("/api/evidence/claims/claim-01")
    assert res_c1.status_code == 200
    c1 = res_c1.json()
    assert c1["claim_id"] == "claim-01"
    assert c1["ai_confidence_percent"] >= 70
    assert len(c1["supporting_evidence"]) >= 3

    # 5. GET /api/evidence/claims/{claim_id}/sources
    res_sources = client.get("/api/evidence/claims/claim-01/sources")
    assert res_sources.status_code == 200
    sources = res_sources.json()
    assert sources["supporting_count"] >= 3

    # 6. GET /api/evidence/claims/{claim_id}/conflicts
    res_conf = client.get("/api/evidence/claims/claim-01/conflicts")
    assert res_conf.status_code == 200
    conflicts = res_conf.json()
    assert len(conflicts) >= 1

    # 7. GET /api/evidence/decisions/{decision_id}
    res_dec = client.get("/api/evidence/decisions/decision-zone-7-escalation")
    assert res_dec.status_code == 200
    dec = res_dec.json()
    assert dec["decision_id"] == "decision-zone-7-escalation"
    assert len(dec["decision_chain"]) == 4
