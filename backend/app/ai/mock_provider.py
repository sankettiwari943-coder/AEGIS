import json
from typing import Dict, Any, Optional
from app.ai.provider import BaseAIProvider

class MockAIProvider(BaseAIProvider):
    """
    Deterministic High-Fidelity Mock AI Provider for Hackathon Demos and Offline Testing.
    Returns grounded, explainable operational reasoning without external API dependencies.
    """
    def __init__(self):
        pass

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        res = self.generate_structured(prompt, system_prompt)
        return res.get("answer", "AEGIS Tactical Orchestrator standing by.")

    def generate_structured(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        p_lower = prompt.lower()
        
        # Extract the user's specific query if prompt was built with "OPERATOR QUERY: ..."
        op_query = p_lower
        if "operator query:" in p_lower:
            op_query = p_lower.split("operator query:")[1].split("\n")[0].strip()

        # 1. Adaptive Learning / Accuracy / Recalibration Query
        if any(w in op_query for w in [
            "what has aegis learned", "what have you learned", "what did you learn",
            "what has been learned", "learned", "learning", "how accurate", "accuracy",
            "prediction performance", "performance", "calibration", "recalibration", "recalibrate"
        ]):
            return {
                "answer": "AEGIS Adaptive Intelligence has identified a systematic underestimation of road network deterioration during peak river surges. Across 24 evaluated outcomes in the demo dataset, overall predictive accuracy is 82%. Hospital trauma access models remain highly calibrated (89% accuracy, STABLE), while Road Network Accessibility exhibits an average bias of -9.4 points (UNDERPREDICTING). AEGIS has applied a -8.0 point calibration factor to future road estimates and updated confidence to 74%.",
                "direct_answer": "AEGIS evaluated accuracy is 82%. System has detected systematic road deterioration underprediction and recommended -8.0 pts calibration.",
                "why_rationale": [
                    "12 evaluated observations reveal persistent -9.4 pt underprediction of road degradation during peak flood crests",
                    "Hospital trauma ward accessibility remains stable at 89% accuracy within ±5% tolerance",
                    "Mission travel times reflect +4.0 min hydrological drag calibration factor",
                    "Sector isolation model has 4 observations (insufficient data for full recalibration, minimum 5 required)"
                ],
                "facts": [
                    "24 total evaluated demo observations",
                    "Overall evaluated dataset accuracy: 82%",
                    "Most reliable metric: Hospital Access (89%)",
                    "Least reliable metric: Road Access (68%)"
                ],
                "model_estimates": [
                    "Base Zone 7 road accessibility: 34% (MODEL ESTIMATE)",
                    "Calibrated road accessibility: 26% (CALIBRATED ESTIMATE)",
                    "Recalibrated confidence: 74%"
                ],
                "uncertainties": [
                    "Sector isolation timeline model has only 4 evaluated observations (5 required for statistical calibration)"
                ],
                "recommendations": [
                    "Inspect calibration audit trail on the /adaptive dashboard",
                    "Pre-position heavy amphibious rescue assets to Zone 7 before arterial cutoff"
                ],
                "confidence": 0.88
            }

        # 2. Silent Risk Query
        elif any(w in op_query for w in [
            "silent", "not reporting", "aren't reporting", "arent reporting", "no report",
            "blackout", "unreported", "blindspot", "zone 4"
        ]):

            return {
                "answer": "Silent Risk Analysis identifies Zone 4 (Riverside Slums & Wetlands) at 91% Silent Crisis Probability. Telemetry indicates Cellular Tower Delta-4 suffered catastrophic power loss, resulting in 0 civilian SOS calls despite 9,300 residents residing in 145cm deep floodwaters. The absence of reports reflects total communication cutoff rather than safety.",
                "direct_answer": "Zone 4 has severe silent crisis probability (91%) due to cellular tower destruction.",
                "why_rationale": [
                    "0 SOS reports received despite 145cm deep flood inundation",
                    "Cellular Tower Delta-4 telemetry confirms total grid failure",
                    "High vulnerability population density (9,300 residents)"
                ],
                "facts": [
                    "Zone 4 population: 9,300",
                    "Flood depth: 145 cm",
                    "Incoming call volume: 0 calls/hr"
                ],
                "model_estimates": [
                    "Silent Crisis Index: 91% (MODEL ESTIMATE)"
                ],
                "uncertainties": [
                    "Exact victim count inside unmonitored slum corridors"
                ],
                "recommendations": [
                    "Immediately dispatch physical swiftwater recon unit (Bravo-5 Zodiac Squad)",
                    "Establish emergency temporary mesh radio relay"
                ],
                "confidence": 0.93
            }

        # 2. Simulation / What-If Query
        elif any(w in op_query for w in ["what if", "simulate", "simulation", "do nothing", "evacuate", "compare"]):
            return {
                "answer": "What-If Simulation indicates that doing nothing results in compound disaster risk escalating to 91 across the 60-minute horizon. Conversely, executing Scenario D (Evacuate Zone 7 + Deploy Delta-2) reduces simulated future risk down to 64, delivering an estimated risk reduction of 27 points (29.7%) and protecting 2,840 high-vulnerability residents.",
                "direct_answer": "Scenario D (Evacuation + Delta-2 Deployment) delivers the optimal outcome with a 27-point risk reduction.",
                "why_rationale": [
                    "Preemptive evacuation cuts exposed population from 11,800 to 8,900",
                    "Deploying Delta-2 stabilizes 3 trauma patients and bypasses severed roads",
                    "Compound synergy achieves 9.0 points risk reduction per asset utilized"
                ],
                "facts": [
                    "Resource cost: 3 assets (2 rescue teams + 1 trauma unit)"
                ],
                "model_estimates": [
                    "Baseline risk: 91 (SIMULATION)",
                    "Intervention risk: 64 (SIMULATION)",
                    "Estimated risk reduction: 27 points (MODEL ESTIMATE)"
                ],
                "uncertainties": [
                    "Evacuation compliance rate modeled at 85%"
                ],
                "recommendations": [
                    "Apply Scenario D to the Mission Plan in the Mission Center"
                ],
                "confidence": 0.88
            }

        # 3. Mission Query
        elif any(w in op_query for w in ["which team", "team r2", "team r1", "delta-2", "guardian-4", "rescue team", "deploy", "who should respond", "send"]):
            return {
                "answer": "The Mission Optimizer recommends deploying Team Delta-2 (Heavy Evacuation Unit) to Zone 7 (Mission Score: 97/100, ~12 min ETA). Although Team Viper-1 is physically closer (3.9 km vs 5.8 km), Viper-1 lacks field medical trauma kits. Zone 7 has 3 critical trauma emergencies in deep water (95 cm), making Delta-2's medical and boat capabilities decisively higher in survival impact (97 vs 88 pts).",
                "direct_answer": "Deploy Team Delta-2 (Heavy Evacuation Unit) to Zone 7.",
                "why_rationale": [
                    "Delta-2 has certified flood rescue boat + advanced trauma paramedic crew",
                    "Zone 7 has 3 critical medical trauma patients and 95cm flood depths",
                    "Closer Team Viper-1 rejected due to lack of trauma capability"
                ],
                "facts": [
                    "Zone 7 victims: 12 (3 medical emergencies)",
                    "Delta-2 capacity: 15 seats",
                    "Delta-2 ETA: 12 minutes"
                ],
                "model_estimates": [
                    "Mission utility score: 97/100 (MODEL ESTIMATE)"
                ],
                "uncertainties": [
                    "Submerged debris along secondary waterways"
                ],
                "recommendations": [
                    "Review and approve simulated dispatch for Delta-2 in Mission Center"
                ],
                "confidence": 0.94
            }

        # 4. Cascading Risk Query
        elif any(w in op_query for w in ["cascade", "cascading", "why is this getting worse", "secondary risk", "power failure", "pump", "chain"]):
            return {
                "answer": "Primary surface inundation is triggering compound secondary failures. In Zone 6/7, floodwaters (92cm) are threatening Electrical Substation #2. Substation failure will trip Basin Drainage Pump #1, causing severe backwater accumulation on Road 14 and cutting off Riverbank Memorial Hospital's trauma ward.",
                "direct_answer": "Substation #2 flood inundation risks cascading to basin drainage pumps and hospital isolation.",
                "why_rationale": [
                    "Flood Inundation → Substation #2 Blackout → Pump #1 Failure → Backwater Flood Surge",
                    "Corridor 14 Road Cutoff → Hospital Trauma Access Blocked → Paramedic Response Delay"
                ],
                "facts": [
                    "Substation Delta-2 water level: 92 cm",
                    "Pump #1 currently at 40% efficiency"
                ],
                "model_estimates": [
                    "Compound cascading vulnerability score: 88/100 (MODEL ESTIMATE)"
                ],
                "uncertainties": [
                    "Emergency diesel generator startup latency at hospital"
                ],
                "recommendations": [
                    "Deploy sandbag barriers to Substation #2",
                    "Dispatch mobile 500kW diesel generator to Pump #1"
                ],
                "confidence": 0.92
            }

        # 5. Evidence / Verification / Why Zone 7 Query
        elif any(w in op_query for w in ["evidence", "why is zone 7", "why zone 7", "why is zone", "why zone", "dangerous", "bridge", "claim", "conflict", "uncertain"]):
            return {
                "answer": "Zone 7 high-risk classification is supported by multiple independent evidence layers (91% confidence): 42 ultrasonic river sensor readings confirming 8.1m river stage, synthetic aperture satellite inundation imagery (95cm depth), and 17 corroborated citizen emergency reports. One minor contradiction exists: automated traffic loop sensor #14 remains operational, though physical road overtopping is confirmed.",
                "direct_answer": "Zone 7 danger is heavily corroborated by sensors, satellite SAR imagery, and civilian reports.",
                "why_rationale": [
                    "42 physical river sensors confirm critical crest",
                    "Satellite SAR radar shows 95cm low-lying water depth",
                    "17 civilian SOS reports corroborated by emergency dispatch"
                ],
                "facts": [
                    "Sensor confidence: 96%",
                    "Data trust index: 88%"
                ],
                "model_estimates": [
                    "Synthesized AI claim confidence: 91% (MODEL ESTIMATE)"
                ],
                "uncertainties": [
                    "Traffic sensor #14 operational status conflicts with flood overtopping reports (UNVERIFIED)"
                ],
                "recommendations": [
                    "Maintain high alert and prioritize rescue operations",
                    "Conduct physical drone check of Bridge 14"
                ],
                "confidence": 0.91
            }

        # 6. Prediction Query
        elif any(w in op_query for w in ["what happens next", "next hour", "escalat", "predict", "prediction", "trajectory", "future", "42 minutes", "critical"]):
            return {
                "answer": "Predictive models estimate continued systemic deterioration over the next 60 minutes. Zone 7 (River Bend) will reach total road isolation within approximately 42 minutes as Corridor 14 submerges completely. Flood risk will surge from 82 to 94 in 60 minutes, while Riverbank Memorial Hospital accessibility drops from 61% down to 34%.",
                "direct_answer": "Critical deterioration projected within 42 minutes for Zone 7.",
                "why_rationale": [
                    "Upstream dam discharge velocity is adding +0.4m/hr to river crest",
                    "Lowland topography causes water pooling along arterial access roads",
                    "Hospital transport corridors will be fully impassable by +60m"
                ],
                "facts": [
                    "Current Zone 7 risk: 82",
                    "Hospital accessibility currently: 61%"
                ],
                "model_estimates": [
                    "Predicted 30m risk: 89 (MODEL ESTIMATE)",
                    "Predicted 60m risk: 93 (MODEL ESTIMATE)",
                    "Isolation timeline: 42 minutes"
                ],
                "uncertainties": [
                    "Rainfall surge intensity could vary by +/- 15%"
                ],
                "recommendations": [
                    "Preemptively evacuate before the 42-minute isolation window closes"
                ],
                "confidence": 0.89
            }

        # 7. Situation Query
        elif any(w in op_query for w in ["what is happening", "what's happening", "situation", "current state", "prioritize", "overview"]):
            return {
                "answer": "Flood conditions are worsening rapidly across the northern river basin sectors. Zone 7 (River Bend Lowlands) has reached critical operational risk (91/100) with rapid road degradation, 145cm flood depths, and 3 trapped medical emergencies. Overall 11,800 residents are currently exposed across monitored sectors with 4 simulated rescue missions deployed.",
                "direct_answer": "Severe river basin flash flooding in progress. Zone 7 is the primary critical focus sector.",
                "why_rationale": [
                    "River gauge telemetry confirms river stage at 8.1m MSL (cresting in 3.5 hrs)",
                    "Corridor 14 Bridge passability severed by deep floodwaters",
                    "3 critical trauma emergencies awaiting evacuation at River Bend"
                ],
                "facts": [
                    "Monsoon Flood Event active across 12 zones",
                    "Average rainfall rate: 42 mm/h",
                    "11,800 total exposed population"
                ],
                "model_estimates": [
                    "Zone 7 operational risk: 91/100 (MODEL ESTIMATE)",
                    "Potential isolation predicted in ~42 minutes"
                ],
                "uncertainties": [
                    "Bridge 7 structural integrity remains unverified by physical inspection",
                    "Telecom blackout in Zone 4 prevents civilian report confirmation"
                ],
                "recommendations": [
                    "Prioritize immediate evacuation of Zone 7",
                    "Deploy amphibious medical unit Delta-2 to River Bend",
                    "Dispatch physical swiftwater recon to Zone 4"
                ],
                "confidence": 0.91
            }

        # 8. Default Operational Response
        return {
            "answer": "AEGIS Disaster Orchestrator online. Flood conditions are currently worsening in Zone 7 (River Bend, Risk: 91) and Zone 4 (Silent Risk: 91%). The Mission Optimizer recommends deploying Delta-2 to Zone 7, while What-If simulations demonstrate a 27-point risk cut when combining evacuation with active rescue transport.",
            "direct_answer": "AEGIS intelligence engines active across Prediction, Cascades, Evidence, Missions, and What-If Simulation.",
            "why_rationale": [
                "Real-time sensor telemetry and hydrological models integrated",
                "Deterministic decision support active with zero autonomous dispatch"
            ],
            "facts": [
                "12 active monitoring zones",
                "4 active simulation missions"
            ],
            "model_estimates": [
                "Overall basin risk: 78/100 (MODEL ESTIMATE)"
            ],
            "uncertainties": [
                "Long-term weather forecast beyond 3 hours"
            ],
            "recommendations": [
                "Inspect Zone 7 critical alerts",
                "Review Delta-2 mission recommendation"
            ],
            "confidence": 0.90
        }
