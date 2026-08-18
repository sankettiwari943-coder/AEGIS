import urllib.request
import json

base = "http://127.0.0.1:8000/api"

print("--- 1. Testing POST /api/missions/optimize ---")
req = urllib.request.Request(f"{base}/missions/optimize?target_zone_id=zone-7&victim_count=12&medical_emergencies=3", method="POST")
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    mission_id = data["mission_id"]
    print(f"Mission ID: {mission_id}")
    print(f"Recommended Team: {data['recommended_team']['callsign']} (Score: {data['recommended_team']['total_mission_score']})")
    print(f"Why Not Closest Team: {data.get('closest_team_comparison', {}).get('comparison_narrative')}")

print("\n--- 2. Testing GET /api/missions/recommendations (Fleet Allocation) ---")
with urllib.request.urlopen(f"{base}/missions/recommendations") as resp:
    fleet = json.loads(resp.read().decode())
    print(f"Plan ID: {fleet['plan_id']}")
    print(f"Assigned Missions: {len(fleet['assigned_missions'])}")
    for m in fleet["assigned_missions"]:
        print(f" - {m['target_zone_name']}: {m['recommended_team']['callsign']} (Score: {m['recommended_team']['total_mission_score']})")

print("\n--- 3. Testing POST /api/missions/{id}/modify ---")
mod_body = json.dumps({"team_id": "team-r1"}).encode()
req_mod = urllib.request.Request(f"{base}/missions/{mission_id}/modify", data=mod_body, headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req_mod) as resp:
    mod_data = json.loads(resp.read().decode())
    print(f"Modified Assigned Team: {mod_data['recommended_team']['callsign']} (Score: {mod_data['recommended_team']['total_mission_score']})")

print("\n--- 4. Testing POST /api/missions/{id}/approve ---")
app_body = json.dumps({"team_id": "team-r2"}).encode()
req_app = urllib.request.Request(f"{base}/missions/{mission_id}/approve", data=app_body, headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req_app) as resp:
    app_data = json.loads(resp.read().decode())
    print(f"Status: {app_data['status']}")
    print(f"Dispatch Status: {app_data.get('dispatch_status')}")
    print(f"Message: {app_data.get('message')}")

print("\n--- 5. Testing GET /api/missions ---")
with urllib.request.urlopen(f"{base}/missions") as resp:
    all_missions = json.loads(resp.read().decode())
    print(f"Total Logged Missions: {len(all_missions)}")

print("\n>>> ALL API VERIFICATION TESTS COMPLETED SUCCESSFULLY! <<<")
