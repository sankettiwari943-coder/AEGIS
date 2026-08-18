import {
  DisasterEvent, Zone, RoadSegment, Infrastructure, RescueTeam,
  PredictionResponse, ZoneCascadingRisk, ZoneCascadeDetailResponse,
  ZoneCascadeGraphResponse, CascadeChain, CascadeAlert, SilentRiskAssessment,
  EvidenceClaim, EvidenceItem, ClaimAssessment, DecisionEvidenceTrace, EvidenceSummaryResponse,
  MissionRecommendation, MultiMissionOptimizationPlan, MissionModifyRequest,
  SimulationRequest, SimulationComparison, InterventionItem, ResourceInventory, MultiScenarioComparisonResponse,
  FeedbackSubmission, FeedbackAnalysisResponse, AIChatResponse, TopPredictionItem, ZonePrediction,
  OrchestratorStructuredResponse, CommandBriefingResponse,
  OutcomeItem, CalibrationItem, LearningInsightItem, LearningEventItem,
  AdaptiveStatusResponse, AdaptivePerformanceResponse, CalibrationDemoResponse,
  HealthResponse, DemoStateResponse, DemoResetResponse,
  DisasterObservation, IngestionStatus, LiveFeedStepEvent,
  RAGQueryResult, RAGDocumentSummary, RAGStatusResponse,
  CVAnalysisResult, CVScanSummary
} from '../types';

const API_BASE = '/api';


export const api = {
  async getCurrentEvent(): Promise<DisasterEvent> {
    const res = await fetch(`${API_BASE}/event/current`);
    if (!res.ok) throw new Error('Failed to fetch current event');
    return res.json();
  },

  async getZones(): Promise<Zone[]> {
    const res = await fetch(`${API_BASE}/zones`);
    if (!res.ok) throw new Error('Failed to fetch zones');
    return res.json();
  },

  async getZone(id: string): Promise<Zone> {
    const res = await fetch(`${API_BASE}/zones/${id}`);
    if (!res.ok) throw new Error('Failed to fetch zone');
    return res.json();
  },

  async getRoads(): Promise<RoadSegment[]> {
    const res = await fetch(`${API_BASE}/roads`);
    if (!res.ok) throw new Error('Failed to fetch roads');
    return res.json();
  },

  async getInfrastructure(): Promise<Infrastructure[]> {
    const res = await fetch(`${API_BASE}/infrastructure`);
    if (!res.ok) throw new Error('Failed to fetch infrastructure');
    return res.json();
  },

  async getPredictions(): Promise<PredictionResponse> {
    const res = await fetch(`${API_BASE}/predictions`);
    if (!res.ok) throw new Error('Failed to fetch predictions');
    return res.json();
  },

  async getTopPredictions(): Promise<TopPredictionItem[]> {
    const res = await fetch(`${API_BASE}/predictions/top`);
    if (!res.ok) throw new Error('Failed to fetch top predictions');
    return res.json();
  },

  async getPredictionHorizon(minutes: number = 60): Promise<any[]> {
    const res = await fetch(`${API_BASE}/predictions/horizon/${minutes}`);
    if (!res.ok) throw new Error('Failed to fetch horizon predictions');
    return res.json();
  },

  async getZonePrediction(zoneId: string): Promise<ZonePrediction> {
    const res = await fetch(`${API_BASE}/predictions/${zoneId}`);
    if (!res.ok) throw new Error('Failed to fetch zone prediction');
    return res.json();
  },

  async getCascadingRisks(): Promise<ZoneCascadingRisk[]> {
    const res = await fetch(`${API_BASE}/risks`);
    if (!res.ok) throw new Error('Failed to fetch cascading risks');
    return res.json();
  },

  async getCascadeAssessments(): Promise<ZoneCascadeDetailResponse[]> {
    const res = await fetch(`${API_BASE}/cascades`);
    if (!res.ok) throw new Error('Failed to fetch cascade assessments');
    return res.json();
  },

  async getZoneCascade(zoneId: string): Promise<ZoneCascadeDetailResponse> {
    const res = await fetch(`${API_BASE}/cascades/${zoneId}`);
    if (!res.ok) throw new Error(`Failed to fetch cascade for zone ${zoneId}`);
    return res.json();
  },

  async getTopCascades(limit: number = 6): Promise<CascadeChain[]> {
    const res = await fetch(`${API_BASE}/cascades/top?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch top cascades');
    return res.json();
  },

  async getCascadeAlerts(): Promise<CascadeAlert[]> {
    const res = await fetch(`${API_BASE}/cascades/alerts`);
    if (!res.ok) throw new Error('Failed to fetch cascade alerts');
    return res.json();
  },

  async getZoneCascadeGraph(zoneId: string): Promise<ZoneCascadeGraphResponse> {
    const res = await fetch(`${API_BASE}/cascades/${zoneId}/graph`);
    if (!res.ok) throw new Error(`Failed to fetch cascade graph for zone ${zoneId}`);
    return res.json();
  },

  async getSilentRisks(): Promise<SilentRiskAssessment[]> {
    const res = await fetch(`${API_BASE}/silent-risks`);
    if (!res.ok) throw new Error('Failed to fetch silent risks');
    return res.json();
  },

  // Phase 5: Truth & Evidence Intelligence
  async getEvidenceItems(zoneId?: string, type?: string, status?: string): Promise<EvidenceItem[]> {
    const params = new URLSearchParams();
    if (zoneId) params.append('zone_id', zoneId);
    if (type) params.append('evidence_type', type);
    if (status) params.append('status', status);
    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/evidence${query}`);
    if (!res.ok) throw new Error('Failed to fetch evidence items');
    return res.json();
  },

  async getEvidenceSummary(): Promise<EvidenceSummaryResponse> {
    const res = await fetch(`${API_BASE}/evidence/summary`);
    if (!res.ok) throw new Error('Failed to fetch evidence summary');
    return res.json();
  },

  async getClaims(zoneId?: string, status?: string): Promise<ClaimAssessment[]> {
    const params = new URLSearchParams();
    if (zoneId) params.append('zone_id', zoneId);
    if (status) params.append('status', status);
    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/evidence/claims${query}`);
    if (!res.ok) throw new Error('Failed to fetch claims');
    return res.json();
  },

  async getClaim(claimId: string): Promise<ClaimAssessment> {
    const res = await fetch(`${API_BASE}/evidence/claims/${claimId}`);
    if (!res.ok) throw new Error(`Failed to fetch claim ${claimId}`);
    return res.json();
  },

  async getClaimSources(claimId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/evidence/claims/${claimId}/sources`);
    if (!res.ok) throw new Error(`Failed to fetch sources for claim ${claimId}`);
    return res.json();
  },

  async getClaimConflicts(claimId: string): Promise<any[]> {
    const res = await fetch(`${API_BASE}/evidence/claims/${claimId}/conflicts`);
    if (!res.ok) throw new Error(`Failed to fetch conflicts for claim ${claimId}`);
    return res.json();
  },

  async getDecisionEvidence(decisionId: string): Promise<DecisionEvidenceTrace> {
    const res = await fetch(`${API_BASE}/evidence/decisions/${decisionId}`);
    if (!res.ok) throw new Error(`Failed to fetch decision evidence for ${decisionId}`);
    return res.json();
  },

  async getEvidence(zoneId?: string): Promise<EvidenceClaim[]> {
    const url = zoneId ? `${API_BASE}/evidence/claims?zone_id=${zoneId}` : `${API_BASE}/evidence/claims`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch evidence');
    const claims = await res.json();
    return claims.map((c: any) => ({
      claim_id: c.claim_id,
      target_zone_id: c.target_zone_id,
      title: c.title,
      description: c.claim_statement,
      citizen_reports_count: c.supporting_sources_count,
      satellite_synthetic_score: c.ai_confidence_percent,
      telemetry_sensor_confirmed: true,
      contradicting_reports_count: c.conflicting_sources_count,
      ai_confidence_percent: c.ai_confidence_percent,
      status: c.status,
      evidence_chain: c.audit_trail
    }));
  },


  async getTeams(): Promise<RescueTeam[]> {
    const res = await fetch(`${API_BASE}/teams`);
    if (!res.ok) throw new Error('Failed to fetch teams');
    return res.json();
  },

  async getMissions(): Promise<MissionRecommendation[]> {
    const res = await fetch(`${API_BASE}/missions`);
    if (!res.ok) throw new Error('Failed to fetch missions');
    return res.json();
  },

  async getMission(missionId: string): Promise<MissionRecommendation> {
    const res = await fetch(`${API_BASE}/missions/${missionId}`);
    if (!res.ok) throw new Error(`Failed to fetch mission ${missionId}`);
    return res.json();
  },

  async getMissionRecommendations(zones?: string[], teams?: string[]): Promise<MultiMissionOptimizationPlan> {
    const params = new URLSearchParams();
    if (zones) zones.forEach(z => params.append('zones', z));
    if (teams) teams.forEach(t => params.append('teams', t));
    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/missions/recommendations${query}`);
    if (!res.ok) throw new Error('Failed to fetch fleet recommendations');
    return res.json();
  },

  async optimizeMission(zoneId: string = 'zone-7', victims: number = 12, medical: number = 3): Promise<MissionRecommendation> {
    const res = await fetch(`${API_BASE}/missions/optimize?target_zone_id=${zoneId}&victim_count=${victims}&medical_emergencies=${medical}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to optimize mission');
    return res.json();
  },

  async approveMission(missionId: string, teamId?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/missions/${missionId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mission_id: missionId, team_id: teamId })
    });
    if (!res.ok) {
      // Fallback to legacy endpoint
      const legacyRes = await fetch(`${API_BASE}/missions/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mission_id: missionId, team_id: teamId })
      });
      if (!legacyRes.ok) throw new Error('Failed to approve mission');
      return legacyRes.json();
    }
    return res.json();
  },

  async modifyMission(missionId: string, payload: MissionModifyRequest): Promise<MissionRecommendation> {
    const res = await fetch(`${API_BASE}/missions/${missionId}/modify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`Failed to modify mission ${missionId}`);
    return res.json();
  },

  async dismissMission(missionId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/missions/${missionId}/dismiss`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error(`Failed to dismiss mission ${missionId}`);
    return res.json();
  },

  async runSimulation(req: SimulationRequest): Promise<SimulationComparison> {
    const res = await fetch(`${API_BASE}/simulations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req)
    });
    if (!res.ok) throw new Error('Failed to run simulation');
    return res.json();
  },

  async getSimulationHistory(): Promise<SimulationComparison[]> {
    const res = await fetch(`${API_BASE}/simulations`);
    if (!res.ok) throw new Error('Failed to get simulation history');
    return res.json();
  },

  async getInterventionsCatalog(): Promise<InterventionItem[]> {
    const res = await fetch(`${API_BASE}/simulations/interventions`);
    if (!res.ok) throw new Error('Failed to get interventions catalog');
    return res.json();
  },

  async getSimulationResourceInventory(): Promise<ResourceInventory> {
    const res = await fetch(`${API_BASE}/simulations/inventory`);
    if (!res.ok) throw new Error('Failed to get simulation inventory');
    return res.json();
  },

  async compareSimulationScenarios(timeHorizon: number = 60, scenarios?: SimulationRequest[]): Promise<MultiScenarioComparisonResponse> {
    const res = await fetch(`${API_BASE}/simulations/compare?time_horizon=${timeHorizon}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ time_horizon: timeHorizon, scenarios: scenarios || [] })
    });
    if (!res.ok) throw new Error('Failed to compare scenarios');
    return res.json();
  },

  async applySimulationToMissions(scenarioId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/simulations/${scenarioId}/apply-to-missions`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error(`Failed to apply simulation ${scenarioId} to missions`);
    return res.json();
  },

  async submitFeedback(sub: FeedbackSubmission): Promise<FeedbackAnalysisResponse> {
    const res = await fetch(`${API_BASE}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(sub)
    });
    if (!res.ok) throw new Error('Failed to submit feedback');
    return res.json();
  },

  async getFeedbackHistory(): Promise<FeedbackAnalysisResponse[]> {
    const res = await fetch(`${API_BASE}/feedback`);
    if (!res.ok) throw new Error('Failed to get feedback');
    return res.json();
  },

  async chatAssistant(query: string, zoneId?: string, mode: string = 'LIVE', sessionId: string = 'demo-session'): Promise<AIChatResponse> {
    const res = await fetch(`${API_BASE}/orchestrator/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: sessionId, context_zone_id: zoneId, context_mode: mode })
    });
    if (!res.ok) {
      // Fallback to legacy endpoint
      const legacyRes = await fetch(`${API_BASE}/assistant/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, session_id: sessionId, context_zone_id: zoneId, context_mode: mode })
      });
      if (!legacyRes.ok) throw new Error('Failed to query assistant');
      return legacyRes.json();
    }
    return res.json();
  },

  async orchestratorChat(query: string, sessionId: string = 'demo-session', zoneId?: string, mode: string = 'LIVE'): Promise<OrchestratorStructuredResponse> {
    const res = await fetch(`${API_BASE}/orchestrator/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: sessionId, context_zone_id: zoneId, context_mode: mode })
    });
    if (!res.ok) throw new Error('Failed to query orchestrator chat');
    return res.json();
  },

  async orchestratorQuery(query: string, sessionId: string = 'demo-session', zoneId?: string, mode: string = 'LIVE'): Promise<OrchestratorStructuredResponse> {
    const res = await fetch(`${API_BASE}/orchestrator/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: sessionId, context_zone_id: zoneId, context_mode: mode })
    });
    if (!res.ok) throw new Error('Failed to run orchestrator query');
    return res.json();
  },

  async getCommandBriefing(sessionId: string = 'demo-session'): Promise<CommandBriefingResponse> {
    const res = await fetch(`${API_BASE}/orchestrator/briefing`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId })
    });
    if (!res.ok) throw new Error('Failed to generate command briefing');
    return res.json();
  },

  async getOrchestratorTools(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/orchestrator/tools`);
    if (!res.ok) throw new Error('Failed to fetch orchestrator tools');
    return res.json();
  },

  // Phase 9: Adaptive Response & Learning Loop
  async getAdaptiveStatus(): Promise<AdaptiveStatusResponse> {
    const res = await fetch(`${API_BASE}/adaptive/status`);
    if (!res.ok) throw new Error('Failed to fetch adaptive status');
    return res.json();
  },

  async getAdaptivePerformance(): Promise<AdaptivePerformanceResponse> {
    const res = await fetch(`${API_BASE}/adaptive/performance`);
    if (!res.ok) throw new Error('Failed to fetch adaptive performance');
    return res.json();
  },

  async getAdaptiveCalibrations(): Promise<CalibrationItem[]> {
    const res = await fetch(`${API_BASE}/adaptive/calibrations`);
    if (!res.ok) throw new Error('Failed to fetch calibrations');
    return res.json();
  },

  async getAdaptiveInsights(): Promise<LearningInsightItem[]> {
    const res = await fetch(`${API_BASE}/adaptive/insights`);
    if (!res.ok) throw new Error('Failed to fetch learning insights');
    return res.json();
  },

  async triggerAdaptiveCalibration(): Promise<CalibrationItem[]> {
    const res = await fetch(`${API_BASE}/adaptive/calibrate`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to trigger recalibration');
    return res.json();
  },

  async getAdaptiveHistory(): Promise<LearningEventItem[]> {
    const res = await fetch(`${API_BASE}/adaptive/history`);
    if (!res.ok) throw new Error('Failed to fetch adaptive audit history');
    return res.json();
  },

  async getAdaptiveOutcomes(): Promise<OutcomeItem[]> {
    const res = await fetch(`${API_BASE}/adaptive/outcomes`);
    if (!res.ok) throw new Error('Failed to fetch evaluated outcomes');
    return res.json();
  },

  async runCalibrationDemo(): Promise<CalibrationDemoResponse> {
    const res = await fetch(`${API_BASE}/adaptive/demo-replay`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to run calibration demo');
    return res.json();
  },

  async getFeedbackOutcome(id: string): Promise<OutcomeItem> {
    const res = await fetch(`${API_BASE}/feedback/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch feedback outcome ${id}`);
    return res.json();
  },

  // Phase 10: Health & Demo State
  async getHealthStatus(): Promise<HealthResponse> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Failed to fetch system health status');
    return res.json();
  },

  async resetDemo(): Promise<DemoResetResponse> {
    const res = await fetch(`${API_BASE}/demo/reset`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset demo scenario');
    return res.json();
  },

  async getDemoState(): Promise<DemoStateResponse> {
    const res = await fetch(`${API_BASE}/demo/state`);
    if (!res.ok) throw new Error('Failed to fetch demo state');
    return res.json();
  },

  // Priority 1 & 4: Ingestion & Live Feed Simulator
  async getIngestionStatus(): Promise<IngestionStatus> {
    const res = await fetch(`${API_BASE}/ingestion/status`);
    if (!res.ok) throw new Error('Failed to fetch ingestion status');
    return res.json();
  },

  async getObservations(zoneId?: string, hazardType?: string, sourceType?: string, limit: number = 50): Promise<DisasterObservation[]> {
    const params = new URLSearchParams();
    if (zoneId) params.append('zone_id', zoneId);
    if (hazardType) params.append('hazard_type', hazardType);
    if (sourceType) params.append('source_type', sourceType);
    params.append('limit', limit.toString());
    const res = await fetch(`${API_BASE}/ingestion/observations?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch observations');
    return res.json();
  },

  async getZoneTelemetry(zoneId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ingestion/telemetry/${zoneId}`);
    if (!res.ok) throw new Error(`Failed to fetch telemetry for zone ${zoneId}`);
    return res.json();
  },

  async startLiveFeed(): Promise<any> {
    const res = await fetch(`${API_BASE}/ingestion/demo/start`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to start live feed simulator');
    return res.json();
  },

  async stopLiveFeed(): Promise<any> {
    const res = await fetch(`${API_BASE}/ingestion/demo/stop`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to stop live feed simulator');
    return res.json();
  },

  async stepLiveFeed(): Promise<LiveFeedStepEvent> {
    const res = await fetch(`${API_BASE}/ingestion/demo/step`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to advance live feed simulation step');
    return res.json();
  },

  async resetLiveFeed(): Promise<any> {
    const res = await fetch(`${API_BASE}/ingestion/demo/reset`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset live feed simulator');
    return res.json();
  },

  // Priority 2: RAG Emergency Knowledge Layer
  async queryRAG(query: string, topK: number = 3, category?: string): Promise<RAGQueryResult> {
    const res = await fetch(`${API_BASE}/rag/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: topK, category })
    });
    if (!res.ok) throw new Error('Failed to query emergency RAG knowledge base');
    return res.json();
  },

  async getRAGDocuments(): Promise<RAGDocumentSummary[]> {
    const res = await fetch(`${API_BASE}/rag/documents`);
    if (!res.ok) throw new Error('Failed to fetch RAG documents catalog');
    return res.json();
  },

  async getRAGStatus(): Promise<RAGStatusResponse> {
    const res = await fetch(`${API_BASE}/rag/status`);
    if (!res.ok) throw new Error('Failed to fetch RAG service status');
    return res.json();
  },

  // Priority 3: Computer Vision Reconnaissance
  async analyzeCV(zoneId: string = 'zone-7', scanId?: string): Promise<CVAnalysisResult> {
    const res = await fetch(`${API_BASE}/cv/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_zone_id: zoneId, scan_id: scanId })
    });
    if (!res.ok) throw new Error('Failed to run computer vision analysis');
    return res.json();
  },

  async getCVScans(): Promise<CVScanSummary[]> {
    const res = await fetch(`${API_BASE}/cv/scans`);
    if (!res.ok) throw new Error('Failed to fetch CV scans catalog');
    return res.json();
  },

  async getCVScan(scanId: string): Promise<CVAnalysisResult> {
    const res = await fetch(`${API_BASE}/cv/scans/${scanId}`);
    if (!res.ok) throw new Error(`Failed to fetch CV scan ${scanId}`);
    return res.json();
  }
};




