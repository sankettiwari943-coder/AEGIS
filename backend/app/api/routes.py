from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from app.models.schemas import (
    DisasterEvent, Zone, RoadSegment, Infrastructure, RescueTeam,
    PredictionResponse, ZoneCascadingRisk, ZoneCascadeDetailResponse,
    ZoneCascadeGraphResponse, CascadeChain, CascadeAlert, SilentRiskAssessment,
    EvidenceClaim, EvidenceItem, ClaimAssessment, DecisionEvidenceTrace,
    EvidenceSummaryResponse, MissionRecommendation, MultiMissionOptimizationPlan,
    MultiMissionOptimizationRequest, MissionModifyRequest,
    SimulationRequest, SimulationComparison, InterventionItem, ResourceInventory,
    MultiScenarioComparisonResponse,
    FeedbackSubmission, FeedbackAnalysisResponse, OutcomeItem, CalibrationItem,
    LearningInsightItem, LearningEventItem, AdaptiveStatusResponse,
    AdaptivePerformanceResponse, CalibrationDemoResponse,
    AIChatRequest, AIChatResponse,
    OrchestratorQueryRequest, OrchestratorStructuredResponse, CommandBriefingResponse
)
from app.data.flood_dataset import (
    CURRENT_EVENT, ZONES_DATA, ROADS_DATA, INFRASTRUCTURE_DATA, RESCUE_TEAMS_DATA
)
from app.services.prediction_engine import prediction_engine
from app.services.cascading.cascade_service import cascade_service
from app.services.cascading_risk_engine import cascading_risk_engine
from app.services.silent_risk_engine import silent_risk_engine
from app.services.evidence.evidence_service import evidence_service
from app.services.evidence_engine import evidence_engine
from app.services.missions.mission_service import mission_service
from app.services.missions.mission_optimizer import mission_optimizer
from app.services.simulation.simulation_service import simulation_service
from app.services.adaptive.feedback_engine import feedback_engine
from app.services.adaptive.adaptive_service import adaptive_service
from app.services.agents.orchestrator import disaster_orchestrator

# Ingestion Services
from app.services.ingestion import (
    situation_store, live_feed_simulator, DisasterObservation, IngestionStatus, LiveFeedStepEvent
)
# RAG Services
from app.services.rag import rag_service
# Computer Vision Services
from app.services.computer_vision import cv_service, CVAnalysisRequest, CVAnalysisResult

router = APIRouter()


# Active disaster event summary
@router.get("/event/current", response_model=DisasterEvent)
def get_current_event():
    return CURRENT_EVENT

# Zones
@router.get("/zones", response_model=List[Zone])
def get_all_zones():
    return ZONES_DATA

@router.get("/zones/{zone_id}", response_model=Zone)
def get_zone_by_id(zone_id: str):
    for z in ZONES_DATA:
        if z.id == zone_id or z.code.lower() == zone_id.lower():
            return z
    raise HTTPException(status_code=404, detail="Zone not found")

# Roads
@router.get("/roads", response_model=List[RoadSegment])
def get_all_roads():
    return ROADS_DATA

# Infrastructure
@router.get("/infrastructure", response_model=List[Infrastructure])
def get_all_infrastructure(zone_id: Optional[str] = None, infra_type: Optional[str] = None):
    results = INFRASTRUCTURE_DATA
    if zone_id:
        results = [i for i in results if i.zone_id == zone_id]
    if infra_type:
        results = [i for i in results if i.type.value == infra_type]
    return results

# Predictions
@router.get("/predictions")
def get_predictions():
    return prediction_engine.get_all_predictions_response()

@router.get("/predictions/top")
def get_top_predictions():
    return prediction_engine.get_top_predictions()

@router.get("/predictions/horizon/{minutes}")
def get_prediction_horizon(minutes: int = 60):
    return prediction_engine.get_horizon_view(minutes)

@router.get("/predictions/{zone_id}")
def get_zone_prediction(zone_id: str):
    for z in ZONES_DATA:
        if z.id == zone_id or z.code.lower() == zone_id.lower():
            return prediction_engine.predict_zone(z)
    raise HTTPException(status_code=404, detail="Zone prediction not found")

# Cascading Risk Intelligence Endpoints
@router.get("/cascades", response_model=List[ZoneCascadeDetailResponse])
def get_all_cascades():
    return cascade_service.get_all_cascade_details()

@router.get("/cascades/top", response_model=List[CascadeChain])
def get_top_cascades(limit: int = 6):
    return cascade_service.get_top_cascading_threats(limit=limit)

@router.get("/cascades/alerts", response_model=List[CascadeAlert])
def get_cascade_alerts():
    return cascade_service.get_all_cascade_alerts()

@router.get("/cascades/{zone_id}", response_model=ZoneCascadeDetailResponse)
def get_zone_cascade(zone_id: str):
    detail = cascade_service.get_zone_cascade_detail(zone_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Cascade assessment for zone '{zone_id}' not found")
    return detail

@router.get("/cascades/{zone_id}/graph", response_model=ZoneCascadeGraphResponse)
def get_zone_cascade_graph(zone_id: str):
    graph = cascade_service.get_zone_cascade_graph(zone_id)
    if not graph:
        raise HTTPException(status_code=404, detail=f"Cascade graph for zone '{zone_id}' not found")
    return graph

# Backward-Compatible Risks Endpoint
@router.get("/risks", response_model=List[ZoneCascadingRisk])
def get_cascading_risks():
    return cascade_service.get_all_cascading_risks()


# Silent Crisis
@router.get("/silent-risks", response_model=List[SilentRiskAssessment])
def get_silent_risks():
    return silent_risk_engine.get_all_silent_risks()

# Truth & Evidence Intelligence Endpoints
@router.get("/evidence", response_model=List[EvidenceItem])
def get_all_evidence(
    zone_id: Optional[str] = None,
    evidence_type: Optional[str] = None,
    status: Optional[str] = None
):
    return evidence_service.get_all_evidence(zone_id=zone_id, evidence_type=evidence_type, status=status)

@router.get("/evidence/summary", response_model=EvidenceSummaryResponse)
def get_evidence_summary():
    return evidence_service.get_evidence_summary()

@router.get("/evidence/claims", response_model=List[ClaimAssessment])
def get_all_claims(
    zone_id: Optional[str] = None,
    status: Optional[str] = None
):
    return evidence_service.get_all_claims(zone_id=zone_id, status=status)

@router.get("/evidence/claims/{claim_id}", response_model=ClaimAssessment)
def get_claim_by_id(claim_id: str):
    claim = evidence_service.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail=f"Evidence claim '{claim_id}' not found")
    return claim

@router.get("/evidence/claims/{claim_id}/sources")
def get_claim_sources(claim_id: str):
    sources = evidence_service.get_claim_sources(claim_id)
    if not sources:
        raise HTTPException(status_code=404, detail=f"Sources for claim '{claim_id}' not found")
    return sources

@router.get("/evidence/claims/{claim_id}/conflicts")
def get_claim_conflicts(claim_id: str):
    return evidence_service.get_claim_conflicts(claim_id)

@router.get("/evidence/decisions/{decision_id}", response_model=DecisionEvidenceTrace)
def get_decision_evidence(decision_id: str):
    trace = evidence_service.get_decision_evidence_chain(decision_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Decision evidence trace for '{decision_id}' not found")
    return trace

@router.get("/evidence/{evidence_id}", response_model=EvidenceItem)
def get_evidence_item_by_id(evidence_id: str):
    item = evidence_service.get_evidence_by_id(evidence_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Evidence item '{evidence_id}' not found")
    return item


# Rescue Teams
@router.get("/teams", response_model=List[RescueTeam])
def get_teams():
    return RESCUE_TEAMS_DATA

# Phase 6: Rescue Mission Optimizer Endpoints
@router.get("/missions", response_model=List[MissionRecommendation])
def get_all_missions():
    return mission_service.get_all_missions()

@router.get("/missions/recommendations", response_model=MultiMissionOptimizationPlan)
def get_mission_recommendations(
    zones: Optional[List[str]] = Query(None),
    teams: Optional[List[str]] = Query(None)
):
    return mission_service.get_fleet_recommendations(zones=zones, available_teams=teams)

@router.get("/missions/{mission_id}", response_model=MissionRecommendation)
def get_mission_by_id(mission_id: str):
    mission = mission_service.get_mission_by_id(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail=f"Mission '{mission_id}' not found")
    return mission

@router.post("/missions/optimize", response_model=MissionRecommendation)
def optimize_mission(
    target_zone_id: str = Query("zone-7"),
    victim_count: int = Query(12),
    medical_emergencies: int = Query(3),
    payload: Optional[Dict[str, Any]] = Body(None)
):
    # Support payload overrides if passed via JSON
    if payload:
        target_zone_id = payload.get("target_zone_id") or payload.get("zone") or target_zone_id
        victim_count = payload.get("victim_count", victim_count)
        medical_emergencies = payload.get("medical_emergencies", medical_emergencies)
    return mission_service.optimize_mission(target_zone_id, victim_count, medical_emergencies)

@router.post("/missions/{mission_id}/approve")
def approve_mission_by_id(mission_id: str, payload: Optional[Dict[str, Any]] = Body(None)):
    team_id = (payload or {}).get("team_id")
    return mission_service.approve_mission(mission_id, team_id=team_id)

@router.post("/missions/approve")
def approve_mission_legacy(payload: Dict[str, Any] = Body(...)):
    mission_id = payload.get("mission_id", "mission-opt-z-07-01")
    team_id = payload.get("team_id")
    return mission_service.approve_mission(mission_id, team_id=team_id)

@router.post("/missions/{mission_id}/modify", response_model=MissionRecommendation)
def modify_mission(mission_id: str, request: MissionModifyRequest):
    return mission_service.modify_mission(mission_id, request)

@router.post("/missions/{mission_id}/dismiss")
def dismiss_mission(mission_id: str):
    return mission_service.dismiss_mission(mission_id)

# Phase 7: What-If Disaster Simulator Endpoints
@router.post("/simulations", response_model=SimulationComparison)
def create_and_run_simulation(request: SimulationRequest):
    return simulation_service.run_simulation(request)

@router.get("/simulations", response_model=List[SimulationComparison])
def get_simulation_history():
    return simulation_service.get_history()

@router.get("/simulations/interventions", response_model=List[InterventionItem])
def get_interventions_catalog():
    return simulation_service.get_interventions()

@router.get("/simulations/inventory", response_model=ResourceInventory)
def get_simulation_resource_inventory():
    return simulation_service.get_resource_inventory()

@router.get("/simulations/{scenario_id}", response_model=SimulationComparison)
def get_simulation_by_id(scenario_id: str):
    sim = simulation_service.get_simulation_by_id(scenario_id)
    if not sim:
        raise HTTPException(status_code=404, detail=f"Simulation scenario '{scenario_id}' not found")
    return sim

@router.post("/simulations/{scenario_id}/run", response_model=SimulationComparison)
def rerun_simulation(scenario_id: str, request: Optional[SimulationRequest] = Body(None)):
    req = request or SimulationRequest(scenario_id=scenario_id, scenario_title=f"Scenario {scenario_id}")
    req.scenario_id = scenario_id
    return simulation_service.run_simulation(req)

@router.post("/simulations/compare", response_model=MultiScenarioComparisonResponse)
def compare_scenarios(
    payload: Optional[Dict[str, Any]] = Body(None),
    time_horizon: int = Query(60)
):
    horizon = (payload or {}).get("time_horizon", time_horizon)
    raw_scenarios = (payload or {}).get("scenarios", [])
    scenario_requests = None
    if raw_scenarios and isinstance(raw_scenarios[0], dict):
        scenario_requests = [SimulationRequest(**s) for s in raw_scenarios]
    return simulation_service.compare_scenarios(time_horizon_minutes=horizon, scenario_requests=scenario_requests)

@router.post("/simulations/{scenario_id}/apply-to-missions")
def apply_simulation_to_mission_plan(scenario_id: str):
    return simulation_service.apply_to_mission_plan(scenario_id)

# Legacy Simulator Endpoints
@router.post("/simulations/run", response_model=SimulationComparison)
def run_simulation_legacy(request: SimulationRequest):
    return simulation_service.run_simulation(request)

# Phase 9: Adaptive Response & Learning Loop Endpoints
@router.post("/feedback", response_model=FeedbackAnalysisResponse)
def submit_feedback(submission: FeedbackSubmission):
    return adaptive_service.submit_feedback(submission)

@router.get("/feedback", response_model=List[FeedbackAnalysisResponse])
def get_feedback_history():
    return feedback_engine.get_history()

@router.get("/feedback/{feedback_id}", response_model=OutcomeItem)
def get_feedback_outcome(feedback_id: str):
    outcomes = adaptive_service.get_outcomes()
    for o in outcomes:
        if o.id == feedback_id or f"fb-{o.id}" == feedback_id:
            return o
    raise HTTPException(status_code=404, detail=f"Feedback outcome {feedback_id} not found")

@router.get("/adaptive/status", response_model=AdaptiveStatusResponse)
def get_adaptive_status():
    return adaptive_service.get_status()

@router.get("/adaptive/performance", response_model=AdaptivePerformanceResponse)
def get_adaptive_performance():
    return adaptive_service.get_performance()

@router.get("/adaptive/calibrations", response_model=List[CalibrationItem])
def get_adaptive_calibrations():
    return adaptive_service.get_calibrations()

@router.get("/adaptive/insights", response_model=List[LearningInsightItem])
def get_adaptive_insights():
    return adaptive_service.get_insights()

@router.post("/adaptive/calibrate", response_model=List[CalibrationItem])
def trigger_adaptive_calibration():
    return adaptive_service.trigger_recalibration()

@router.get("/adaptive/history", response_model=List[LearningEventItem])
def get_adaptive_audit_history():
    return adaptive_service.get_audit_history()

@router.get("/adaptive/outcomes", response_model=List[OutcomeItem])
def get_adaptive_outcomes():
    return adaptive_service.get_outcomes()

@router.post("/adaptive/demo-replay", response_model=CalibrationDemoResponse)
def run_calibration_demo_replay():
    return adaptive_service.run_calibration_demo()


# Phase 8: AI Disaster Orchestrator Endpoints
@router.post("/orchestrator/chat", response_model=OrchestratorStructuredResponse)
def orchestrator_chat(req: OrchestratorQueryRequest):
    query_text = req.query or req.message or "What is the current situation?"
    session_id = req.session_id or "demo-session"
    return disaster_orchestrator.process_query(
        query=query_text,
        session_id=session_id,
        context_zone_id=req.context_zone_id,
        context_mode=req.context_mode
    )

@router.post("/orchestrator/query", response_model=OrchestratorStructuredResponse)
def orchestrator_query(req: OrchestratorQueryRequest):
    query_text = req.query or req.message or "What is the current situation?"
    session_id = req.session_id or "demo-session"
    return disaster_orchestrator.process_query(
        query=query_text,
        session_id=session_id,
        context_zone_id=req.context_zone_id,
        context_mode=req.context_mode
    )

@router.post("/orchestrator/briefing", response_model=CommandBriefingResponse)
def orchestrator_briefing(payload: Optional[Dict[str, Any]] = Body(None)):
    session_id = (payload or {}).get("session_id", "demo-session")
    return disaster_orchestrator.generate_briefing(session_id=session_id)

@router.get("/orchestrator/tools")
def orchestrator_tools():
    return disaster_orchestrator.get_available_tools()

# Backward Compatible Assistant Endpoints
@router.post("/assistant/chat", response_model=AIChatResponse)
def chat_assistant(req: AIChatRequest):
    return disaster_orchestrator.route_query(req)

@router.post("/ai/analyze", response_model=AIChatResponse)
def ai_analyze(req: AIChatRequest):
    return disaster_orchestrator.route_query(req)

# Phase 10: System Health & Demo State Endpoints
@router.get("/health")
def get_system_health():
    """Returns the operational status and sub-service health of AEGIS."""
    return {
        "status": "operational",
        "version": "1.0.0",
        "mode": "DEMO / SIMULATION",
        "services": {
            "prediction": "healthy",
            "cascade": "healthy",
            "evidence": "healthy",
            "missions": "healthy",
            "simulation": "healthy",
            "adaptive": "healthy",
            "ai": "healthy"
        },
        "active_disaster": "Flood Event — Northern Corridor",
        "system_time": "2026-08-15T12:00:00Z"
    }

@router.post("/demo/reset")
def reset_demo_state():
    """Resets all dynamic state (missions, simulations, adaptive history, AI sessions, live feed) to baseline T+0."""
    mission_service.reset()
    simulation_service.reset()
    live_feed_simulator.reset()
    situation_store.reset_state()
    from app.services.adaptive.learning_store import learning_store
    learning_store._init_demo_dataset()
    from app.services.orchestrator.context_builder import context_builder
    context_builder.sessions.clear()
    
    return {
        "status": "RESET_SUCCESSFUL",
        "message": "AEGIS Demo Scenario successfully reset to baseline T+0 state.",
        "active_event": "Flood Event — Northern Corridor",
        "timeline_step": "T+0",
        "active_zones_count": len(ZONES_DATA),
        "available_teams_count": len(RESCUE_TEAMS_DATA)
    }

@router.get("/demo/state")
def get_demo_state():
    """Returns the deterministic demo scenario metadata and timeline steps."""
    return {
        "event_id": "EVT-2026-FL-001",
        "title": "Flood Event — Northern Corridor",
        "intensity": "ESCALATING",
        "current_time_step": "T+0",
        "timeline_steps": [
            {
                "time": "T+0",
                "label": "T+0 (Current Horizon)",
                "description": "Flood worsening in Northern Corridor. River cresting at 3.2m.",
                "zone7_risk": 86,
                "zone7_isolation_minutes": 42,
                "road_accessibility_pct": 48,
                "telecom_pct": 72,
                "silent_crisis_flag": False
            },
            {
                "time": "T+30",
                "label": "T+30 (30 Min Horizon)",
                "description": "Corridor 14 approach road submerged. Heavy current debris blocking drainage.",
                "zone7_risk": 89,
                "zone7_isolation_minutes": 22,
                "road_accessibility_pct": 39,
                "telecom_pct": 51,
                "silent_crisis_flag": False
            },
            {
                "time": "T+60",
                "label": "T+60 (60 Min Horizon)",
                "description": "Bridge approach completely submerged. Zone 7 reaches critical isolation status.",
                "zone7_risk": 93,
                "zone7_isolation_minutes": 0,
                "road_accessibility_pct": 29,
                "telecom_pct": 28,
                "silent_crisis_flag": True
            },
            {
                "time": "T+180",
                "label": "T+180 (3 Hour Horizon)",
                "description": "Critical cascading conditions across entire northern corridor with Substation #2 failure.",
                "zone7_risk": 97,
                "zone7_isolation_minutes": 0,
                "road_accessibility_pct": 12,
                "telecom_pct": 14,
                "silent_crisis_flag": True
            }
        ]
    }

# ==========================================
# Ingestion & Live Feed Simulator Endpoints
# ==========================================
@router.get("/ingestion/status", response_model=IngestionStatus)
def get_ingestion_status():
    st = situation_store.get_status()
    sim_st = live_feed_simulator.get_status()
    st.active_simulator_running = sim_st["is_running"]
    st.simulation_step = sim_st["current_step"]
    st.total_simulation_steps = sim_st["total_steps"]
    return st

@router.get("/ingestion/observations", response_model=List[DisasterObservation])
def get_observations(
    zone_id: Optional[str] = None,
    hazard_type: Optional[str] = None,
    source_type: Optional[str] = None,
    limit: int = 50
):
    return situation_store.get_observations(zone_id=zone_id, hazard_type=hazard_type, source_type=source_type, limit=limit)

@router.get("/ingestion/telemetry/{zone_id}")
def get_zone_telemetry(zone_id: str):
    return situation_store.get_zone_telemetry(zone_id)

@router.post("/ingestion/observe", response_model=DisasterObservation)
def post_observation(observation: DisasterObservation):
    return situation_store.ingest_observation(observation)

@router.post("/ingestion/demo/start")
def start_live_feed():
    return live_feed_simulator.start()

@router.post("/ingestion/demo/stop")
def stop_live_feed():
    return live_feed_simulator.stop()

@router.post("/ingestion/demo/step", response_model=LiveFeedStepEvent)
def step_live_feed():
    return live_feed_simulator.step()

@router.post("/ingestion/demo/reset")
def reset_live_feed():
    return live_feed_simulator.reset()

# ==========================================
# RAG Emergency Knowledge Layer Endpoints
# ==========================================
@router.post("/rag/query")
def query_rag_knowledge(
    payload: Dict[str, Any] = Body(...)
):
    query_text = payload.get("query", "flood emergency evacuation SOP")
    top_k = payload.get("top_k", 3)
    category = payload.get("category")
    return rag_service.query_knowledge_base(query=query_text, top_k=top_k, category=category)

@router.get("/rag/documents")
def get_rag_documents():
    return rag_service.get_documents_catalog()

@router.get("/rag/status")
def get_rag_status():
    return rag_service.get_status()

# ==========================================
# Computer Vision Intelligence Endpoints
# ==========================================
@router.post("/cv/analyze", response_model=CVAnalysisResult)
def analyze_cv_imagery(request: Optional[CVAnalysisRequest] = Body(None)):
    req = request or CVAnalysisRequest(target_zone_id="zone-7")
    return cv_service.analyze_image(req)

@router.get("/cv/scans")
def get_cv_scans():
    return cv_service.get_scans_catalog()

@router.get("/cv/scans/{scan_id}", response_model=CVAnalysisResult)
def get_cv_scan_by_id(scan_id: str):
    res = cv_service.get_scan_by_id(scan_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"CV Recon Scan '{scan_id}' not found")
    return res


