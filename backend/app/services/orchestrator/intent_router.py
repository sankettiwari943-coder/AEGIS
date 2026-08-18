import re
from typing import Tuple, List, Optional

class IntentRouter:
    """
    Classifies operator queries into structured intents and selects appropriate internal AEGIS engine tools.
    """
    def __init__(self):
        pass

    def route_intent(
        self,
        query: str,
        context_zone_id: Optional[str] = None
    ) -> Tuple[str, List[str], Optional[str]]:
        """
        Returns (intent_name, list_of_tool_names, resolved_zone_id).
        """
        q = query.lower()

        # Extract zone mention if present
        zone_match = re.search(r"zone[ -]?(\d+)|z[ -]?0?(\d+)|sector[ -]?(\d+)", q)
        extracted_zone = None
        if zone_match:
            num = zone_match.group(1) or zone_match.group(2) or zone_match.group(3)
            extracted_zone = f"zone-{int(num)}"
        resolved_zone = extracted_zone or context_zone_id or "zone-7"

        # 0. RAG / SOP / Doctrine / Protocol Query
        if any(w in q for w in ["sop", "doctrine", "protocol", "guideline", "manual", "triage standard", "evacuation order", "guidelines"]):
            return "RAG_SOP_QUERY", [
                "query_emergency_knowledge_base",
                "get_prediction",
                "get_current_situation"
            ], resolved_zone

        # 0.1 Computer Vision / Drone / Satellite Scan Query
        if any(w in q for w in ["drone", "satellite", "aerial", "image", "scan", "computer vision", "cv", "flir", "sar", "camera"]):
            return "CV_QUERY", [
                "get_cv_flood_analysis",
                "get_evidence",
                "get_prediction"
            ], resolved_zone

        # 1. Command Briefing Request
        if any(w in q for w in ["briefing", "command briefing", "executive summary", "situation report", "sitrep"]):
            return "BRIEFING_REQUEST", [
                "get_current_situation",
                "get_prediction",
                "get_cascading_risks",
                "get_mission_recommendations",
                "query_emergency_knowledge_base",
                "get_cv_flood_analysis",
                "get_silent_risk_zones",
                "get_prediction_performance",
                "run_simulation"
            ], resolved_zone


        # 2. Adaptive Learning / Accuracy / Calibration Query
        if any(w in q for w in [
            "learn", "learned", "learning", "accuracy", "accurate", "calibration", "recalibration",
            "prediction performance", "how accurate", "error", "outcomes", "recalibrate", "feedback"
        ]):
            return "ADAPTIVE_QUERY", [
                "get_prediction_performance",
                "get_adaptive_insights",
                "get_calibrations"
            ], resolved_zone


        # 2. Silent Risk / Unreported Area Query / Zone 4 Specific
        if any(w in q for w in [
            "silent", "not reporting", "aren't reporting", "arent reporting", "no report",
            "blackout", "unmonitored", "without signal", "blindspot", "silent crisis", "silent risk"
        ]) or (("zone 4" in q or "z-04" in q or "sector 4" in q) and not any(w in q for w in ["what if", "simulate", "team r", "which team"])):
            return "SILENT_RISK_QUERY", [
                "get_silent_risk_zones",
                "get_evidence",
                "get_current_situation"
            ], "zone-4"

        # 3. Simulation / What-If Query
        if any(w in q for w in ["what if", "what happens if", "do nothing", "simulate", "simulation", "evacuate", "compare"]):
            return "SIMULATION_QUERY", [
                "run_simulation",
                "get_resource_status",
                "get_prediction"
            ], resolved_zone

        # 4. Mission / Rescue Query
        if any(w in q for w in ["which team", "team r2", "team r1", "delta-2", "guardian-4", "who should respond", "send", "rescue team", "deploy", "dispatch"]):
            return "MISSION_QUERY", [
                "get_mission_recommendations",
                "get_resource_status",
                "get_prediction"
            ], resolved_zone

        # 5. Cascading Risk Query
        if any(w in q for w in ["cascade", "cascading", "getting worse", "secondary", "power failure", "pump", "chain", "ripple"]):
            return "CASCADE_QUERY", [
                "get_cascading_risks",
                "get_prediction",
                "get_active_alerts"
            ], resolved_zone

        # 6. Evidence / Conflict / Uncertainty Query
        if any(w in q for w in ["evidence", "why do you think", "why is zone", "why is sector", "dangerous", "is the bridge", "uncertain", "conflict", "contradict", "trust"]):
            return "EVIDENCE_QUERY", [
                "get_evidence",
                "get_prediction",
                "get_cascading_risks"
            ], resolved_zone

        # 7. Prediction Query
        if any(w in q for w in ["what happens next", "next hour", "predict", "prediction", "trajectory", "future", "escalat", "isolation"]):
            return "PREDICTION_QUERY", [
                "get_prediction",
                "get_current_situation",
                "get_active_alerts"
            ], resolved_zone

        # 8. Resource Inventory Query
        if any(w in q for w in ["resource", "how many team", "available", "inventory", "generator", "boat", "assets"]):
            return "RESOURCE_QUERY", [
                "get_resource_status",
                "get_mission_recommendations"
            ], resolved_zone

        # 9. Current Situation Query
        if any(w in q for w in ["what is happening", "what's happening", "status", "situation", "overview", "prioritize", "priority", "which area", "which zone"]):
            return "SITUATION_QUERY", [
                "get_current_situation",
                "get_prediction",
                "get_active_alerts",
                "get_mission_recommendations"
            ], resolved_zone

        # Default Fallback
        return "GENERAL_HELP", [
            "get_current_situation",
            "get_prediction",
            "get_mission_recommendations"
        ], resolved_zone

intent_router = IntentRouter()
