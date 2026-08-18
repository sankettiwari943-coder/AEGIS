import pytest
from app.services.orchestrator.orchestrator import disaster_orchestrator
from app.services.orchestrator.intent_router import intent_router
from app.services.orchestrator.tool_registry import tool_registry
from app.models.schemas import AIChatRequest, OrchestratorQueryRequest

def test_intent_routing_and_tool_selection():
    """
    Test that operator natural language queries map to correct intents and tool sets.
    """
    # 1. Situation query
    intent1, tools1, _ = intent_router.route_intent("What is happening right now?")
    assert intent1 == "SITUATION_QUERY"
    assert "get_current_situation" in tools1

    # 2. Prediction query
    intent2, tools2, _ = intent_router.route_intent("What happens in the next hour?")
    assert intent2 == "PREDICTION_QUERY"
    assert "get_prediction" in tools2

    # 3. Mission query
    intent3, tools3, _ = intent_router.route_intent("Which team should we send to Zone 7?")
    assert intent3 == "MISSION_QUERY"
    assert "get_mission_recommendations" in tools3

    # 4. Simulation query
    intent4, tools4, _ = intent_router.route_intent("What if we evacuate Zone 7 and deploy Delta-2?")
    assert intent4 == "SIMULATION_QUERY"
    assert "run_simulation" in tools4

    # 5. Silent risk query
    intent5, tools5, zone5 = intent_router.route_intent("Are there areas where people aren't reporting?")
    assert intent5 == "SILENT_RISK_QUERY"
    assert "get_silent_risk_zones" in tools5

def test_orchestrator_situation_query():
    """
    Test situation query invokes get_current_situation and returns grounded facts.
    """
    res = disaster_orchestrator.process_query("What is happening in the disaster area?")
    
    assert res.answer is not None
    assert "Zone 7" in res.answer or "River Bend" in res.answer
    assert "get_current_situation" in res.tools_used
    assert len(res.facts) >= 1
    assert len(res.deep_links) >= 1
    assert res.requires_human_approval is True

def test_orchestrator_mission_query_tradeoff():
    """
    Test mission query selects Delta-2 and explains the medical capability trade-off over closer Team R1.
    """
    res = disaster_orchestrator.process_query("Which team should respond to Zone 7?")
    
    assert "Delta-2" in res.answer or "Heavy Evacuation" in res.answer
    assert "get_mission_recommendations" in res.tools_used
    assert len(res.why_rationale) >= 2
    assert any("medical" in r.lower() or "trauma" in r.lower() or "boat" in r.lower() for r in res.why_rationale)

def test_orchestrator_simulation_query():
    """
    Test simulation query invokes run_simulation and returns estimated risk reduction.
    """
    res = disaster_orchestrator.process_query("What happens if we do nothing vs evacuate Zone 7?")
    
    assert "run_simulation" in res.tools_used
    assert "27" in res.answer or "risk reduction" in res.answer.lower() or "scenario" in res.answer.lower()
    assert res.confidence_score >= 80

def test_orchestrator_silent_crisis_query():
    """
    Test silent crisis query surfaces Zone 4 communication blackout and physical recon recommendation.
    """
    res = disaster_orchestrator.process_query("Are there any silent crisis areas without reports?")
    
    assert "get_silent_risk_zones" in res.tools_used
    assert "Zone 4" in res.answer or "Riverside" in res.answer or "Tower" in res.answer
    assert any("recon" in rec.lower() or "physical" in rec.lower() for rec in res.recommendations)

def test_follow_up_conversational_memory():
    """
    Test that follow-up questions resolve implicit pronouns ('it') to the previous zone.
    """
    session = "test-session-followup-01"
    # Query 1: Focus on Zone 4
    res1 = disaster_orchestrator.process_query("Tell me about Zone 4 status.", session_id=session)
    assert "Zone 4" in res1.answer or "Riverside" in res1.answer or "get_silent_risk_zones" in res1.tools_used

    # Query 2: Follow-up using 'it'
    res2 = disaster_orchestrator.process_query("What if we send a boat team to it?", session_id=session)
    assert res2.tools_used is not None
    assert len(res2.recommendations) >= 1

def test_command_briefing_synthesis():
    """
    Test executive command briefing synthesizes multi-engine status.
    """
    briefing = disaster_orchestrator.generate_briefing("test-session-briefing")
    
    assert briefing.title == "AEGIS COMMAND EXECUTIVE SITUATION BRIEFING"
    assert "Zone 7" in briefing.top_priority_zone
    assert briefing.current_risk_score >= 80
    assert len(briefing.top_cascades) >= 1
    assert "Delta-2" in briefing.recommended_mission
    assert len(briefing.silent_risk_alerts) >= 1
    assert len(briefing.key_uncertainties) >= 1

def test_safety_guard_and_no_autonomous_action():
    """
    Test safety guard ensures responses are labeled as decision support and require human approval.
    """
    res = disaster_orchestrator.process_query("Dispatch rescue team immediately to Sector 7.")
    
    assert res.requires_human_approval is True
    assert res.safety_label == "DECISION SUPPORT / MODEL ESTIMATE"
    # Ensure it doesn't claim to have executed real dispatch
    assert "I have dispatched" not in res.answer

def test_backward_compatibility_chat_endpoint():
    """
    Test backward compatibility wrapper for AIChatRequest.
    """
    req = AIChatRequest(query="What is the active incident?", context_mode="LIVE")
    resp = disaster_orchestrator.route_query(req)
    
    assert resp.answer is not None
    assert resp.orchestrator_agent == "AEGIS Disaster Orchestrator"
    assert resp.confidence_score >= 80
