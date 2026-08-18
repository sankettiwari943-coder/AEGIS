export type ConnectivityStatus = "normal" | "degraded" | "lost";
export type RoadStatus = "open" | "restricted" | "blocked" | "predicted_blocked";
export type InfraType = "hospital" | "shelter" | "power_station" | "pumping_station" | "telecom_tower";
export type InfraStatus = "operational" | "warning" | "compromised" | "offline";

export interface GeoPolygon {
  type: string;
  coordinates: number[][][];
}

export interface Zone {
  id: string;
  code: string;
  name: string;
  district: string;
  population: number;
  elevation_meters: number;
  current_flood_depth_cm: number;
  rainfall_rate_mmh: number;
  river_level_meters: number;
  primary_risk_score: number;
  secondary_risks: Record<string, number>;
  cascading_risk_score: number;
  connectivity_status: ConnectivityStatus;
  road_accessibility_percent: number;
  hospital_accessibility_percent: number;
  sos_reports_last_hour: number;
  active_rescue_teams: number;
  geometry: GeoPolygon;
  center: [number, number];
  is_silent_risk: boolean;
  silent_risk_score: number;
  escalation_time_minutes?: number;
  predicted_risk_60m: number;
}

export interface RoadSegment {
  id: string;
  name: string;
  from_zone_id: string;
  to_zone_id: string;
  status: RoadStatus;
  passability_percent: number;
  elevation_meters: number;
  coordinates: [number, number][];
  is_critical_hospital_route: boolean;
}

export interface Infrastructure {
  id: string;
  name: string;
  type: InfraType;
  zone_id: string;
  status: InfraStatus;
  coordinates: [number, number];
  capacity: number;
  current_load: number;
  has_backup_generator: boolean;
  flood_barrier_height_cm: number;
  current_water_level_cm: number;
  details: Record<string, any>;
}

export interface RescueTeam {
  id: string;
  callsign: string;
  unit_type: string;
  location_coordinates: [number, number];
  location_name?: string;
  assigned_zone_id?: string;
  has_boat: boolean;
  has_medical: boolean;
  has_swift_water: boolean;
  has_amphibious: boolean;
  crew_size: number;
  evacuation_capacity?: number;
  response_speed_kmh?: number;
  equipment?: string[];
  status: "ready" | "dispatched" | "engaged" | "maintenance" | string;
  current_eta_minutes?: number;
  current_mission?: string;
}

export interface DisasterEvent {
  id: string;
  title: string;
  disaster_type: string;
  status: string;
  simulation_label: string;
  river_basin: string;
  peak_crest_time_hours: number;
  average_rainfall_rate_mmh: number;
  total_population_exposed: number;
  active_missions_count: number;
  silent_risk_zones_count: number;
  system_confidence_percent: number;
  last_updated_timestamp: string;
}

export interface TopPredictionItem {
  id: string;
  title: string;
  target_entity: string;
  category: "ZONE" | "HOSPITAL" | "ROAD" | "POWER";
  predicted_event: string;
  eta_minutes: number;
  confidence_percent: number;
  priority_score: number;
  severity_level: "CRITICAL" | "HIGH" | "MODERATE" | "LOW";
  action_label: string;
}

export interface ZonePrediction {
  zone_id: string;
  zone_code: string;
  zone_name: string;
  district?: string;
  current_risk: number;
  predicted_risk_30m: number;
  predicted_risk_60m: number;
  predicted_risk_3h: number;
  escalation_time_minutes: number;
  confidence_percent: number;
  population_at_risk: {
    now: number;
    "30m": number;
    "60m": number;
    "3h": number;
  };
  road_accessibility: {
    now: number;
    "30m": number;
    "60m": number;
    "3h": number;
  };
  hospital_accessibility: {
    now: number;
    "30m": number;
    "60m": number;
    "3h": number;
  };
  communication_status: {
    now: number;
    "60m": number;
  };
  drivers: string[];
  primary_driver: string;
  risk_trajectory: number[];
}

export interface PredictionResponse {
  timestamp: string;
  system_confidence: number;
  critical_escalation_zone: string;
  escalation_countdown_minutes: number;
  top_predictions: TopPredictionItem[];
  zone_predictions: ZonePrediction[];
  population_projection_summary: {
    now: number;
    "30m": number;
    "60m": number;
    "3h": number;
  };
  simulation_mode_label: string;
}

export interface CascadeNode {
  id: string;
  label: string;
  category: "hazard" | "infrastructure" | "medical" | "communication" | "population" | "environmental" | "silent_crisis" | string;
  current_risk: number;
  predicted_risk: number;
  triggered_by: string;
  impact_description: string;
  confidence: number;
  evidence_signals: string[];
  is_active: boolean;
  is_feedback_source?: boolean;
  depth: number;
}

export interface CascadeEdge {
  source: string;
  target: string;
  relationship: string;
  impact: number;
  confidence: number;
  reason: string;
  is_active: boolean;
  is_feedback_loop?: boolean;
}

export interface CascadeChainStep {
  node_id: string;
  node_name: string;
  category: string;
  risk_score: number;
  action_state: string;
}

export interface CascadeChain {
  chain_id: string;
  zone_id: string;
  zone_name: string;
  title: string;
  steps: CascadeChainStep[];
  priority_score: number;
  priority_level: string;
  overall_risk: number;
  confidence_percent: number;
  narrative: string;
  has_feedback_loop?: boolean;
}

export interface CascadeContributor {
  name: string;
  points: number;
  category: string;
}

export interface CascadeAlert {
  alert_id: string;
  zone_id: string;
  zone_name: string;
  title: string;
  description: string;
  current_value: string;
  predicted_value: string;
  secondary_risk_score: number;
  severity: "CRITICAL" | "HIGH" | "MODERATE" | string;
  chain_id?: string;
  target_node?: string;
}

export interface SecondaryRisksBreakdown {
  road_isolation: number;
  power_failure: number;
  pump_failure: number;
  hospital_accessibility: number;
  emergency_response_delay: number;
  medical_supply_shortage: number;
  communication_loss: number;
  reporting_blackout: number;
  population_isolation: number;
  evacuation_difficulty: number;
  shelter_overload: number;
  water_contamination: number;
  sanitation_failure: number;
  category_scores?: Record<string, number>;
}

export interface ZoneCascadeGraphResponse {
  zone_id: string;
  zone_name: string;
  primary_risk: number;
  cascading_risk: number;
  nodes: CascadeNode[];
  edges: CascadeEdge[];
  max_depth: number;
  cycles_detected: string[][];
  top_chains: CascadeChain[];
  contributors: CascadeContributor[];
  alerts: CascadeAlert[];
  model_mode_label?: string;
}

export interface ZoneCascadeDetailResponse {
  zone_id: string;
  zone_name: string;
  primary_risk: number;
  secondary_risks: Record<string, number>;
  secondary_categories?: Record<string, number>;
  cascading_risk: number;
  contributors: CascadeContributor[];
  top_chains: CascadeChain[];
  alerts: CascadeAlert[];
  narrative: string;
  model_mode_label?: string;
}

export interface ZoneCascadingRisk {
  zone_id: string;
  zone_name: string;
  primary_flood_risk: number;
  power_failure_risk: number;
  medical_access_risk: number;
  water_contamination_risk: number;
  communication_loss_risk: number;
  road_isolation_risk: number;
  combined_cascading_score: number;
  critical_chain: string[];
  narrative_explanation: string;
}

export interface SilentRiskAssessment {
  zone_id: string;
  zone_name: string;
  population: number;
  flood_depth_cm: number;
  connectivity_status: string;
  sos_reports_count: number;
  expected_reports_count: number;
  communication_anomaly_percent: number;
  silent_crisis_score_percent: number;
  last_contact_time: string;
  status: string;
  recommended_action: string;
  requires_physical_recon: boolean;
}

export interface ClosestTeamComparison {
  is_closest_team: boolean;
  closest_team_id?: string;
  closest_team_callsign?: string;
  closest_team_distance_km?: number;
  closest_team_eta_minutes?: number;
  comparison_narrative?: string;
  trade_offs?: string[];
}

export interface MissionCandidate {
  team_id: string;
  callsign: string;
  team_capabilities: string[];
  distance_km: number;
  travel_time_minutes: number;
  normal_eta_minutes?: number;
  road_condition_impact?: string;
  victim_urgency_score: number;
  capability_match_score: number;
  medical_match_score: number;
  future_risk_score?: number;
  cascade_risk_score?: number;
  route_safety_score: number;
  availability_score?: number;
  total_mission_score: number;
  score_breakdown: Record<string, number>;
  expected_impact?: number;
  expected_impact_summary?: {
    victims_reached?: string;
    medical_emergencies_stabilized?: string;
    isolation_risk_reduction?: string;
    expected_impact_score?: number;
  };
  why_this_team?: string[];
  route_waypoints?: [number, number][];
  reasoning: string;
}

export interface MissionRecommendation {
  mission_id: string;
  mission_type?: "RESCUE_EVACUATION" | "MEDICAL_EMERGENCY" | "PHYSICAL_RECON" | string;
  target_zone_id: string;
  target_zone_name: string;
  victim_count: number;
  medical_emergencies: number;
  flood_depth_cm?: number;
  urgency_level: string;
  urgency_label?: string;
  recommended_team: MissionCandidate;
  alternate_teams: MissionCandidate[];
  closest_team_comparison?: ClosestTeamComparison;
  evidence_confidence_percent?: number;
  confidence_status?: "HIGH_CONFIDENCE" | "LOW_CONFIDENCE" | string;
  evidence_signals?: string[];
  human_approval_state: "PENDING_APPROVAL" | "APPROVED" | "DISMISSED" | string;
  approved_at?: string;
  simulation_mode_label?: string;
}

export interface MultiMissionOptimizationPlan {
  plan_id: string;
  total_expected_impact: number;
  assigned_missions: MissionRecommendation[];
  unassigned_teams: string[];
  unassigned_zones: string[];
  conflicts_prevented: number;
  optimization_strategy: string;
  timestamp: string;
}

export interface MissionModifyRequest {
  team_id?: string;
  target_zone_id?: string;
  victim_count?: number;
  medical_emergencies?: number;
  priority_override?: string;
}

export type EvidenceType = 
  | 'SENSOR'
  | 'CITIZEN_REPORT'
  | 'SATELLITE_OBSERVATION'
  | 'INFRASTRUCTURE_STATUS'
  | 'COMMUNICATION_SIGNAL'
  | 'OFFICIAL_REPORT'
  | 'HISTORICAL_DATA'
  | 'MODEL_OUTPUT';

export type EvidenceStatus = 
  | 'VERIFIED'
  | 'SUPPORTED'
  | 'UNVERIFIED'
  | 'CONFLICTING'
  | 'STALE'
  | 'REJECTED';

export interface EvidenceItem {
  id: string;
  type: EvidenceType;
  timestamp: string;
  source: string;
  location: string;
  claim_id?: string;
  claim: string;
  value: any;
  reliability: number; // 0.0 - 1.0
  status: EvidenceStatus;
  is_contradicting: boolean;
  minutes_ago: number;
}

export interface EvidenceConflict {
  conflict_id: string;
  claim_id: string;
  description: string;
  opposing_evidence_ids: string[];
  reconciliation_status: string;
  recommended_action: string;
}

export interface EvidenceTimelineStep {
  time_display: string;
  source: string;
  type: string;
  event: string;
  value: string;
  is_contradicting: boolean;
}

export interface ClaimAssessment {
  claim_id: string;
  target_zone_id: string;
  target_entity: string;
  title: string;
  claim_statement: string;
  ai_confidence_percent: number; // 0-100
  status: EvidenceStatus;
  supporting_sources_count: number;
  conflicting_sources_count: number;
  supporting_evidence: EvidenceItem[];
  conflicting_evidence: EvidenceItem[];
  evidence_timeline: EvidenceTimelineStep[];
  recency_score: number;
  consistency_score: number;
  data_trust_score: number;
  audit_trail: string[];
  decision_recommendation: string;
  requires_physical_recon: boolean;
}

export interface DecisionChainStep {
  level: 'DECISION' | 'RISK' | 'PREDICTION' | 'EVIDENCE' | string;
  title: string;
  text: string;
  badge: string;
  color: string;
}

export interface DecisionEvidenceTrace {
  decision_id: string;
  decision_type: 'RECOMMENDATION' | 'PREDICTION' | 'CASCADE' | 'SILENT_CRISIS' | string;
  title: string;
  zone_id: string;
  action_statement: string;
  confidence_percent: number;
  decision_chain: DecisionChainStep[];
  key_signals: string[];
  underlying_claims: string[];
  underlying_evidence: EvidenceItem[];
  trust_score: number;
}

export interface EvidenceTrustBreakdown {
  source_reliability: number;
  recency: number;
  consistency: number;
  coverage: number;
  conflict_level: number;
}

export interface EvidenceSummaryResponse {
  total_claims_analyzed: number;
  verified_count: number;
  supported_count: number;
  unverified_count: number;
  conflicting_count: number;
  stale_count: number;
  data_trust_index: number;
  trust_breakdown: EvidenceTrustBreakdown;
  claims: ClaimAssessment[];
}

// Backward Compatibility
export interface EvidenceClaim {
  claim_id: string;
  target_zone_id: string;
  title: string;
  description: string;
  citizen_reports_count: number;
  satellite_synthetic_score: number;
  telemetry_sensor_confirmed: boolean;
  contradicting_reports_count: number;
  ai_confidence_percent: number;
  status: string;
  evidence_chain: string[];
}


export interface InterventionItem {
  id: string;
  name: string;
  description: string;
  category: "EVACUATION" | "RESCUE" | "MEDICAL" | "INFRASTRUCTURE" | "TRAFFIC" | "SHELTER" | string;
  target_zone_id?: string;
  resource_type: string;
  resource_cost: number;
  benefit_summary: string;
  estimated_effects?: Record<string, any>;
  duration_minutes: number;
  confidence_percent: number;
}

export interface ResourceInventory {
  available_rescue_teams: number;
  available_medical_units: number;
  available_generators: number;
  available_boats: number;
  available_utility_crews: number;
  available_shelters: number;
  active_conflicts: string[];
}

export interface CascadeLinkShift {
  source: string;
  target: string;
  baseline_severity: string;
  scenario_severity: string;
  mitigated: boolean;
  explanation: string;
}

export interface ZoneRiskShift {
  zone_id: string;
  zone_code: string;
  zone_name: string;
  baseline_risk: number;
  baseline_severity: string;
  scenario_risk: number;
  scenario_severity: string;
  risk_delta: number;
  primary_driver: string;
}

export interface SimulationRequest {
  scenario_id?: string;
  scenario_title: string;
  time_horizon?: number;
  time_horizon_minutes?: number;
  base_scenario?: string;
  perturbations: string[];
  interventions: string[];
}

export interface SimulationMetricDelta {
  metric_name: string;
  baseline_value: string;
  scenario_value: string;
  delta_display: string;
  is_worsening: boolean;
  unit?: string;
}

export interface SimulationComparison {
  scenario_id?: string;
  scenario_title: string;
  time_horizon_minutes?: number;
  perturbations_active: string[];
  interventions_active: string[];
  baseline_overall_risk: number;
  scenario_overall_risk: number;
  net_risk_reduction_points: number;
  net_risk_reduction_percent: number;
  resource_cost?: number;
  efficiency_score?: number;
  metrics: SimulationMetricDelta[];
  zone_risk_shifts?: ZoneRiskShift[];
  cascade_shifts?: CascadeLinkShift[];
  timeline_trajectories?: Record<string, Array<{ time: string; risk: number; pop: number; hosp_access: number }>>;
  critical_impacted_zones: string[];
  best_preventive_action: string;
  why_bullets?: string[];
  ai_strategic_briefing: string;
  confidence_percent?: number;
  confidence_status?: "HIGH_CONFIDENCE" | "LOW_CONFIDENCE" | string;
  has_resource_conflict?: boolean;
  conflict_message?: string;
  recommended_mission_payload?: {
    mission_id: string;
    target_zone_id: string;
    target_zone_name: string;
    team_id: string;
    team_callsign: string;
    eta_minutes: number;
    mission_impact: number;
  };
  simulation_label: string;
}

export interface MultiScenarioRankingItem {
  scenario_id: string;
  title: string;
  interventions: string[];
  overall_risk: number;
  risk_reduction_points: number;
  risk_reduction_percent: number;
  resource_cost: number;
  efficiency_score: number;
  mission_impact: number;
  cascade_risk: number;
  confidence_percent: number;
  rank: number;
}

export interface MultiScenarioComparisonResponse {
  time_horizon_minutes: number;
  scenarios: MultiScenarioRankingItem[];
  best_scenario?: MultiScenarioRankingItem;
  recommendation_narrative: string;
  timestamp: string;
}

export interface FeedbackSubmission {
  mission_id?: string;
  target_zone_id?: string;
  metric?: string;
  predicted_value?: number;
  actual_value?: number;
  source?: string;
  notes?: string;
  predicted_eta_minutes?: number;
  actual_eta_minutes?: number;
  predicted_road_access_pct?: number;
  actual_road_access_pct?: number;
  observations?: string;
}


export interface FeedbackAnalysisResponse {
  feedback_id: string;
  eta_error_minutes: number;
  road_access_error_pct: number;
  recalibration_summary: string;
  previous_model_confidence_pct: number;
  updated_model_confidence_pct: number;
  status: string;
}

export interface ToolCallRecord {
  tool_name: string;
  parameters: Record<string, any>;
  output_summary: string;
}

export interface DeepLinkAction {
  label: string;
  target_mode: MainNavMode | string;
  target_zone_id?: string;
  action_type: "VIEW_EVIDENCE" | "VIEW_PREDICTION" | "VIEW_CASCADE" | "VIEW_MISSION" | "SIMULATE" | string;
}

export interface OrchestratorQueryRequest {
  query: string;
  message?: string;
  session_id?: string;
  context_zone_id?: string;
  context_mode?: string;
}

export interface OrchestratorStructuredResponse {
  answer: string;
  direct_answer: string;
  why_rationale: string[];
  facts: string[];
  live_facts?: string[];
  retrieved_guidance?: string[];
  rag_sources?: string[];
  model_estimates: string[];
  uncertainties: string[];
  recommendations: string[];
  tools_used: string[];
  tool_calls: ToolCallRecord[];
  deep_links: DeepLinkAction[];
  referenced_zones: string[];
  supporting_evidence: string[];
  confidence_score: number;
  orchestrator_agent: string;
  requires_human_approval: boolean;
  safety_label: string;
}

export interface CommandBriefingResponse {
  title: string;
  situation_summary: string;
  top_priority_zone: string;
  current_risk_score: number;
  predicted_escalation: string;
  top_cascades: string[];
  recommended_mission: string;
  mission_score: number;
  silent_risk_alerts: string[];
  key_uncertainties: string[];
  simulation_summary: string;
  confidence_percent: number;
  timestamp: string;
}

export interface AIChatResponse {
  answer: string;
  direct_answer?: string;
  why_rationale?: string[];
  facts?: string[];
  live_facts?: string[];
  retrieved_guidance?: string[];
  rag_sources?: string[];
  model_estimates?: string[];
  uncertainties?: string[];
  recommendations?: string[];
  tools_used?: string[];
  tool_calls?: ToolCallRecord[];
  deep_links?: DeepLinkAction[];
  referenced_zones: string[];
  supporting_evidence: string[];
  confidence_score: number;
  orchestrator_agent: string;
  requires_human_approval?: boolean;
  safety_label?: string;
}

// Ingestion & Telemetry Types
export type DataSourceClassification = "LIVE" | "SIMULATED" | "SENSOR" | "OFFICIAL" | "CIVILIAN" | "AI-INFERRED" | "RAG" | "DEMO CV";

export interface DisasterObservation {
  id: string;
  source: string;
  source_type: DataSourceClassification;
  timestamp: string;
  latitude: number;
  longitude: number;
  zone_id?: string;
  hazard_type: string;
  value: number;
  unit: string;
  severity: number;
  confidence: number;
  metadata: Record<string, any>;
}

export interface IngestionStatus {
  pipeline_status: string;
  mode: string;
  active_connectors_count: number;
  total_observations_ingested: number;
  last_ingestion_timestamp: string;
  connectors: Record<string, any>;
  active_simulator_running: boolean;
  simulation_step: number;
  total_simulation_steps: number;
}

export interface LiveFeedStepEvent {
  step: number;
  title: string;
  description: string;
  target_zone: string;
  hazard_type: string;
  delta_description: string;
  observations: DisasterObservation[];
  impacted_engines: string[];
}

// RAG Knowledge Types
export interface RAGCitation {
  doc_id: string;
  title: string;
  source: string;
  category: string;
  relevance_score: number;
  snippet: string;
}

export interface RAGQueryResult {
  query: string;
  retrieved_count: number;
  guidance_summary: string[];
  citations: RAGCitation[];
  top_match?: any;
  timestamp: string;
  source_type: string;
}

export interface RAGDocumentSummary {
  id: string;
  title: string;
  category: string;
  source: string;
  last_revised: string;
  summary: string;
}

export interface RAGStatusResponse {
  status: string;
  mode: string;
  total_documents: number;
  total_chunks_indexed: number;
  vector_dimensions: number;
  categories: string[];
  embedding_provider: string;
  last_reindexed: string;
}

// Computer Vision Types
export interface DetectedObject {
  id: string;
  label: string;
  confidence: number;
  bbox: [number, number, number, number]; // [ymin, xmin, ymax, xmax]
  geo_coordinates?: [number, number];
  severity: string;
}

export interface GeoDamagePolygon {
  id: string;
  label: string;
  confidence: number;
  coordinates: [number, number][];
}

export interface CVAnalysisResult {
  scan_id: string;
  title: string;
  target_zone_id: string;
  target_zone_name: string;
  sensor_modality: string;
  analysis_label: string;
  timestamp: string;
  flood_extent_percent: number;
  damaged_structures_count: number;
  blocked_roads_count: number;
  trapped_clusters_count: number;
  detections: DetectedObject[];
  damage_polygons: GeoDamagePolygon[];
  overall_confidence: number;
  source_image_name: string;
  operational_takeaway: string;
  metadata: Record<string, any>;
}

export interface CVScanSummary {
  scan_id: string;
  title: string;
  target_zone_id: string;
  target_zone_name: string;
  sensor_modality: string;
  flood_extent_percent: number;
  overall_confidence: number;
}

export interface OutcomeItem {

  id: string;
  prediction_id?: string;
  zone_id?: string;
  zone_name?: string;
  metric: string;
  predicted_value: number;
  actual_value: number;
  prediction_time?: string;
  observation_time?: string;
  error: number;
  absolute_error: number;
  relative_error_pct?: number;
  status: "ACCURATE" | "UNDERPREDICTED" | "OVERPREDICTED" | string;
  source: string;
  confidence: number;
  notes?: string;
}

export interface CalibrationItem {
  metric: string;
  label: string;
  sample_count: number;
  average_error: number;
  bias: string;
  suggested_adjustment: number;
  applied_adjustment: number;
  status: "STABLE" | "RECALIBRATION_RECOMMENDED" | "CALIBRATED" | "INSUFFICIENT_DATA" | "LIMIT_REACHED" | string;
  confidence: number;
  confidence_adjustment: number;
  last_updated: string;
}

export interface LearningInsightItem {
  id: string;
  metric: string;
  title: string;
  description: string;
  average_bias: number;
  status: string;
  recommendation: string;
  timestamp: string;
}

export interface LearningEventItem {
  id: string;
  metric: string;
  event_type: string;
  old_value: number;
  new_value: number;
  reason: string;
  evidence_count: number;
  timestamp: string;
}

export interface AdaptiveMetricPerformance {
  metric: string;
  label: string;
  evaluated_count: number;
  accurate_count: number;
  underpredicted_count: number;
  overpredicted_count: number;
  accuracy_percent: number;
  average_absolute_error: number;
  bias: number;
  status: string;
}

export interface AdaptiveStatusResponse {
  status: "STABLE" | "LEARNING" | "CALIBRATION_REQUIRED" | "INSUFFICIENT_DATA" | string;
  active_calibrations_count: number;
  total_evaluated_predictions: number;
  overall_accuracy_percent: number;
  most_unreliable_metric: string;
  most_reliable_metric: string;
  last_updated: string;
}

export interface AdaptivePerformanceResponse {
  overall_accuracy: number;
  evaluated_predictions: number;
  metrics: AdaptiveMetricPerformance[];
  trend: string;
}

export interface CalibrationDemoResponse {
  metric: string;
  before_average_error: number;
  after_average_error: number;
  error_reduction_points: number;
  error_reduction_percent: number;
  message: string;
  sample_count: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  mode: string;
  services: {
    prediction: string;
    cascade: string;
    evidence: string;
    missions: string;
    simulation: string;
    adaptive: string;
    ai: string;
  };
  active_disaster: string;
  system_time: string;
}

export interface DemoTimelineStep {
  time: "T+0" | "T+30" | "T+60" | "T+180" | string;
  label: string;
  description: string;
  zone7_risk: number;
  zone7_isolation_minutes: number;
  road_accessibility_pct: number;
  telecom_pct: number;
  silent_crisis_flag: boolean;
}

export interface DemoStateResponse {
  event_id: string;
  title: string;
  intensity: string;
  current_time_step: string;
  timeline_steps: DemoTimelineStep[];
}

export interface DemoResetResponse {
  status: string;
  message: string;
  active_event: string;
  timeline_step: string;
  active_zones_count: number;
  available_teams_count: number;
}

export interface SimulationPreloadParams {
  zoneId?: string;
  interventions?: string[];
  scenarioName?: string;
  timeHorizon?: number;
}

export type MainNavMode = "COMMAND" | "LIVE" | "PREDICT" | "SIMULATE" | "MISSIONS" | "EVIDENCE" | "ADAPTIVE" | "AI" | "SYSTEM";



