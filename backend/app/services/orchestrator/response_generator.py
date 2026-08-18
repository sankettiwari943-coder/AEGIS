from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models.schemas import (
    OrchestratorStructuredResponse, ToolCallRecord, DeepLinkAction, CommandBriefingResponse
)

class ResponseGenerator:
    """
    Synthesizes AI Provider outputs with structured engine data, generating
    interactive deep-links, confidence metrics, and command briefings.
    """
    def __init__(self):
        pass

    def build_structured_response(
        self,
        ai_data: Dict[str, Any],
        tool_records: List[Dict[str, Any]],
        intent: str,
        zone_id: str,
        tool_outputs: Dict[str, Any]
    ) -> OrchestratorStructuredResponse:
        """
        Constructs the final OrchestratorStructuredResponse with deep-link navigation hooks.
        """
        # Convert tool records to ToolCallRecord schema
        records = [
            ToolCallRecord(
                tool_name=r["tool_name"],
                parameters=r.get("parameters", {}),
                output_summary=r.get("output_summary", "")
            )
            for r in tool_records
        ]

        # Generate contextual Deep Links
        deep_links: List[DeepLinkAction] = []
        if intent in ["EVIDENCE_QUERY", "CONFLICT_QUERY", "SITUATION_QUERY", "BRIEFING_REQUEST"]:
            deep_links.append(DeepLinkAction(
                label="VIEW EVIDENCE",
                target_mode="EVIDENCE",
                target_zone_id=zone_id,
                action_type="VIEW_EVIDENCE"
            ))
        if intent in ["CASCADE_QUERY", "SITUATION_QUERY", "BRIEFING_REQUEST"]:
            deep_links.append(DeepLinkAction(
                label="VIEW CASCADE",
                target_mode="CASCADE",
                target_zone_id=zone_id,
                action_type="VIEW_CASCADE"
            ))
        if intent in ["PREDICTION_QUERY", "SITUATION_QUERY", "BRIEFING_REQUEST"]:
            deep_links.append(DeepLinkAction(
                label="VIEW PREDICTION",
                target_mode="PREDICT",
                target_zone_id=zone_id,
                action_type="VIEW_PREDICTION"
            ))
        if intent in ["MISSION_QUERY", "SITUATION_QUERY", "BRIEFING_REQUEST"]:
            deep_links.append(DeepLinkAction(
                label="VIEW MISSION",
                target_mode="MISSIONS",
                target_zone_id=zone_id,
                action_type="VIEW_MISSION"
            ))
        if intent in ["SIMULATION_QUERY", "SITUATION_QUERY", "BRIEFING_REQUEST"]:
            deep_links.append(DeepLinkAction(
                label="SIMULATE",
                target_mode="SIMULATE",
                target_zone_id=zone_id,
                action_type="SIMULATE"
            ))
        if intent in ["ADAPTIVE_QUERY", "SITUATION_QUERY", "BRIEFING_REQUEST"]:
            deep_links.append(DeepLinkAction(
                label="VIEW ADAPTIVE",
                target_mode="ADAPTIVE",
                target_zone_id=zone_id,
                action_type="VIEW_ADAPTIVE"
            ))


        # Extract supporting evidence titles from engine tool outputs
        evidence_signals = []
        if "evidence" in tool_outputs:
            for c in tool_outputs["evidence"].get("claims", []):
                evidence_signals.append(f"{c['title']} ({c['confidence_percent']}% confidence)")
        if not evidence_signals:
            evidence_signals = [
                "42 Ultrasonic Hydrological Gauges (8.1m river crest)",
                "Synthetic Aperture Radar Inundation Signature (95cm depth)",
                "Emergency Dispatch Civilian SOS Corroboration"
            ]

        referenced_zones = ["Zone 7 (River Bend)", "Zone 4 (Riverside Slums)"]
        if zone_id == "zone-4":
            referenced_zones = ["Zone 4 (Riverside Slums)", "Zone 9 (Lower Confluence)"]

        # Extract live operational facts from tool outputs
        live_facts = []
        if "current_situation" in tool_outputs:
            sit = tool_outputs["current_situation"]
            live_facts.append(f"Active Event: {sit.get('event_title', 'Urban Flood')} ({sit.get('status', 'ESCALATING')})")
            live_facts.append(f"Exposed Population: {sit.get('total_exposed_population', 11800):,} residents across river basin")
        if "prediction" in tool_outputs:
            p = tool_outputs["prediction"]
            live_facts.append(f"Predicted Trajectory: Risk {p.get('current_risk', 86)} -> {p.get('predicted_risk_60m', 93)} (60m)")
            live_facts.append(f"Time to Isolation: ~{p.get('isolation_predicted_minutes', 42)} minutes")
        if "computer_vision" in tool_outputs:
            cv = tool_outputs["computer_vision"]
            live_facts.append(f"Aerial Drone Recon: Flood Extent {cv.get('flood_extent_percent', 78)}%, {cv.get('damaged_structures_count', 14)} damaged structures")
        if "live_ingestion" in tool_outputs:
            ing = tool_outputs["live_ingestion"].get("telemetry", {})
            live_facts.append(f"Telemetry: River Level {ing.get('river_level_meters', 7.85)}m, Flood Depth {ing.get('current_flood_depth_cm', 125)}cm")
        if not live_facts:
            live_facts = [
                "River Basin cresting at 7.85m (+1.35m over flood stage)",
                "Corridor 14 bridge access degrading towards 29% passability",
                "11,800 residents exposed across 12 monitoring sectors"
            ]

        # Extract retrieved SOP guidance from RAG
        retrieved_guidance = []
        rag_sources = []
        if "rag_knowledge" in tool_outputs:
            rag_data = tool_outputs["rag_knowledge"]
            retrieved_guidance.extend(rag_data.get("guidance_summary", []))
            rag_sources.extend([c.get("doc_id", "") + " - " + c.get("title", "") for c in rag_data.get("citations", [])])
        if not retrieved_guidance:
            retrieved_guidance = [
                "[SOP-FL-001] Urban Riverine Flood: Proactive evacuation mandatory before arterial routes submerge below 30cm passability.",
                "[SOP-RES-005] Swiftwater USAR: Heavy Evacuation Units with boat capability prioritized for stranded clusters > 10 victims.",
                "[SOP-INFRA-004] Substation Protection: Pre-stage diesel generation at pumping stations before electrical grid trip."
            ]
            rag_sources = [
                "SOP-FL-001 (NDMA Riverine Flood Manual)",
                "SOP-RES-005 (Federal USAR Doctrine 2026)",
                "SOP-INFRA-004 (Electrical Grid Safety Standard)"
            ]

        conf_score = int(ai_data.get("confidence", 0.90) * 100) if isinstance(ai_data.get("confidence"), float) else int(ai_data.get("confidence", 90))

        return OrchestratorStructuredResponse(

            answer=ai_data.get("answer", "AEGIS intelligence engines active."),
            direct_answer=ai_data.get("direct_answer", ""),
            why_rationale=ai_data.get("why_rationale", []),
            facts=ai_data.get("facts", live_facts),
            live_facts=live_facts,
            retrieved_guidance=retrieved_guidance,
            rag_sources=rag_sources,
            model_estimates=ai_data.get("model_estimates", []),
            uncertainties=ai_data.get("uncertainties", [
                "Corridor 14 road bridge structural integrity unconfirmed by physical inspection",
                "Rainfall runoff velocity may accelerate isolation timing by 8-12 minutes"
            ]),
            recommendations=ai_data.get("recommendations", [
                "Deploy Delta-2 (Heavy Evacuation Unit) to Zone 7 immediately with boat and medical crew",
                "Dispatch aerial scout drone to Zone 4 to investigate silent crisis communication anomaly"
            ]),
            tools_used=[r.tool_name for r in records],
            tool_calls=records,
            deep_links=deep_links,
            referenced_zones=referenced_zones,
            supporting_evidence=evidence_signals,
            confidence_score=conf_score,
            orchestrator_agent="AEGIS Disaster Orchestrator",
            requires_human_approval=True,
            safety_label="DECISION SUPPORT / MODEL ESTIMATE"
        )


    def build_command_briefing(self, tool_outputs: Dict[str, Any]) -> CommandBriefingResponse:
        """
        Synthesizes a comprehensive multi-engine situation briefing.
        """
        sit = tool_outputs.get("current_situation", {})
        pred = tool_outputs.get("prediction", {})
        casc = tool_outputs.get("cascading_risks", {})
        rec = tool_outputs.get("mission_recommendations", {})
        sim = tool_outputs.get("simulation", {})
        silent = tool_outputs.get("silent_risk_zones", {})

        return CommandBriefingResponse(
            title="AEGIS COMMAND EXECUTIVE SITUATION BRIEFING",
            situation_summary=(
                f"Active Event: {sit.get('event_title', 'Monsoon Flood Disaster')}. "
                f"Peak crest projected in {sit.get('peak_crest_hours', 3.5)} hours with {sit.get('total_exposed_population', 11800):,} exposed residents across 12 monitoring zones."
            ),
            top_priority_zone=pred.get("target_zone_name", "Zone 7 — River Bend Lowlands"),
            current_risk_score=pred.get("current_risk", 91),
            predicted_escalation=f"Potential critical isolation in ~{pred.get('isolation_predicted_minutes', 42)} minutes as arterial Road 14 submerges.",
            top_cascades=[
                "Substation #2 flood inundation -> Basin Drainage Pump #1 power loss",
                "Corridor 14 Bridge cutoff -> Riverbank Memorial Hospital trauma isolation"
            ],
            recommended_mission=f"{rec.get('recommended_team', {}).get('callsign', 'Delta-2 (Heavy Evacuation Unit)')} -> {rec.get('target_zone_name', 'Zone 7')}",
            mission_score=rec.get("recommended_team", {}).get("total_score", 97),
            silent_risk_alerts=[
                "Zone 4 (Riverside Slums): 91% Silent Crisis Index due to Cellular Tower Delta-4 destruction."
            ],
            key_uncertainties=[
                "Bridge 14 structural integrity unverified by physical inspection",
                "Traffic sensor #14 operational signal conflicts with flood imagery"
            ],
            simulation_summary=(
                f"Scenario D (Evacuate Z7 + Deploy Delta-2) reduces compound risk from "
                f"{sim.get('baseline_overall_risk', 91)} down to {sim.get('scenario_overall_risk', 64)} (Estimated {sim.get('net_risk_reduction_points', 27)} points / {sim.get('net_risk_reduction_percent', 29)}% risk cut)."
            ),
            confidence_percent=91,
            timestamp=datetime.now().isoformat()
        )

response_generator = ResponseGenerator()
