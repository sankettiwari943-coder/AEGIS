import React, { useState, useEffect } from 'react';
import { FeedbackSubmission, FeedbackAnalysisResponse } from '../types';
import { api } from '../services/api';
import { 
  Cpu, 
  Activity, 
  CheckCircle2, 
  RotateCcw, 
  Send, 
  TrendingUp, 
  Database, 
  Server, 
  Radio,
  Sliders,
  ShieldCheck
} from 'lucide-react';

export const SystemPage: React.FC = () => {
  // Feedback form state
  const [predictedEta, setPredictedEta] = useState(10);
  const [actualEta, setActualEta] = useState(17);
  const [predictedRoad, setPredictedRoad] = useState(70);
  const [actualRoad, setActualRoad] = useState(35);
  const [observations, setObservations] = useState('Corridor 14 bridge overtopping caused 7 minute rescue transit delay.');
  
  const [feedbackHistory, setFeedbackHistory] = useState<FeedbackAnalysisResponse[]>([]);
  const [lastResponse, setLastResponse] = useState<FeedbackAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const hist = await api.getFeedbackHistory();
        setFeedbackHistory(hist);
      } catch (err) {
        console.error(err);
      }
    };
    fetchHistory();
  }, []);

  const handleSubmitFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const resp = await api.submitFeedback({
        mission_id: 'mission-feedback-01',
        target_zone_id: 'zone-7',
        predicted_eta_minutes: predictedEta,
        actual_eta_minutes: actualEta,
        predicted_road_access_pct: predictedRoad,
        actual_road_access_pct: actualRoad,
        observations
      });
      setLastResponse(resp);
      setFeedbackHistory((prev) => [resp, ...prev]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const agents = [
    { name: 'SituationAgent', role: 'Real-time telemetry & environmental sensing', status: 'ACTIVE', calls: 248 },
    { name: 'PredictionAgent', role: '90-min deterministic inundation & isolation trajectory', status: 'ACTIVE', calls: 192 },
    { name: 'RiskAgent', role: 'Dependency graph cascading risk & silent crisis detector', status: 'ACTIVE', calls: 310 },
    { name: 'RescueAgent', role: 'Multi-criteria asset utility & capability triage optimizer', status: 'ACTIVE', calls: 145 },
    { name: 'VerificationAgent', role: 'Multi-source Bayesian truth & synthetic SAR verification', status: 'ACTIVE', calls: 86 },
    { name: 'GISAgent', role: 'MapLibre GL JS vector topology & dynamic isochrone rendering', status: 'ACTIVE', calls: 412 },
    { name: 'DisasterOrchestrator', role: 'Central routing & Gemini 2.5/Flash structured synthesis', status: 'ACTIVE', calls: 520 },
  ];

  return (
    <div className="w-full h-full flex flex-col space-y-3 p-4 overflow-y-auto font-mono text-xs">
      {/* Top Banner */}
      <div className="hud-card p-4 rounded-lg flex flex-wrap items-center justify-between gap-3 border-l-4 border-l-cyan-400">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-cyan-400 font-bold text-sm">ADAPTIVE FEEDBACK & SPECIALIZED AI AGENTS ARCHITECTURE</span>
            <span className="px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-[10px]">
              OBSERVE → LEARN → RECALIBRATE
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            AEGIS closes the operational loop by comparing predictive model outputs against post-mission field ground truth.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="text-emerald-300 font-bold">ALL 7 SPECIALIZED AGENTS ONLINE</span>
        </div>
      </div>

      {/* Main Grid: Adaptive Feedback Form on Left, Agent Architecture on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1">
        {/* Left Column: Adaptive Feedback Input Form (6 cols) */}
        <div className="lg:col-span-6 flex flex-col space-y-3">
          <div className="hud-card p-4 rounded-lg space-y-3 flex-1 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <div className="font-bold text-slate-200 text-sm">
                  POST-MISSION OPERATIONAL GROUND TRUTH
                </div>
                <span className="text-slate-400 text-[10px]">Section 18 Feedback Loop</span>
              </div>

              <form onSubmit={handleSubmitFeedback} className="space-y-3 mt-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-slate-400 text-[11px]">PREDICTED ETA (MIN):</label>
                    <input
                      type="number"
                      value={predictedEta}
                      onChange={(e) => setPredictedEta(parseInt(e.target.value))}
                      className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-cyan-300 font-bold"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-slate-400 text-[11px]">ACTUAL OBSERVED ETA (MIN):</label>
                    <input
                      type="number"
                      value={actualEta}
                      onChange={(e) => setActualEta(parseInt(e.target.value))}
                      className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-amber-300 font-bold"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-slate-400 text-[11px]">PREDICTED ROAD ACCESS (%):</label>
                    <input
                      type="number"
                      value={predictedRoad}
                      onChange={(e) => setPredictedRoad(parseInt(e.target.value))}
                      className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-cyan-300 font-bold"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-slate-400 text-[11px]">ACTUAL ROAD ACCESS (%):</label>
                    <input
                      type="number"
                      value={actualRoad}
                      onChange={(e) => setActualRoad(parseInt(e.target.value))}
                      className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-red-400 font-bold"
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-slate-400 text-[11px]">OPERATOR FIELD OBSERVATIONS:</label>
                  <textarea
                    value={observations}
                    onChange={(e) => setObservations(e.target.value)}
                    rows={2}
                    className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-slate-200 text-xs font-mono"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 rounded bg-cyan-500 hover:bg-cyan-400 text-black font-extrabold text-xs flex items-center justify-center space-x-1.5 transition-all shadow-[0_0_15px_rgba(0,240,255,0.3)]"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>RECORD GROUND TRUTH & RECALIBRATE MODEL</span>
                </button>
              </form>
            </div>

            {/* Recalibration Telemetry Display */}
            {lastResponse && (
              <div className="mt-3 p-3 rounded bg-cyan-950/40 border border-cyan-500/40 space-y-1.5">
                <div className="flex justify-between items-center text-cyan-300 font-bold">
                  <span>MODEL RECALIBRATION RESULT</span>
                  <span className="text-emerald-400">STATUS: {lastResponse.status}</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-slate-300 text-[11px]">
                  <div>ETA Error: <span className="text-amber-400 font-bold">{lastResponse.eta_error_minutes > 0 ? `+${lastResponse.eta_error_minutes}` : lastResponse.eta_error_minutes} min</span></div>
                  <div>Road Access Error: <span className="text-red-400 font-bold">{lastResponse.road_access_error_pct > 0 ? `+${lastResponse.road_access_error_pct}` : lastResponse.road_access_error_pct}%</span></div>
                  <div className="col-span-2">
                    Model Confidence Shift: <span className="text-slate-400">{lastResponse.previous_model_confidence_pct}%</span> → <span className="text-cyan-300 font-black text-sm">{lastResponse.updated_model_confidence_pct}%</span>
                  </div>
                </div>
                <p className="text-[10px] text-slate-400 font-sans mt-1">{lastResponse.recalibration_summary}</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Specialized AI Agents Hierarchy (6 cols) */}
        <div className="lg:col-span-6 flex flex-col space-y-3">
          <div className="hud-card p-4 rounded-lg space-y-3 flex-1 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <div className="font-bold text-slate-200">SPECIALIZED AI AGENT ORCHESTRATION</div>
                <span className="text-slate-400 text-[10px]">Modular Backend Services</span>
              </div>

              <div className="mt-3 space-y-2">
                {agents.map((agent) => (
                  <div
                    key={agent.name}
                    className="p-2.5 rounded bg-slate-900/80 border border-slate-800 flex items-center justify-between"
                  >
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-cyan-300">{agent.name}</span>
                        <span className="px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-400 border border-emerald-500/30 text-[9px] font-bold">
                          {agent.status}
                        </span>
                      </div>
                      <div className="text-[10px] text-slate-400 mt-0.5">{agent.role}</div>
                    </div>

                    <div className="text-right shrink-0">
                      <div className="text-[9px] text-slate-500 uppercase">Requests Handled</div>
                      <div className="text-slate-200 font-bold">{agent.calls} calls</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-3 rounded bg-slate-900 border border-slate-800 text-[11px] text-slate-400 space-y-1">
              <div className="text-slate-300 font-bold flex items-center space-x-1.5">
                <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                <span>Gemini 2.5 / Flash Integration:</span>
              </div>
              <p className="text-[10px] font-sans">
                Consumes structured telemetry JSON to generate tactical briefings and explain cascading chains without hallucinating coordinates or casualty values.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
