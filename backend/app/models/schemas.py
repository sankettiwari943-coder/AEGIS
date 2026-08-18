from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class ConnectivityStatus(str, Enum):
    NORMAL = "normal"
    DEGRADED = "degraded"
    LOST = "lost"

class RoadStatus(str, Enum):
    OPEN = "open"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"
    PREDICTED_BLOCKED = "predicted_blocked"

class InfraType(str, Enum):
    HOSPITAL = "hospital"
    SHELTER = "shelter"
    POWER_STATION = "power_station"
    PUMPING_STATION = "pumping_station"
    TELECOM_TOWER = "telecom_tower"

class InfraStatus(str, Enum):
    OPERATIONAL = "operational"
    WARNING = "warning"
    COMPROMISED = "compromised"
    OFFLINE = "offline"

class MissionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DISPATCHED = "dispatched"
    ACTIVE = "active"
    COMPLETED = "completed"

# GeoJSON Polygon Model
class GeoPolygon(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[List[float]]] # [lng, lat] rings

# Zone Data
class Zone(BaseModel):
    id: str
    code: str
    name: str
    district: str
    population: int
    elevation_meters: float
    current_flood_depth_cm: float
    rainfall_rate_mmh: float
    river_level_meters: float
    primary_risk_score: int
    secondary_risks: Dict[str, int] = Field(default_factory=dict)
    cascading_risk_score: int
    connectivity_status: ConnectivityStatus
    road_accessibility_percent: int
    hospital_accessibility_percent: int
    sos_reports_last_hour: int
    active_rescue_teams: int
    geometry: GeoPolygon
    center: List[float] # [lng, lat]
    is_silent_risk: bool = False
    silent_risk_score: int = 0
    escalation_time_minutes: Optional[int] = None
    predicted_risk_60m: int

# Road Segment
class RoadSegment(BaseModel):
    id: str
    name: str
    from_zone_id: str
    to_zone_id: str
    status: RoadStatus
    passability_percent: int
    elevation_meters: float
    coordinates: List[List[float]] # [[lng, lat], [lng, lat], ...]
    is_critical_hospital_route: bool = False

# Infrastructure
class Infrastructure(BaseModel):
    id: str
    name: str
    type: InfraType
    zone_id: str
    status: InfraStatus
    coordinates: List[float] # [lng, lat]
    capacity: int
    current_load: int
    has_backup_generator: bool
    flood_barrier_height_cm: float
    current_water_level_cm: float
    details: Dict[str, Any] = Field(default_factory=dict)

# Rescue Team
class RescueTeam(BaseModel):
    id: str
    callsign: str
    unit_type: str
    location_coordinates: List[float] # [lng, lat]
    location_name: Optional[str] = None
    assigned_zone_id: Optional[str] = None
    has_boat: bool
    has_medical: bool
    has_swift_water: bool
    has_amphibious: bool
    crew_size: int
    evacuation_capacity: int = 12
    response_speed_kmh: float = 35.0
    equipment: List[str] = Field(default_factory=list)
    status: str # "ready", "dispatched", "engaged", "staged"
    current_eta_minutes: Optional[int] = None
    current_mission: Optional[str] = None


# Disaster Event Summary
class DisasterEvent(BaseModel):
    id: str
    title: str
    disaster_type: str = "URBAN FLOOD"
    status: str = "ESCALATING"
    simulation_label: str = "SIMULATION / DEMONSTRATION DATA"
    river_basin: str
    peak_crest_time_hours: float
    average_rainfall_rate_mmh: float
    total_population_exposed: int
    active_missions_count: int
    silent_risk_zones_count: int
    system_confidence_percent: int
    last_updated_timestamp: str

# Predictive Intelligence
class ZonePrediction(BaseModel):
    zone_id: str
    zone_name: str
    current_risk: int
    predicted_risk_30m: int
    predicted_risk_60m: int
    predicted_risk_90m: int
    escalation_time_minutes: int
    population_at_risk_current: int
    population_at_risk_predicted: int
    hospital_access_current_pct: int
    hospital_access_predicted_pct: int
    predicted_road_blocks_count: int
    confidence_percent: int
    primary_driver: str
    risk_trajectory: List[int] # [0m, 15m, 30m, 45m, 60m, 90m]
    ai_rationale: str

class PredictionResponse(BaseModel):
    timestamp: str
    system_confidence: int
    critical_escalation_zone: str
    escalation_countdown_minutes: int
    zone_predictions: List[ZonePrediction]
    simulation_mode_label: str = "SIMULATION / DEMONSTRATION DATA"

# Cascading Risk Models
class CascadeNode(BaseModel):
    id: str
    label: str
    category: str # "hazard", "infrastructure", "medical", "communication", "population", "environmental", "silent_crisis"
    current_risk: int
    predicted_risk: int
    triggered_by: str
    impact_description: str
    confidence: int # 0-100
    evidence_signals: List[str] = Field(default_factory=list)
    is_active: bool = True
    is_feedback_source: bool = False
    depth: int = 0

class CascadeEdge(BaseModel):
    source: str
    target: str
    relationship: str # "causes", "degrades", "cuts_off", "disables", "amplifies", "delays"
    impact: int # 0-100
    confidence: int # 0-100
    reason: str
    is_active: bool = True
    is_feedback_loop: bool = False

class CascadeChainStep(BaseModel):
    node_id: str
    node_name: str
    category: str
    risk_score: int
    action_state: str # "INITIATING", "SURGING", "FAILURE", "DISABLED", "CUTOFF", "ISOLATED", "CRITICAL"

class CascadeChain(BaseModel):
    chain_id: str
    zone_id: str
    zone_name: str
    title: str
    steps: List[CascadeChainStep]
    priority_score: int # 0-100
    priority_level: str # "CRITICAL CASCADE", "HIGH CASCADE", "MODERATE CASCADE", "LOW CASCADE"
    overall_risk: int
    confidence_percent: int
    narrative: str
    has_feedback_loop: bool = False

class CascadeContributor(BaseModel):
    name: str
    points: int
    category: str

class CascadeAlert(BaseModel):
    alert_id: str
    zone_id: str
    zone_name: str
    title: str
    description: str
    current_value: str
    predicted_value: str
    secondary_risk_score: int
    severity: str # "CRITICAL", "HIGH", "MODERATE"
    chain_id: Optional[str] = None
    target_node: Optional[str] = None

class SecondaryRisksBreakdown(BaseModel):
    road_isolation: int
    power_failure: int
    pump_failure: int
    hospital_accessibility: int
    emergency_response_delay: int
    medical_supply_shortage: int
    communication_loss: int
    reporting_blackout: int
    population_isolation: int
    evacuation_difficulty: int
    shelter_overload: int
    water_contamination: int
    sanitation_failure: int
    category_scores: Dict[str, int] = Field(default_factory=dict)

class ZoneCascadeGraphResponse(BaseModel):
    zone_id: str
    zone_name: str
    primary_risk: int
    cascading_risk: int
    nodes: List[CascadeNode]
    edges: List[CascadeEdge]
    max_depth: int
    cycles_detected: List[List[str]] = Field(default_factory=list)
    top_chains: List[CascadeChain] = Field(default_factory=list)
    contributors: List[CascadeContributor] = Field(default_factory=list)
    alerts: List[CascadeAlert] = Field(default_factory=list)
    model_mode_label: str = "MODEL ESTIMATE ONLY"

class ZoneCascadeDetailResponse(BaseModel):
    zone_id: str
    zone_name: str
    primary_risk: int
    secondary_risks: Dict[str, int]
    secondary_categories: Dict[str, int] = Field(default_factory=dict)
    cascading_risk: int
    contributors: List[CascadeContributor]
    top_chains: List[CascadeChain]
    alerts: List[CascadeAlert]
    narrative: str
    model_mode_label: str = "MODEL ESTIMATE ONLY"

class ZoneCascadingRisk(BaseModel):
    zone_id: str
    zone_name: str
    primary_flood_risk: int
    power_failure_risk: int
    medical_access_risk: int
    water_contamination_risk: int
    communication_loss_risk: int
    road_isolation_risk: int
    combined_cascading_score: int
    critical_chain: List[str]
    narrative_explanation: str


# Silent Crisis
class SilentRiskAssessment(BaseModel):
    zone_id: str
    zone_name: str
    population: int
    flood_depth_cm: float
    connectivity_status: str
    sos_reports_count: int
    expected_reports_count: int
    communication_anomaly_percent: int
    silent_crisis_score_percent: int
    last_contact_time: str
    status: str
    recommended_action: str
    requires_physical_recon: bool

# Mission Allocation & Optimizer Models
class ClosestTeamComparison(BaseModel):
    is_closest_team: bool = True
    closest_team_id: Optional[str] = None
    closest_team_callsign: Optional[str] = None
    closest_team_distance_km: Optional[float] = None
    closest_team_eta_minutes: Optional[int] = None
    comparison_narrative: Optional[str] = None
    trade_offs: List[str] = Field(default_factory=list)

class MissionCandidate(BaseModel):
    team_id: str
    callsign: str
    team_capabilities: List[str]
    distance_km: float
    travel_time_minutes: int
    normal_eta_minutes: int = 0
    road_condition_impact: str = "NORMAL"
    victim_urgency_score: int
    capability_match_score: int
    medical_match_score: int
    future_risk_score: int = 0
    cascade_risk_score: int = 0
    route_safety_score: int = 90
    availability_score: int = 100
    total_mission_score: int
    score_breakdown: Dict[str, int] = Field(default_factory=dict)
    expected_impact: int = 90
    expected_impact_summary: Dict[str, Any] = Field(default_factory=dict)
    why_this_team: List[str] = Field(default_factory=list)
    route_waypoints: List[List[float]] = Field(default_factory=list)
    reasoning: str

class MissionRecommendation(BaseModel):
    mission_id: str
    mission_type: str = "RESCUE_EVACUATION" # "RESCUE_EVACUATION", "MEDICAL_EMERGENCY", "PHYSICAL_RECON"
    target_zone_id: str
    target_zone_name: str
    victim_count: int
    medical_emergencies: int
    flood_depth_cm: float = 0.0
    urgency_level: str
    urgency_label: str = "MODEL ESTIMATE"
    recommended_team: MissionCandidate
    alternate_teams: List[MissionCandidate] = Field(default_factory=list)
    closest_team_comparison: Optional[ClosestTeamComparison] = None
    evidence_confidence_percent: int = 90
    confidence_status: str = "HIGH_CONFIDENCE" # "HIGH_CONFIDENCE", "LOW_CONFIDENCE"
    evidence_signals: List[str] = Field(default_factory=list)
    human_approval_state: str = "PENDING_APPROVAL" # "PENDING_APPROVAL", "APPROVED", "DISMISSED"
    approved_at: Optional[str] = None
    simulation_mode_label: str = "SIMULATION / DEMONSTRATION DATA ONLY"

class MissionScoringWeights(BaseModel):
    victim_urgency: float = 0.30
    travel_time: float = 0.20
    team_capability: float = 0.20
    medical_capability: float = 0.15
    future_risk: float = 0.10
    resource_availability: float = 0.05

class MultiMissionOptimizationRequest(BaseModel):
    zones: Optional[List[str]] = None
    available_teams: Optional[List[str]] = None
    prioritize_medical: bool = True

class MultiMissionOptimizationPlan(BaseModel):
    plan_id: str
    total_expected_impact: int
    assigned_missions: List[MissionRecommendation] = Field(default_factory=list)
    unassigned_teams: List[str] = Field(default_factory=list)
    unassigned_zones: List[str] = Field(default_factory=list)
    conflicts_prevented: int = 0
    optimization_strategy: str = "Multi-Attribute Utility Optimization (Deterministic)"
    timestamp: str

class MissionModifyRequest(BaseModel):
    team_id: Optional[str] = None
    target_zone_id: Optional[str] = None
    victim_count: Optional[int] = None
    medical_emergencies: Optional[int] = None
    priority_override: Optional[str] = None

# Truth & Evidence Models
class EvidenceType(str, Enum):
    SENSOR = "SENSOR"
    CITIZEN_REPORT = "CITIZEN_REPORT"
    SATELLITE_OBSERVATION = "SATELLITE_OBSERVATION"
    INFRASTRUCTURE_STATUS = "INFRASTRUCTURE_STATUS"
    COMMUNICATION_SIGNAL = "COMMUNICATION_SIGNAL"
    OFFICIAL_REPORT = "OFFICIAL_REPORT"
    HISTORICAL_DATA = "HISTORICAL_DATA"
    MODEL_OUTPUT = "MODEL_OUTPUT"

class EvidenceStatus(str, Enum):
    VERIFIED = "VERIFIED"
    SUPPORTED = "SUPPORTED"
    UNVERIFIED = "UNVERIFIED"
    CONFLICTING = "CONFLICTING"
    STALE = "STALE"
    REJECTED = "REJECTED"

class EvidenceItem(BaseModel):
    id: str
    type: EvidenceType
    timestamp: str
    source: str
    location: str
    claim_id: Optional[str] = None
    claim: str
    value: Any
    reliability: float # 0.0 - 1.0
    status: EvidenceStatus
    is_contradicting: bool = False
    minutes_ago: int = 0

class EvidenceConflict(BaseModel):
    conflict_id: str
    claim_id: str
    description: str
    opposing_evidence_ids: List[str] = Field(default_factory=list)
    reconciliation_status: str = "UNRESOLVED" # "UNRESOLVED", "RESOLVED", "RECON_REQUIRED"
    recommended_action: str

class ClaimAssessment(BaseModel):
    claim_id: str
    target_zone_id: str
    target_entity: str
    title: str
    claim_statement: str
    ai_confidence_percent: int # 0-100
    status: EvidenceStatus
    supporting_sources_count: int
    conflicting_sources_count: int
    supporting_evidence: List[EvidenceItem] = Field(default_factory=list)
    conflicting_evidence: List[EvidenceItem] = Field(default_factory=list)
    evidence_timeline: List[Dict[str, Any]] = Field(default_factory=list)
    recency_score: int = 90
    consistency_score: int = 85
    data_trust_score: int = 85
    audit_trail: List[str] = Field(default_factory=list)
    decision_recommendation: str
    requires_physical_recon: bool = False

class DecisionEvidenceTrace(BaseModel):
    decision_id: str
    decision_type: str # "RECOMMENDATION", "PREDICTION", "CASCADE", "SILENT_CRISIS"
    title: str
    zone_id: str
    action_statement: str
    confidence_percent: int
    decision_chain: List[Dict[str, Any]] = Field(default_factory=list) # [{ level: "DECISION", title: "...", text: "..." }]
    key_signals: List[str] = Field(default_factory=list)
    underlying_claims: List[str] = Field(default_factory=list)
    underlying_evidence: List[EvidenceItem] = Field(default_factory=list)
    trust_score: int = 85

class EvidenceSummaryResponse(BaseModel):
    total_claims_analyzed: int
    verified_count: int
    supported_count: int
    unverified_count: int
    conflicting_count: int
    stale_count: int
    data_trust_index: int # 0-100
    trust_breakdown: Dict[str, int] = Field(default_factory=dict)
    claims: List[ClaimAssessment] = Field(default_factory=list)

# Backward Compatibility
class EvidenceClaim(BaseModel):
    claim_id: str
    target_zone_id: str
    title: str
    description: str
    citizen_reports_count: int
    satellite_synthetic_score: int # 0-100
    telemetry_sensor_confirmed: bool
    contradicting_reports_count: int
    ai_confidence_percent: int
    status: str # "VERIFIED", "UNVERIFIED_DAMAGE", "CONTRADICTED"
    evidence_chain: List[str]


# Phase 7: What-If Simulation Models
class InterventionItem(BaseModel):
    id: str
    name: str
    description: str
    category: str # "EVACUATION", "RESCUE", "MEDICAL", "INFRASTRUCTURE", "TRAFFIC", "SHELTER"
    target_zone_id: Optional[str] = None
    resource_type: str # "rescue_team", "medical_unit", "boat_team", "generator", "utility_crew", "shelter"
    resource_cost: int = 1
    benefit_summary: str = ""
    estimated_effects: Dict[str, Any] = Field(default_factory=dict)
    duration_minutes: int = 60
    confidence_percent: int = 85

class ResourceInventory(BaseModel):
    available_rescue_teams: int = 3
    available_medical_units: int = 1
    available_generators: int = 2
    available_boats: int = 2
    available_utility_crews: int = 2
    available_shelters: int = 2
    active_conflicts: List[str] = Field(default_factory=list)

class CascadeLinkShift(BaseModel):
    source: str
    target: str
    baseline_severity: str
    scenario_severity: str
    mitigated: bool
    explanation: str

class ZoneRiskShift(BaseModel):
    zone_id: str
    zone_code: str
    zone_name: str
    baseline_risk: int
    baseline_severity: str
    scenario_risk: int
    scenario_severity: str
    risk_delta: int
    primary_driver: str

class SimulationRequest(BaseModel):
    scenario_id: Optional[str] = None
    scenario_title: str = "Compound What-If Scenario"
    time_horizon: int = 60 # 30, 60, 180 (minutes)
    time_horizon_minutes: Optional[int] = None
    base_scenario: str = "do_nothing"
    perturbations: List[str] = Field(default_factory=list)
    interventions: List[str] = Field(default_factory=list)

class SimulationMetricDelta(BaseModel):
    metric_name: str
    baseline_value: str
    scenario_value: str
    delta_display: str
    is_worsening: bool
    unit: Optional[str] = None

class SimulationComparison(BaseModel):
    scenario_id: str = "sim-01"
    scenario_title: str
    time_horizon_minutes: int = 60
    perturbations_active: List[str] = Field(default_factory=list)
    interventions_active: List[str] = Field(default_factory=list)
    baseline_overall_risk: int
    scenario_overall_risk: int
    net_risk_reduction_points: int
    net_risk_reduction_percent: int
    resource_cost: int = 0
    efficiency_score: float = 0.0
    metrics: List[SimulationMetricDelta] = Field(default_factory=list)
    zone_risk_shifts: List[ZoneRiskShift] = Field(default_factory=list)
    cascade_shifts: List[CascadeLinkShift] = Field(default_factory=list)
    timeline_trajectories: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    critical_impacted_zones: List[str] = Field(default_factory=list)
    best_preventive_action: str
    why_bullets: List[str] = Field(default_factory=list)
    ai_strategic_briefing: str
    confidence_percent: int = 85
    confidence_status: str = "HIGH_CONFIDENCE"
    has_resource_conflict: bool = False
    conflict_message: Optional[str] = None
    recommended_mission_payload: Optional[Dict[str, Any]] = None
    simulation_label: str = "SIMULATION / MODEL ESTIMATE ONLY"

class MultiScenarioRankingItem(BaseModel):
    scenario_id: str
    title: str
    interventions: List[str]
    overall_risk: int
    risk_reduction_points: int
    risk_reduction_percent: int
    resource_cost: int
    efficiency_score: float
    mission_impact: int
    cascade_risk: int
    confidence_percent: int
    rank: int

class MultiScenarioComparisonResponse(BaseModel):
    time_horizon_minutes: int
    scenarios: List[MultiScenarioRankingItem] = Field(default_factory=list)
    best_scenario: Optional[MultiScenarioRankingItem] = None
    recommendation_narrative: str
    timestamp: str

# Adaptive Feedback
# Phase 9: Adaptive Learning & Recalibration Models
class OutcomeItem(BaseModel):
    id: str # e.g. "OUT-001"
    prediction_id: Optional[str] = None
    zone_id: Optional[str] = None
    zone_name: Optional[str] = None
    metric: str # "road_accessibility", "hospital_accessibility", "flood_risk", "predicted_isolation_time", "mission_eta", etc.
    predicted_value: float
    actual_value: float
    prediction_time: str = ""
    observation_time: str = ""
    error: float # predicted - actual or actual - predicted
    absolute_error: float
    relative_error_pct: Optional[float] = None
    status: str # "ACCURATE", "UNDERPREDICTED", "OVERPREDICTED"
    source: str = "Operator Observation" # "Operator Observation", "Sensor", "Official Update", "Simulation Feedback"
    confidence: float = 0.85
    notes: Optional[str] = None

class FeedbackSubmission(BaseModel):
    mission_id: Optional[str] = None
    target_zone_id: Optional[str] = "zone-7"
    metric: str = "road_accessibility"
    predicted_value: Optional[float] = None
    actual_value: Optional[float] = None
    source: str = "Operator Observation"
    notes: Optional[str] = None
    # Legacy fields for backward compatibility
    predicted_eta_minutes: Optional[int] = None
    actual_eta_minutes: Optional[int] = None
    predicted_road_access_pct: Optional[int] = None
    actual_road_access_pct: Optional[int] = None
    observations: Optional[str] = None

class FeedbackAnalysisResponse(BaseModel):
    feedback_id: str
    outcome: Optional[OutcomeItem] = None
    eta_error_minutes: Optional[int] = None
    road_access_error_pct: Optional[int] = None
    recalibration_summary: str
    previous_model_confidence_pct: int
    updated_model_confidence_pct: int
    status: str = "RECALIBRATION_RECORDED"

class CalibrationItem(BaseModel):
    metric: str
    label: str
    sample_count: int
    average_error: float
    bias: str # "UNDERPREDICTING", "OVERPREDICTING", "BALANCED / STABLE"
    suggested_adjustment: float
    applied_adjustment: float
    status: str # "STABLE", "RECALIBRATION_RECOMMENDED", "CALIBRATED", "INSUFFICIENT_DATA", "LIMIT_REACHED"
    confidence: float
    confidence_adjustment: float
    last_updated: str

class LearningInsightItem(BaseModel):
    id: str
    metric: str
    title: str
    description: str
    average_bias: float
    status: str
    recommendation: str
    timestamp: str

class LearningEventItem(BaseModel):
    id: str
    metric: str
    event_type: str # "CALIBRATION_UPDATE", "FEEDBACK_OBSERVED", "TOLERANCE_ADJUSTED", "BIAS_DETECTED"
    old_value: float
    new_value: float
    reason: str
    evidence_count: int
    timestamp: str

class AdaptiveMetricPerformance(BaseModel):
    metric: str
    label: str
    evaluated_count: int
    accurate_count: int
    underpredicted_count: int
    overpredicted_count: int
    accuracy_percent: float
    average_absolute_error: float
    bias: float
    status: str

class AdaptiveStatusResponse(BaseModel):
    status: str # "STABLE", "LEARNING", "CALIBRATION_REQUIRED", "INSUFFICIENT_DATA"
    active_calibrations_count: int
    total_evaluated_predictions: int
    overall_accuracy_percent: float
    most_unreliable_metric: str
    most_reliable_metric: str
    last_updated: str

class AdaptivePerformanceResponse(BaseModel):
    overall_accuracy: float
    evaluated_predictions: int
    metrics: List[AdaptiveMetricPerformance] = Field(default_factory=list)
    trend: str = "Improving"

class CalibrationDemoResponse(BaseModel):
    metric: str
    before_average_error: float
    after_average_error: float
    error_reduction_points: float
    error_reduction_percent: float
    message: str
    sample_count: int


# Phase 8: AI Disaster Orchestrator Models
class ToolCallRecord(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    output_summary: str = ""

class DeepLinkAction(BaseModel):
    label: str
    target_mode: str # "LIVE", "PREDICT", "CASCADE", "EVIDENCE", "MISSIONS", "SIMULATE"
    target_zone_id: Optional[str] = None
    action_type: str # "VIEW_EVIDENCE", "VIEW_PREDICTION", "VIEW_CASCADE", "VIEW_MISSION", "SIMULATE"

class OrchestratorQueryRequest(BaseModel):
    query: str
    message: Optional[str] = None # Alias for query
    session_id: Optional[str] = "demo-session"
    context_zone_id: Optional[str] = None
    context_mode: Optional[str] = "LIVE"

class OrchestratorStructuredResponse(BaseModel):
    answer: str
    direct_answer: str = ""
    why_rationale: List[str] = Field(default_factory=list)
    facts: List[str] = Field(default_factory=list)
    live_facts: List[str] = Field(default_factory=list)
    retrieved_guidance: List[str] = Field(default_factory=list)
    rag_sources: List[str] = Field(default_factory=list)
    model_estimates: List[str] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    tool_calls: List[ToolCallRecord] = Field(default_factory=list)
    deep_links: List[DeepLinkAction] = Field(default_factory=list)
    referenced_zones: List[str] = Field(default_factory=list)
    supporting_evidence: List[str] = Field(default_factory=list)
    confidence_score: int = 88
    orchestrator_agent: str = "AEGIS Disaster Orchestrator"
    requires_human_approval: bool = True
    safety_label: str = "DECISION SUPPORT / MODEL ESTIMATE"

class CommandBriefingResponse(BaseModel):
    title: str = "AEGIS COMMAND SITUATION BRIEFING"
    situation_summary: str
    top_priority_zone: str
    current_risk_score: int
    predicted_escalation: str
    top_cascades: List[str] = Field(default_factory=list)
    recommended_mission: str
    mission_score: int
    silent_risk_alerts: List[str] = Field(default_factory=list)
    key_uncertainties: List[str] = Field(default_factory=list)
    simulation_summary: str
    confidence_percent: int
    timestamp: str

# AI Assistant Chat
class AIChatRequest(BaseModel):
    query: str
    message: Optional[str] = None
    session_id: Optional[str] = "demo-session"
    context_zone_id: Optional[str] = None
    context_mode: Optional[str] = "LIVE"

class AIChatResponse(BaseModel):
    answer: str
    direct_answer: Optional[str] = None
    why_rationale: Optional[List[str]] = None
    live_facts: Optional[List[str]] = None
    retrieved_guidance: Optional[List[str]] = None
    rag_sources: Optional[List[str]] = None
    referenced_zones: List[str] = Field(default_factory=list)
    supporting_evidence: List[str] = Field(default_factory=list)
    uncertainties: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    tools_used: Optional[List[str]] = None
    deep_links: Optional[List[DeepLinkAction]] = None
    confidence_score: int = 88
    orchestrator_agent: str = "AEGIS Disaster Orchestrator"
    requires_human_approval: bool = True
    safety_label: str = "DECISION SUPPORT / MODEL ESTIMATE"

