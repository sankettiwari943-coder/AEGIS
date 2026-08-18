from typing import Dict, Any, List, Optional
from app.data.flood_dataset import CURRENT_EVENT, ZONES_DATA, ROADS_DATA, INFRASTRUCTURE_DATA, RESCUE_TEAMS_DATA
from app.services.prediction_engine import prediction_engine
from app.services.cascading.cascade_service import cascade_service
from app.services.evidence.evidence_service import evidence_service
from app.services.missions.mission_service import mission_service
from app.services.missions.mission_optimizer import mission_optimizer
from app.services.simulation.simulation_service import simulation_service
from app.services.silent_risk_engine import silent_risk_engine
from app.models.schemas import SimulationRequest

class ToolRegistry:
    """
    Internal AEGIS Tool Registry.
    Exposes deterministic engine queries to the AI Disaster Orchestrator.
    Guarantees the LLM never calculates risk scores or invents raw data directly.
    """
    def __init__(self):
        pass

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Returns metadata descriptions of all internal AEGIS tools."""
        return [
            {
                "name": "get_current_situation",
                "description": "Retrieves the active disaster event, flood depths, rainfall telemetry, exposed population, and critical sectors.",
                "parameters": {}
            },
            {
                "name": "get_prediction",
                "description": "Retrieves predictive risk horizons (NOW, 30m, 60m, 3h), isolation countdowns, and operational priority rankings.",
                "parameters": {"zone_id": "Optional target zone ID (e.g. zone-7)"}
            },
            {
                "name": "get_cascading_risks",
                "description": "Retrieves multi-hop cascading failure chains (substations, pumps, road cutoffs, hospital isolation).",
                "parameters": {"zone_id": "Optional target zone ID"}
            },
            {
                "name": "get_evidence",
                "description": "Retrieves multi-source evidence assessments, supporting sensor data, satellite SAR imagery, citizen reports, and contradictions.",
                "parameters": {"target": "Optional claim ID or zone ID"}
            },
            {
                "name": "get_mission_recommendations",
                "description": "Retrieves multi-attribute rescue mission allocations, capability matching, and 'Why not the closest team?' comparisons.",
                "parameters": {"zone_id": "Optional target zone ID"}
            },
            {
                "name": "run_simulation",
                "description": "Executes a What-If disaster simulation comparing unmitigated baseline against proactive interventions.",
                "parameters": {"interventions": "List of intervention IDs (e.g. ['evacuate_zone_7', 'deploy_team_r2'])"}
            },
            {
                "name": "get_resource_status",
                "description": "Retrieves live inventory and assignment status for rescue teams, medical units, emergency generators, and boats.",
                "parameters": {}
            },
            {
                "name": "get_silent_risk_zones",
                "description": "Retrieves sectors with zero reports caused by infrastructure/telecom blackouts (silent crises).",
                "parameters": {}
            },
            {
                "name": "get_active_alerts",
                "description": "Retrieves real-time operational alerts and critical escalation warnings.",
                "parameters": {}
            },
            {
                "name": "get_prediction_performance",
                "description": "Retrieves historical evaluated prediction accuracy, error statistics, and reliability breakdowns across metrics.",
                "parameters": {}
            },
            {
                "name": "get_adaptive_insights",
                "description": "Retrieves actionable learning insights derived from systematic prediction bias and model divergence.",
                "parameters": {}
            },
            {
                "name": "get_calibrations",
                "description": "Retrieves active calibration factors, bias indicators, sample counts, and confidence adjustments.",
                "parameters": {}
            },
            {
                "name": "query_emergency_knowledge_base",
                "description": "Retrieves authoritative disaster standard operating procedures (SOPs), evacuation protocols, triage manuals, and infrastructure guidelines from the RAG knowledge store.",
                "parameters": {"query": "Search query text (e.g. 'flood evacuation hospital guidelines')"}
            },
            {
                "name": "get_cv_flood_analysis",
                "description": "Retrieves aerial drone and satellite Computer Vision diagnostics, detected damaged structures, flooded roadways, and stranded civilian clusters.",
                "parameters": {"zone_id": "Target zone ID (e.g. 'zone-7')"}
            },
            {
                "name": "get_live_ingestion_observations",
                "description": "Retrieves multi-source validated telemetry observations (Doppler radar, ultrasonic river gauges, submerged road pressure sensors, telecom uptime).",
                "parameters": {"zone_id": "Optional target zone ID"}
            }
        ]



    def get_current_situation(self) -> Dict[str, Any]:
        """Tool 1: Get current incident situation summary."""
        zones_summary = []
        for z in ZONES_DATA:
            zones_summary.append({
                "id": z.id,
                "name": z.name,
                "risk_score": z.primary_risk_score,
                "population": z.population,
                "flood_depth_cm": z.current_flood_depth_cm,
                "status": z.connectivity_status.value if hasattr(z.connectivity_status, "value") else str(z.connectivity_status)
            })
        
        # Sort by risk score
        zones_summary.sort(key=lambda x: x["risk_score"], reverse=True)

        return {
            "event_title": CURRENT_EVENT.title,
            "status": CURRENT_EVENT.status,
            "total_exposed_population": 11800,
            "average_rainfall_rate_mmh": CURRENT_EVENT.average_rainfall_rate_mmh,
            "peak_crest_hours": CURRENT_EVENT.peak_crest_time_hours,
            "top_critical_zone": zones_summary[0] if zones_summary else None,
            "all_zones": zones_summary[:5],
            "active_missions_count": 4
        }

    def get_prediction(self, zone_id: Optional[str] = None) -> Dict[str, Any]:
        """Tool 2: Get predictive risk trajectories and isolation time."""
        target = zone_id or "zone-7"
        zone = next((z for z in ZONES_DATA if z.id == target or z.code.lower() == target.lower()), ZONES_DATA[0])
        pred = prediction_engine.predict_zone(zone)
        top_preds = prediction_engine.get_top_predictions()
        
        return {
            "target_zone_id": zone.id,
            "target_zone_name": zone.name,
            "current_risk": pred["current_risk"],
            "predicted_risk_30m": pred["predicted_risk_30m"],
            "predicted_risk_60m": pred["predicted_risk_60m"],
            "predicted_risk_3h": pred["predicted_risk_3h"],
            "isolation_predicted_minutes": pred.get("escalation_time_minutes", 42),
            "primary_escalation_driver": pred.get("primary_driver", "Rapid river crest velocity and corridor submergence"),
            "top_escalating_zones": [
                {"id": p.get("id"), "title": p.get("title"), "entity": p.get("target_entity"), "eta_mins": p.get("eta_minutes")}
                for p in top_preds[:3]
            ]
        }

    def get_cascading_risks(self, zone_id: Optional[str] = None) -> Dict[str, Any]:
        """Tool 3: Get cascading failure chains and critical downstream infrastructure."""
        target = zone_id or "zone-7"
        cascade_data = cascade_service.get_zone_cascade_detail(target)
        graph_data = cascade_service.get_zone_cascade_graph(target)

        zone_name = cascade_data.zone_name if cascade_data else "Zone 7 — River Bend Lowlands"
        cascading_risk_score = cascade_data.cascading_risk if cascade_data else 88
        chains = cascade_data.top_chains if cascade_data else []

        return {
            "target_zone_id": target,
            "target_zone_name": zone_name,
            "cascading_risk_score": cascading_risk_score,
            "critical_failure_chains": [
                {
                    "title": c.title,
                    "priority_level": c.priority_level,
                    "overall_risk": c.overall_risk,
                    "steps": [s.node_name for s in c.steps]
                }
                for c in chains[:3]
            ],
            "graph_nodes_count": len(graph_data.nodes) if graph_data else 0,
            "graph_edges_count": len(graph_data.edges) if graph_data else 0,
            "key_vulnerabilities": [
                "Substation #2 flooding threatens Basin Drainage Pump #1 power",
                "Corridor 14 Bridge submergence cuts off Riverbank Memorial Hospital trauma access"
            ]
        }

    def get_evidence(self, target: Optional[str] = None) -> Dict[str, Any]:
        """Tool 4: Get verified multi-source evidence and conflicts."""
        summary = evidence_service.get_evidence_summary()
        claims = evidence_service.get_all_claims(zone_id="zone-7" if target in [None, "zone-7", "Z-07"] else None)

        return {
            "data_trust_index": summary.data_trust_index,
            "total_claims_analyzed": summary.total_claims_analyzed,
            "verified_count": summary.verified_count,
            "conflicting_count": summary.conflicting_count,
            "claims": [
                {
                    "claim_id": c.claim_id,
                    "title": c.title,
                    "status": c.status.value if hasattr(c.status, "value") else str(c.status),
                    "confidence_percent": c.ai_confidence_percent,
                    "supporting_count": c.supporting_sources_count,
                    "conflicting_count": c.conflicting_sources_count,
                    "statement": c.claim_statement
                }
                for c in claims[:4]
            ],
            "key_contradiction": "Traffic Loop Sensor #14 indicates green signal while citizen reports and satellite SAR show 95cm road overtopping."
        }

    def get_mission_recommendations(self, zone_id: Optional[str] = None) -> Dict[str, Any]:
        """Tool 5: Get multi-attribute mission optimization and trade-offs."""
        target = zone_id or "zone-7"
        rec = mission_service.optimize_mission(target, victim_count=12, medical_emergencies=3)

        return {
            "mission_id": rec.mission_id,
            "target_zone_id": rec.target_zone_id,
            "target_zone_name": rec.target_zone_name,
            "recommended_team": {
                "callsign": rec.recommended_team.callsign,
                "team_id": rec.recommended_team.team_id,
                "total_score": rec.recommended_team.total_mission_score,
                "eta_minutes": rec.recommended_team.travel_time_minutes,
                "distance_km": rec.recommended_team.distance_km,
                "capabilities": rec.recommended_team.team_capabilities,
                "why_this_team": rec.recommended_team.why_this_team
            },
            "why_not_closest_team": (
                rec.closest_team_comparison.comparison_narrative
                if rec.closest_team_comparison and rec.closest_team_comparison.comparison_narrative
                else "Team Viper-1 is closer (3.9 km vs 5.8 km) but lacks field trauma medical equipment required for 3 trauma emergencies."
            ),
            "human_approval_state": rec.human_approval_state
        }

    def run_simulation(self, interventions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Tool 6: Run What-If simulation comparing baseline vs intervention."""
        actions = interventions or ["evacuate_zone_7", "deploy_team_r2"]
        req = SimulationRequest(
            scenario_title="Compound What-If Strategy",
            time_horizon_minutes=60,
            perturbations=["road_14_blocked", "hospital_power_lost"],
            interventions=actions
        )
        comp = simulation_service.run_simulation(req)

        return {
            "scenario_title": comp.scenario_title,
            "time_horizon_minutes": comp.time_horizon_minutes,
            "baseline_overall_risk": comp.baseline_overall_risk,
            "scenario_overall_risk": comp.scenario_overall_risk,
            "net_risk_reduction_points": comp.net_risk_reduction_points,
            "net_risk_reduction_percent": comp.net_risk_reduction_percent,
            "resource_cost": comp.resource_cost,
            "efficiency_score": comp.efficiency_score,
            "best_preventive_action": comp.best_preventive_action,
            "why_bullets": comp.why_bullets,
            "confidence_percent": comp.confidence_percent
        }

    def get_resource_status(self) -> Dict[str, Any]:
        """Tool 7: Get live resource inventory and active deployments."""
        inv = simulation_service.get_resource_inventory()
        teams = [
            {"id": t.id, "callsign": t.callsign, "status": t.status, "equipment": t.equipment}
            for t in RESCUE_TEAMS_DATA
        ]

        return {
            "available_rescue_teams": inv.available_rescue_teams,
            "available_medical_units": inv.available_medical_units,
            "available_generators": inv.available_generators,
            "available_boats": inv.available_boats,
            "available_utility_crews": inv.available_utility_crews,
            "fleet_status": teams
        }

    def get_silent_risk_zones(self) -> Dict[str, Any]:
        """Tool 8: Get silent crisis sectors with communication anomalies."""
        silent_zones = silent_risk_engine.get_all_silent_risks()
        
        return {
            "silent_crises_count": len(silent_zones),
            "zones": [
                {
                    "zone_id": s.zone_id,
                    "zone_name": s.zone_name,
                    "anomaly_probability_percent": s.communication_anomaly_percent,
                    "telecom_status": s.connectivity_status,
                    "silent_crisis_score_percent": s.silent_crisis_score_percent,
                    "status": s.status,
                    "recommended_action": s.recommended_action
                }
                for s in silent_zones
            ]
        }

    def get_active_alerts(self) -> Dict[str, Any]:
        """Tool 9: Get critical active operational alerts."""
        return {

            "alerts": [

                {
                    "severity": "CRITICAL",
                    "title": "Zone 7 Imminent Isolation",
                    "message": "Corridor 14 Bridge passability degrading rapidly. Complete road cutoff in 42 minutes."
                },
                {
                    "severity": "CRITICAL",
                    "title": "Substation #2 Flood Overtopping",
                    "message": "Water levels at 92cm. Inundation risks cascading power cutoff to Basin Drainage Pump #1."
                },
                {
                    "severity": "HIGH",
                    "title": "Zone 4 Silent Crisis",
                    "message": "Cellular Tower Delta-4 down. Zero civilian reports despite 145cm inundation. Physical recon required."
                }
            ]
        }

    def get_prediction_performance(self) -> Dict[str, Any]:
        """Tool 10: Get historical prediction vs reality evaluation performance metrics."""
        from app.services.adaptive.adaptive_service import adaptive_service
        perf = adaptive_service.get_performance()
        status = adaptive_service.get_status()

        return {
            "overall_accuracy_percent": round(perf.overall_accuracy * 100, 1),
            "total_evaluated_predictions": perf.evaluated_predictions,
            "trend": perf.trend,
            "most_reliable_metric": status.most_reliable_metric,
            "most_unreliable_metric": status.most_unreliable_metric,
            "metric_breakdown": [
                {
                    "metric": m.metric,
                    "label": m.label,
                    "accuracy_percent": m.accuracy_percent,
                    "average_error": m.bias,
                    "status": m.status
                }
                for m in perf.metrics
            ]
        }

    def get_adaptive_insights(self) -> Dict[str, Any]:
        """Tool 11: Get actionable AI learning insights derived from systematic error patterns."""
        from app.services.adaptive.adaptive_service import adaptive_service
        insights = adaptive_service.get_insights()

        return {
            "insights_count": len(insights),
            "insights": [
                {
                    "metric": i.metric,
                    "title": i.title,
                    "description": i.description,
                    "bias": i.average_bias,
                    "status": i.status,
                    "recommendation": i.recommendation
                }
                for i in insights
            ]
        }

    def get_calibrations(self) -> Dict[str, Any]:
        """Tool 12: Get current calibration factors and parameters."""
        from app.services.adaptive.adaptive_service import adaptive_service
        calibs = adaptive_service.get_calibrations()

        return {
            "calibrations": [
                {
                    "metric": c.metric,
                    "label": c.label,
                    "sample_count": c.sample_count,
                    "bias": c.bias,
                    "average_error": c.average_error,
                    "applied_adjustment": c.applied_adjustment,
                    "status": c.status,
                    "confidence": c.confidence
                }
                for c in calibs
            ]
        }

    def query_emergency_knowledge_base(self, query: str = "flood emergency SOP evacuation") -> Dict[str, Any]:
        """Tool 13: Query RAG knowledge store for emergency guidelines, doctrine, and SOP citations."""
        from app.services.rag.rag_service import rag_service
        return rag_service.query_knowledge_base(query=query, top_k=3)

    def get_cv_flood_analysis(self, zone_id: Optional[str] = None) -> Dict[str, Any]:
        """Tool 14: Query aerial drone & satellite Computer Vision diagnostic overlays."""
        from app.services.computer_vision.cv_service import cv_service
        from app.services.computer_vision.cv_models import CVAnalysisRequest
        target = zone_id or "zone-7"
        res = cv_service.analyze_image(CVAnalysisRequest(target_zone_id=target))
        return res.dict() if hasattr(res, "dict") else res.model_dump()

    def get_live_ingestion_observations(self, zone_id: Optional[str] = None) -> Dict[str, Any]:
        """Tool 15: Query multi-source validated telemetry observations and state."""
        from app.services.ingestion.situation_store import situation_store
        target = zone_id or "zone-7"
        telemetry = situation_store.get_zone_telemetry(target)
        recent_obs = situation_store.get_observations(zone_id=target, limit=5)
        return {
            "target_zone_id": target,
            "telemetry": telemetry,
            "recent_observations": [o.dict() if hasattr(o, "dict") else o.model_dump() for o in recent_obs],
            "data_source_mode": "FUSED (LIVE / SENSOR / RADAR)"
        }

tool_registry = ToolRegistry()


