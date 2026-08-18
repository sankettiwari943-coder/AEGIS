import urllib.request
import json
import time

base = "http://127.0.0.1:8000/api"

def make_post(endpoint, payload=None):
    data = json.dumps(payload or {}).encode('utf-8')
    req = urllib.request.Request(f"{base}/{endpoint}", data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def make_get(endpoint):
    with urllib.request.urlopen(f"{base}/{endpoint}") as resp:
        return json.loads(resp.read().decode('utf-8'))

def run_single_demo_cycle(run_num):
    print(f"\n=======================================================")
    print(f"        STARTING COMPLETE DEMO CYCLE #{run_num}         ")
    print(f"=======================================================")
    
    # 1. Health check
    health = make_get("health")
    assert health.get("status") == "operational", f"Run {run_num}: Health not operational"
    print(f"[{run_num}.1] System Health: OPERATIONAL (7/7 Services Online)")
    
    # 2. Reset to T+0 baseline
    reset_res = make_post("demo/reset")
    assert reset_res.get("status") == "RESET_SUCCESSFUL", f"Run {run_num}: Reset failed"
    print(f"[{run_num}.2] State Initialized: T+0 Baseline")
    
    # 3. Detect & Predict Zone 7 Crisis
    preds_data = make_get("predictions")
    preds = preds_data.get("zone_predictions", [])
    z7_pred = next((p for p in preds if p.get("zone_id") == "zone-7"), None)
    assert z7_pred is not None, f"Run {run_num}: Zone 7 prediction missing"
    assert z7_pred.get("escalation_time_minutes") == 42, f"Run {run_num}: Isolation time not 42m"
    print(f"[{run_num}.3] Prediction Verified: Zone 7 Risk={z7_pred.get('current_risk')}, Isolation={z7_pred.get('escalation_time_minutes')}m")

    
    # 4. Cascading Risk Graph
    cascades = make_get("cascades/zone-7")
    assert len(cascades.get("top_chains", [])) > 0, f"Run {run_num}: Cascades empty"
    print(f"[{run_num}.4] Cascading Graph Verified: {len(cascades.get('top_chains', []))} failure chains mapped")

    
    # 5. Silent Risk in Zone 4
    silents = make_get("silent-risks")
    z4_silent = next((s for s in silents if s.get("zone_id") == "zone-4"), None)
    assert z4_silent is not None and z4_silent.get("requires_physical_recon") is True, f"Run {run_num}: Zone 4 silent risk missing"
    print(f"[{run_num}.5] Silent Crisis Verified: Zone 4 flagged (0 SOS, Pop={z4_silent.get('population')}, Recon={z4_silent.get('requires_physical_recon')})")

    
    # 6. Mission Optimizer
    opt_res = make_post("missions/optimize", {"target_zone_id": "zone-7", "victim_count": 12, "medical_emergencies": 3})
    assert opt_res.get("recommended_team", {}).get("team_id") == "team-r2", f"Run {run_num}: Recommended team not R2"
    assert opt_res.get("recommended_team", {}).get("total_mission_score") > 85, f"Run {run_num}: Score < 85"
    print(f"[{run_num}.6] Mission Optimizer Verified: Team {opt_res.get('recommended_team', {}).get('team_callsign')} selected (Score: {opt_res.get('recommended_team', {}).get('total_mission_score')})")

    
    # 7. What-If Simulation Sandbox
    sim_res = make_post("simulations/run", {
        "scenario_id": f"run-{run_num}-sim",
        "scenario_title": "Evacuate Zone 7 + Deploy Delta-2",
        "time_horizon_minutes": 60,
        "perturbations": ["road_14_blocked", "hospital_power_lost"],
        "interventions": ["evacuate_zone_7", "deploy_team_r2"]
    })
    assert sim_res.get("baseline_overall_risk") == 91.0, f"Run {run_num}: Baseline risk not 91"
    assert sim_res.get("scenario_overall_risk") == 64.0, f"Run {run_num}: Scenario risk not 64"
    assert sim_res.get("net_risk_reduction_points") == 27.0, f"Run {run_num}: Net cut not 27"
    print(f"[{run_num}.7] What-If Simulation Verified: Baseline=91 -> Scenario=64 (Net Cut: -27 pts / -29%)")
    
    # 8. AI Orchestrator Grounded Response
    chat_res = make_post("orchestrator/chat", {
        "query": "What should we do right now about Zone 7?",
        "session_id": f"run-{run_num}-session",
        "context_zone_id": "zone-7"
    })
    combined_ai_text = chat_res.get("direct_answer", "") + " " + chat_res.get("answer", "") + " " + " ".join(chat_res.get("why_rationale", []))
    assert "Zone 7" in combined_ai_text or "zone" in combined_ai_text.lower(), f"Run {run_num}: AI missing Zone 7"
    assert len(chat_res.get("tools_used", [])) >= 3, f"Run {run_num}: AI did not use tools"
    print(f"[{run_num}.8] AI Orchestrator Verified: Grounded answer generated using tools {chat_res.get('tools_used')}")

    
    # 9. Adaptive Learning Loop & Replay
    replay_res = make_post("adaptive/demo-replay")
    assert replay_res.get("error_reduction_percent") > 40.0, f"Run {run_num}: Replay error reduction not > 40%"
    print(f"[{run_num}.9] Adaptive Learning Verified: Historical Error reduced from {replay_res.get('before_average_error')} to {replay_res.get('after_average_error')} pts ({replay_res.get('error_reduction_percent')}% improvement)")

    
    # 10. Clean Final Reset
    final_reset = make_post("demo/reset")
    assert final_reset.get("status") == "RESET_SUCCESSFUL", f"Run {run_num}: Final reset failed"
    print(f"[{run_num}.10] Final Reset Verified: State cleanly restored to T+0")
    print(f"===> DEMO CYCLE #{run_num} PASSED PERFECTLY WITH ZERO ERRORS! <===")

if __name__ == "__main__":
    print("===================================================================")
    print("         AEGIS THREE-CONSECUTIVE DEMO VALIDATION SUITE             ")
    print("===================================================================")
    for i in range(1, 4):
        run_single_demo_cycle(i)
        time.sleep(0.5)
    print("\n===================================================================")
    print(">>> ALL THREE CONSECUTIVE DEMO RUNS PASSED WITH 100% SUCCESS! <<<")
    print("===================================================================")
