import pytest
from app.services.agents.orchestrator import disaster_orchestrator

def test_orchestrator_grounded_response_with_rag_and_live_facts():
    # Query orchestrator with question
    res = disaster_orchestrator.process_query(
        query="What should we do right now in Zone 7?",
        session_id="test-grounding-session",
        context_zone_id="zone-7"
    )
    assert res.direct_answer != ""
    assert len(res.facts) > 0
    assert len(res.live_facts) > 0
    assert len(res.retrieved_guidance) > 0
    assert len(res.recommendations) > 0
    assert len(res.uncertainties) > 0
    assert res.requires_human_approval is True
    assert res.confidence_score > 70

def test_orchestrator_sop_query_intent():
    res = disaster_orchestrator.process_query(
        query="What is the official evacuation SOP guideline for hospital isolation?",
        session_id="test-sop-session"
    )
    assert "query_emergency_knowledge_base" in res.tools_used or len(res.retrieved_guidance) > 0
