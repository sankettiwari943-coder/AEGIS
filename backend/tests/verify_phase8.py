import urllib.request
import json

base = "http://127.0.0.1:8000/api"

def make_post(endpoint, payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f"{base}/{endpoint}", data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def make_get(endpoint):
    with urllib.request.urlopen(f"{base}/{endpoint}") as resp:
        return json.loads(resp.read().decode('utf-8'))

print("===================================================================")
print("             PHASE 8: AI DISASTER ORCHESTRATOR VERIFICATION        ")
print("===================================================================")

# 1. Test GET /api/orchestrator/tools
print("\n--- 1. Testing GET /api/orchestrator/tools ---")
tools = make_get("orchestrator/tools")
print(f"Total internal AEGIS engine tools registered: {len(tools)}")
for t in tools:
    print(f" [OK] Tool: {t['name']} - {t['description'][:60]}...")

assert len(tools) >= 9, "Expected at least 9 tools registered"

# 2. Test Query 1: Situation Query
print("\n--- 2. Testing Query 1: 'What is happening right now?' ---")
q1 = make_post("orchestrator/chat", {"query": "What is happening right now?", "session_id": "verify-session"})
print(f"Direct Answer: {q1.get('direct_answer')}")
print(f"Tools Used: {q1.get('tools_used')}")
print(f"Facts: {q1.get('facts')}")
print(f"Confidence: {q1.get('confidence_score')}%")
print(f"Requires Human Approval: {q1.get('requires_human_approval')}")
assert "get_current_situation" in q1.get("tools_used", []), "get_current_situation not in tools_used"
assert q1.get("requires_human_approval") is True, "Human approval must be required"

# 3. Test Query 2: Prediction Query
print("\n--- 3. Testing Query 2: 'What happens in the next hour?' ---")
q2 = make_post("orchestrator/chat", {"query": "What happens in the next hour?", "session_id": "verify-session"})
print(f"Direct Answer: {q2.get('direct_answer')}")
print(f"Model Estimates: {q2.get('model_estimates')}")
print(f"Tools Used: {q2.get('tools_used')}")
assert "get_prediction" in q2.get("tools_used", []), "get_prediction not in tools_used"

# 4. Test Query 3: Evidence Query
print("\n--- 4. Testing Query 3: 'Why is Zone 7 dangerous?' ---")
q3 = make_post("orchestrator/chat", {"query": "Why is Zone 7 dangerous?", "session_id": "verify-session"})
print(f"Direct Answer: {q3.get('direct_answer')}")
print(f"Why Rationale: {q3.get('why_rationale')}")
print(f"Evidence Signals: {q3.get('supporting_evidence')}")
print(f"Uncertainties: {q3.get('uncertainties')}")
assert "get_evidence" in q3.get("tools_used", []), "get_evidence not in tools_used"

# 5. Test Query 4: Mission Query (Trade-off)
print("\n--- 5. Testing Query 4: 'Which team should go to Zone 7?' ---")
q4 = make_post("orchestrator/chat", {"query": "Which team should go to Zone 7?", "session_id": "verify-session"})
print(f"Direct Answer: {q4.get('direct_answer')}")
print(f"Why Rationale: {q4.get('why_rationale')}")
print(f"Tools Used: {q4.get('tools_used')}")
assert "get_mission_recommendations" in q4.get("tools_used", []), "get_mission_recommendations not in tools_used"

# 6. Test Query 5: Simulation Query
print("\n--- 6. Testing Query 5: 'What happens if we do nothing vs evacuate Zone 7?' ---")
q5 = make_post("orchestrator/chat", {"query": "What happens if we do nothing vs evacuate Zone 7?", "session_id": "verify-session"})
print(f"Direct Answer: {q5.get('direct_answer')}")
print(f"Why Rationale: {q5.get('why_rationale')}")
print(f"Model Estimates: {q5.get('model_estimates')}")
assert "run_simulation" in q5.get("tools_used", []), "run_simulation not in tools_used"

# 7. Test Query 6: Silent Risk Query
print("\n--- 7. Testing Query 6: 'Are there areas where people aren\\'t reporting?' ---")
q6 = make_post("orchestrator/chat", {"query": "Are there areas where people aren't reporting?", "session_id": "verify-session"})
print(f"Direct Answer: {q6.get('direct_answer')}")
print(f"Recommendations: {q6.get('recommendations')}")
print(f"Tools Used: {q6.get('tools_used')}")
assert "get_silent_risk_zones" in q6.get("tools_used", []), "get_silent_risk_zones not in tools_used"

# 8. Test Query 7: Command Briefing
print("\n--- 8. Testing Query 7: POST /api/orchestrator/briefing ---")
briefing = make_post("orchestrator/briefing", {"session_id": "verify-session"})
print(f"Title: {briefing.get('title')}")
print(f"Top Priority Sector: {briefing.get('top_priority_zone')}")
print(f"Current Risk Score: {briefing.get('current_risk_score')}/100")
print(f"Escalation Forecast: {briefing.get('predicted_escalation')}")
print(f"Recommended Mission: {briefing.get('recommended_mission')}")
print(f"Simulation Outcome: {briefing.get('simulation_summary')}")
print(f"Confidence: {briefing.get('confidence_percent')}%")
assert "Zone 7" in briefing.get("top_priority_zone", "")

# 9. Test Follow-up Conversational Memory
print("\n--- 9. Testing Follow-up Conversational Memory ('it' pronoun) ---")
mem_sess = "followup-test-session"
r_step1 = make_post("orchestrator/chat", {"query": "Tell me about Zone 4 status.", "session_id": mem_sess})
print(f"Step 1 (Explicit Zone 4) Answer: {r_step1.get('direct_answer')}")
r_step2 = make_post("orchestrator/chat", {"query": "What if we send a boat team to it?", "session_id": mem_sess})
print(f"Step 2 (Follow-up 'it') Tools: {r_step2.get('tools_used')}")
print(f"Step 2 Recommendations: {r_step2.get('recommendations')}")
assert len(r_step2.get("tools_used", [])) >= 1

# 10. Backward Compatible Chat Endpoint
print("\n--- 10. Testing Legacy POST /api/assistant/chat ---")
legacy = make_post("assistant/chat", {"query": "Give me a quick tactical overview.", "context_mode": "LIVE"})
print(f"Legacy Agent Name: {legacy.get('orchestrator_agent')}")
print(f"Legacy Answer: {legacy.get('answer')[:120]}...")
assert legacy.get("confidence_score") >= 80

print("\n===================================================================")
print(">>> ALL 10 PHASE 8 AI DISASTER ORCHESTRATOR TESTS PASSED! <<<")
print("===================================================================")
