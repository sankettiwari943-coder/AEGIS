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
print("       PHASE 9: ADAPTIVE RESPONSE & LEARNING LOOP VERIFICATION     ")
print("===================================================================")

# 1. Test GET /api/adaptive/status
print("\n--- 1. Testing GET /api/adaptive/status ---")
status = make_get("adaptive/status")
print(f"Status: {status.get('status')}")
print(f"Overall Accuracy: {status.get('overall_accuracy_percent')}%")
print(f"Total Evaluated: {status.get('total_evaluated_predictions')}")
print(f"Most Unreliable: {status.get('most_unreliable_metric')}")
print(f"Most Reliable: {status.get('most_reliable_metric')}")
assert status.get("total_evaluated_predictions") >= 20

# 2. Test GET /api/adaptive/performance
print("\n--- 2. Testing GET /api/adaptive/performance ---")
perf = make_get("adaptive/performance")
print(f"Overall Accuracy Ratio: {perf.get('overall_accuracy')}")
print(f"Trend: {perf.get('trend')}")
print(f"Total Metrics Evaluated: {len(perf.get('metrics', []))}")
for m in perf.get("metrics", []):
    print(f"  - {m['label']}: Accuracy {m['accuracy_percent']}%, Avg Error {m['bias']:+.1f} pts [{m['status']}]")
assert len(perf.get("metrics", [])) >= 3

# 3. Test GET /api/adaptive/calibrations
print("\n--- 3. Testing GET /api/adaptive/calibrations ---")
calibs = make_get("adaptive/calibrations")
print(f"Total Calibration Factors: {len(calibs)}")
for c in calibs:
    print(f"  - {c['label']}: Sample Count={c['sample_count']}, Bias={c['bias']}, Applied Adjustment={c['applied_adjustment']:+.1f} pts [{c['status']}]")
assert any(c["metric"] == "road_accessibility" for c in calibs)

# 4. Test GET /api/adaptive/insights
print("\n--- 4. Testing GET /api/adaptive/insights ---")
insights = make_get("adaptive/insights")
print(f"Total Actionable Insights: {len(insights)}")
for ins in insights:
    print(f"  * {ins['title']}: {ins['recommendation']}")
assert len(insights) >= 3

# 5. Test POST /api/adaptive/demo-replay
print("\n--- 5. Testing POST /api/adaptive/demo-replay (Before vs After Demo) ---")
demo = make_post("adaptive/demo-replay")
print(f"Metric: {demo.get('metric')}")
print(f"Before Average Error: {demo.get('before_average_error')} pts")
print(f"After Average Error: {demo.get('after_average_error')} pts")
print(f"Error Reduction: -{demo.get('error_reduction_points')} pts ({demo.get('error_reduction_percent')}%)")
print(f"Demo Message: {demo.get('message')}")
assert demo.get("after_average_error") < demo.get("before_average_error")

# 6. Test GET /api/adaptive/history (Audit Trail)
print("\n--- 6. Testing GET /api/adaptive/history ---")
history = make_get("adaptive/history")
print(f"Audit Trail Events Count: {len(history)}")
for h in history[:3]:
    print(f"  [{h['timestamp']}] {h['event_type']} on {h['metric']}: {h['reason']} (Samples: {h['evidence_count']})")
assert len(history) >= 1

# 7. Test POST /api/feedback (Submit Human Observation)
print("\n--- 7. Testing POST /api/feedback ---")
fb_payload = {
    "metric": "road_accessibility",
    "target_zone_id": "zone-7",
    "predicted_value": 70.0,
    "actual_value": 35.0,
    "source": "Operator Observation",
    "notes": "Route flooded by secondary backwater surge."
}
fb_res = make_post("feedback", fb_payload)
print(f"Feedback ID: {fb_res.get('feedback_id')}")
print(f"Summary: {fb_res.get('recalibration_summary')}")
print(f"Updated Confidence: {fb_res.get('updated_model_confidence_pct')}%")
assert fb_res.get("status") == "RECALIBRATION_RECORDED"

# 8. Test Prediction Engine Calibration Layer Output
print("\n--- 8. Testing Prediction Engine Calibration Layer Output ---")
preds = make_get("predictions")
zone7_pred = next((z for z in preds.get("zone_predictions", []) if z.get("zone_id") == "zone-7"), None)
assert zone7_pred is not None
print(f"Zone 7 Calibration Layer:")
print(f"  Base Estimate: {zone7_pred.get('calibration', {}).get('base_estimate')}%")
print(f"  Calibration Adjustment: {zone7_pred.get('calibration', {}).get('calibration_adjustment')} pts")
print(f"  Calibrated Estimate: {zone7_pred.get('calibration', {}).get('calibrated_estimate')}%")
print(f"  Calibration Basis: {zone7_pred.get('calibration', {}).get('calibration_basis')}")

# 9. Test Orchestrator Learning Query: "What has AEGIS learned?"
print("\n--- 9. Testing Orchestrator Query: 'What has AEGIS learned?' ---")
orch_q1 = make_post("orchestrator/chat", {"query": "What has AEGIS learned?", "session_id": "verify-session-p9"})
print(f"Direct Answer: {orch_q1.get('direct_answer')}")
print(f"Tools Used: {orch_q1.get('tools_used')}")
print(f"Facts: {orch_q1.get('facts')}")
print(f"Deep Links: {[d['label'] for d in orch_q1.get('deep_links', [])]}")
assert "VIEW ADAPTIVE" in [d["label"] for d in orch_q1.get("deep_links", [])]

# 10. Test Orchestrator Query: "How accurate have our predictions been?"
print("\n--- 10. Testing Orchestrator Query: 'How accurate have our predictions been?' ---")
orch_q2 = make_post("orchestrator/chat", {"query": "How accurate have our predictions been?", "session_id": "verify-session-p9"})
print(f"Direct Answer: {orch_q2.get('direct_answer')}")
print(f"Why Rationale: {orch_q2.get('why_rationale')}")

print("\n===================================================================")
print(">>> ALL 10 PHASE 9 ADAPTIVE LEARNING LOOP TESTS PASSED! <<<")
print("===================================================================")
