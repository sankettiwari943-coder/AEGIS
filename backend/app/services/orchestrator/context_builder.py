import json
from typing import Dict, Any, List, Optional, Tuple
from app.services.orchestrator.tool_registry import tool_registry, ToolRegistry

class ContextBuilder:
    """
    Manages conversational memory, session context, follow-up pronoun resolution,
    and executes tool requests to build compact context prompts for the LLM.
    """
    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry or tool_registry
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "last_zone_id": "zone-7",
                "last_intent": "SITUATION_QUERY",
                "history": []
            }
        return self.sessions[session_id]

    def resolve_followup_context(
        self,
        query: str,
        session_id: str,
        explicit_zone_id: Optional[str] = None
    ) -> str:
        """
        Resolves implicit pronouns like 'it', 'that sector', 'the area' using session memory.
        """
        session = self.get_or_create_session(session_id)
        if explicit_zone_id:
            session["last_zone_id"] = explicit_zone_id
            return explicit_zone_id

        # If query has implicit pronoun and no explicit zone
        q_lower = query.lower()
        if any(p in q_lower for p in [" it", "that area", "that zone", "that sector", "there"]):
            return session.get("last_zone_id", "zone-7")

        return session.get("last_zone_id", "zone-7")

    def execute_tools_and_build_context(
        self,
        tool_names: List[str],
        zone_id: str,
        query: str,
        session_id: str
    ) -> Tuple[Dict[str, Any], str, List[Dict[str, Any]]]:
        """
        Executes requested tools and formats them into a compact structured payload and prompt text.
        Returns (tool_outputs_dict, formatted_context_text, tool_call_records).
        """
        session = self.get_or_create_session(session_id)
        session["last_zone_id"] = zone_id

        outputs: Dict[str, Any] = {}
        records: List[Dict[str, Any]] = []

        for name in tool_names:
            if name == "get_current_situation":
                res = self.registry.get_current_situation()
                outputs["current_situation"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {},
                    "output_summary": f"Incident: {res['event_title']}, Exposed: {res['total_exposed_population']:,}, Top Zone: {res['top_critical_zone']['name'] if res['top_critical_zone'] else 'None'}"
                })
            elif name == "get_prediction":
                res = self.registry.get_prediction(zone_id)
                outputs["prediction"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {"zone_id": zone_id},
                    "output_summary": f"{res['target_zone_name']}: Risk {res['current_risk']} -> {res['predicted_risk_60m']} (60m), Isolation in ~{res['isolation_predicted_minutes']}m"
                })
            elif name == "get_cascading_risks":
                res = self.registry.get_cascading_risks(zone_id)
                outputs["cascading_risks"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {"zone_id": zone_id},
                    "output_summary": f"Cascading Score: {res['cascading_risk_score']}, Chains: {len(res['critical_failure_chains'])}"
                })
            elif name == "get_evidence":
                res = self.registry.get_evidence(zone_id)
                outputs["evidence"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {"target": zone_id},
                    "output_summary": f"Trust Index: {res['data_trust_index']}%, Claims: {len(res['claims'])}, Verified: {res['verified_count']}"
                })
            elif name == "get_mission_recommendations":
                res = self.registry.get_mission_recommendations(zone_id)
                outputs["mission_recommendations"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {"zone_id": zone_id},
                    "output_summary": f"Recommended: {res['recommended_team']['callsign']} (Score: {res['recommended_team']['total_score']})"
                })
            elif name == "run_simulation":
                res = self.registry.run_simulation()
                outputs["simulation"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {"scenario": "Evacuate Z7 + Deploy Delta-2"},
                    "output_summary": f"Baseline {res['baseline_overall_risk']} -> Sim {res['scenario_overall_risk']} (-{res['net_risk_reduction_points']} pts / {res['net_risk_reduction_percent']}%)"
                })
            elif name == "get_resource_status":
                res = self.registry.get_resource_status()
                outputs["resource_status"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {},
                    "output_summary": f"Available Teams: {res['available_rescue_teams']}, Medics: {res['available_medical_units']}, Gen: {res['available_generators']}"
                })
            elif name == "get_silent_risk_zones":
                res = self.registry.get_silent_risk_zones()
                outputs["silent_risk_zones"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {},
                    "output_summary": f"Silent Crises: {res['silent_crises_count']} sectors flagged"
                })
            elif name == "get_active_alerts":
                res = self.registry.get_active_alerts()
                outputs["active_alerts"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {},
                    "output_summary": f"{len(res['alerts'])} active alerts"
                })
            elif name == "get_prediction_performance":
                res = self.registry.get_prediction_performance()
                outputs["prediction_performance"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {},
                    "output_summary": f"Overall Accuracy: {res['overall_accuracy_percent']}%, Total Evaluated: {res['total_evaluated_predictions']}"
                })
            elif name == "get_adaptive_insights":
                res = self.registry.get_adaptive_insights()
                outputs["adaptive_insights"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {},
                    "output_summary": f"Generated {res['insights_count']} actionable learning insights"
                })
            elif name == "get_calibrations":
                res = self.registry.get_calibrations()
                outputs["calibrations"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {},
                    "output_summary": f"Loaded {len(res['calibrations'])} calibration factors"
                })
            elif name == "query_emergency_knowledge_base":
                res = self.registry.query_emergency_knowledge_base(query=query)
                outputs["rag_knowledge"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {"query": query},
                    "output_summary": f"RAG Retrieved {res['retrieved_count']} SOP guidelines ({res['top_match']['title'] if res['top_match'] else 'None'})"
                })
            elif name == "get_cv_flood_analysis":
                res = self.registry.get_cv_flood_analysis(zone_id)
                outputs["computer_vision"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {"zone_id": zone_id},
                    "output_summary": f"CV Scan: {res['title']} (Flood Extent: {res['flood_extent_percent']}%, Damaged: {res['damaged_structures_count']})"
                })
            elif name == "get_live_ingestion_observations":
                res = self.registry.get_live_ingestion_observations(zone_id)
                outputs["live_ingestion"] = res
                records.append({
                    "tool_name": name,
                    "parameters": {"zone_id": zone_id},
                    "output_summary": f"Telemetry: {len(res['recent_observations'])} recent sensor/radar observations"
                })

        # Format compact prompt context

        context_str = (
            f"OPERATOR QUERY: {query}\n"
            f"FOCUSED SECTOR: {zone_id}\n\n"
            f"STRUCTURED AEGIS ENGINE OUTPUTS:\n"
            f"{json.dumps(outputs, indent=2)}"
        )

        return outputs, context_str, records

context_builder = ContextBuilder()
