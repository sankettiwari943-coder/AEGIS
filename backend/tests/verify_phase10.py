import urllib.request
import json

base = "http://127.0.0.1:8000/api"

def make_post(endpoint, payload=None):
    data = json.dumps(payload or {}).encode('utf-8')
    req = urllib.request.Request(f"{base}/{endpoint}", data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def make_get(endpoint):
    with urllib.request.urlopen(f"{base}/{endpoint}") as resp:
        return json.loads(resp.read().decode('utf-8'))

print("===================================================================")
print("       PHASE 10: AEGIS INTEGRATION & DEMO MODE VERIFICATION        ")
print("===================================================================")

# 1. Test GET /api/health
print("\n--- 1. Testing GET /api/health ---")
health = make_get("health")
print(f"Status: {health.get('status')}")
print(f"Mode: {health.get('mode')}")
print(f"Services: {health.get('services')}")
assert health.get("status") == "operational"
assert health.get("services", {}).get("ai") == "healthy"
assert health.get("services", {}).get("simulation") == "healthy"

# 2. Test GET /api/demo/state
print("\n--- 2. Testing GET /api/demo/state ---")
demo_state = make_get("demo/state")
print(f"Event: {demo_state.get('title')}")
print(f"Intensity: {demo_state.get('intensity')}")
print(f"Timeline Steps: {len(demo_state.get('timeline_steps', []))}")
for s in demo_state.get("timeline_steps", []):
    print(f"  * {s['time']}: Zone 7 Risk={s['zone7_risk']}, Isolation Horizon={s['zone7_isolation_minutes']}m, Road={s['road_accessibility_pct']}%, Telecom={s['telecom_pct']}%")
assert len(demo_state.get("timeline_steps", [])) == 4

# 3. Test POST /api/demo/reset
print("\n--- 3. Testing POST /api/demo/reset ---")
reset_res = make_post("demo/reset")
print(f"Reset Status: {reset_res.get('status')}")
print(f"Message: {reset_res.get('message')}")
print(f"Active Zones: {reset_res.get('active_zones_count')}")
assert reset_res.get("status") == "RESET_SUCCESSFUL"

# 4. Test Orchestrator Briefing & Grounding
print("\n--- 4. Testing POST /api/orchestrator/briefing ---")
briefing = make_post("orchestrator/briefing", {"session_id": "phase10-test-session"})
print(f"Briefing Title: {briefing.get('title')}")
print(f"Top Priority Zone: {briefing.get('top_priority_zone')}")
print(f"Recommended Mission: {briefing.get('recommended_mission')} (Score: {briefing.get('mission_score')}/100)")
print(f"Simulation Summary: {briefing.get('simulation_summary')}")
assert "Zone 7" in briefing.get("top_priority_zone", "")

# 5. Test Live Simulation Run for Deep Link Scenario
print("\n--- 5. Testing POST /api/simulations/run (What-If Deep Link) ---")
sim_res = make_post("simulations/run", {
    "scenario_id": "phase10-demo-sim",
    "scenario_title": "Evacuate Zone 7 + Deploy Delta-2",
    "time_horizon_minutes": 60,
    "perturbations": ["road_14_blocked", "hospital_power_lost"],
    "interventions": ["evacuate_zone_7", "deploy_team_r2"]
})

print(f"Baseline Overall Risk: {sim_res.get('baseline_overall_risk')}")
print(f"Scenario Overall Risk: {sim_res.get('scenario_overall_risk')}")
print(f"Net Risk Reduction: -{sim_res.get('net_risk_reduction_points')} pts ({sim_res.get('net_risk_reduction_percent')}%)")
assert sim_res.get("net_risk_reduction_points") > 15

print("\n===================================================================")
print(">>> ALL PHASE 10 BACKEND INTEGRATION & DEMO MODE TESTS PASSED! <<<")
print("===================================================================")
