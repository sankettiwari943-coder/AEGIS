import urllib.request
import json

base = "http://127.0.0.1:8000/api"

print("--- 1. Testing GET /api/simulations/interventions ---")
with urllib.request.urlopen(f"{base}/simulations/interventions") as resp:
    catalog = json.loads(resp.read().decode())
    print(f"Catalog items loaded: {len(catalog)}")
    for item in catalog[:3]:
        print(f" - {item['id']}: {item['name']} ({item['benefit_summary']})")

print("\n--- 2. Testing GET /api/simulations/inventory ---")
with urllib.request.urlopen(f"{base}/simulations/inventory") as resp:
    inv = json.loads(resp.read().decode())
    print(f"Inventory: Teams={inv['available_rescue_teams']}, Medics={inv['available_medical_units']}, Gen={inv['available_generators']}")

print("\n--- 3. Testing POST /api/simulations (Baseline: Do Nothing) ---")
base_req = json.dumps({
    "scenario_title": "Do Nothing Baseline",
    "time_horizon": 60,
    "perturbations": ["road_14_blocked", "hospital_power_lost"],
    "interventions": []
}).encode()
req = urllib.request.Request(f"{base}/simulations", data=base_req, headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req) as resp:
    res_base = json.loads(resp.read().decode())
    print(f"Baseline Overall Risk: {res_base['baseline_overall_risk']}")
    print(f"Simulated Risk: {res_base['scenario_overall_risk']}")
    print(f"Risk Reduction: {res_base['net_risk_reduction_points']} pts")

print("\n--- 4. Testing POST /api/simulations (Compound: Evacuate Z7 + Deploy Delta-2) ---")
opt_req = json.dumps({
    "scenario_title": "Scenario D: Evacuate Z7 + Deploy Delta-2",
    "time_horizon": 60,
    "perturbations": ["road_14_blocked", "hospital_power_lost"],
    "interventions": ["evacuate_zone_7", "deploy_team_r2"]
}).encode()
req_opt = urllib.request.Request(f"{base}/simulations", data=opt_req, headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req_opt) as resp:
    res_opt = json.loads(resp.read().decode())
    print(f"Scenario ID: {res_opt['scenario_id']}")
    print(f"Baseline Risk: {res_opt['baseline_overall_risk']}")
    print(f"Simulated Risk: {res_opt['scenario_overall_risk']}")
    print(f"Estimated Risk Reduction: {res_opt['net_risk_reduction_points']} pts ({res_opt['net_risk_reduction_percent']}%)")
    print(f"Efficiency Score: {res_opt['efficiency_score']} pts/asset")
    print(f"Recommended Best Action: {res_opt['best_preventive_action']}")
    print("Why bullets:")
    for b in res_opt.get("why_bullets", []):
        print(f"  {b}")
    opt_scenario_id = res_opt['scenario_id']

print("\n--- 5. Testing POST /api/simulations/compare (Leaderboard) ---")
cmp_req = json.dumps({"time_horizon": 60}).encode()
req_cmp = urllib.request.Request(f"{base}/simulations/compare", data=cmp_req, headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req_cmp) as resp:
    ranking = json.loads(resp.read().decode())
    print(f"Ranked Scenarios Count: {len(ranking['scenarios'])}")
    for s in ranking['scenarios']:
        print(f" Rank #{s['rank']}: {s['title']} -> Risk: {s['overall_risk']}, Cut: -{s['risk_reduction_points']} pts, Eff: {s['efficiency_score']}")

print("\n--- 6. Testing POST /api/simulations/{id}/apply-to-missions (Bridge to Mission Center) ---")
req_apply = urllib.request.Request(f"{base}/simulations/{opt_scenario_id}/apply-to-missions", method="POST")
with urllib.request.urlopen(req_apply) as resp:
    apply_res = json.loads(resp.read().decode())
    print(f"Status: {apply_res['status']}")
    print(f"Staged Mission ID: {apply_res.get('mission_id')}")
    print(f"Target Zone: {apply_res.get('target_zone_id')}")
    print(f"Message: {apply_res.get('message')}")

print("\n--- 7. Testing GET /api/simulations (History) ---")
with urllib.request.urlopen(f"{base}/simulations") as resp:
    history = json.loads(resp.read().decode())
    print(f"History Log Count: {len(history)}")

print("\n>>> ALL PHASE 7 WHAT-IF SIMULATOR ENDPOINTS VERIFIED SUCCESSFULLY! <<<")
