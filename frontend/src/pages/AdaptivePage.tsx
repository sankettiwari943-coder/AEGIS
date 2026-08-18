import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  AdaptiveStatusResponse,
  AdaptivePerformanceResponse,
  CalibrationItem,
  LearningInsightItem,
  LearningEventItem,
  OutcomeItem,
  CalibrationDemoResponse,
  MainNavMode
} from '../types';
import {
  RotateCcw,
  Activity,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  Cpu,
  Sliders,
  Sparkles,
  Zap,
  ShieldCheck,
  Send,
  X,
  FileCheck,
  Check,
  ArrowRight,
  Info,
  Clock,
  Radio
} from 'lucide-react';

interface AdaptivePageProps {
  onNavigate?: (mode: MainNavMode, zoneId?: string) => void;
}

export const AdaptivePage: React.FC<AdaptivePageProps> = ({ onNavigate }) => {
  const [status, setStatus] = useState<AdaptiveStatusResponse | null>(null);
  const [performance, setPerformance] = useState<AdaptivePerformanceResponse | null>(null);
  const [calibrations, setCalibrations] = useState<CalibrationItem[]>([]);
  const [insights, setInsights] = useState<LearningInsightItem[]>([]);
  const [auditEvents, setAuditEvents] = useState<LearningEventItem[]>([]);
  const [outcomes, setOutcomes] = useState<OutcomeItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Calibration Demo State
  const [demoRunning, setDemoRunning] = useState(false);
  const [demoResult, setDemoResult] = useState<CalibrationDemoResponse | null>(null);

  // Active Learning Loop Step
  const [activeLoopStep, setActiveLoopStep] = useState<number>(0);

  // Feedback Form State
  const [feedbackMetric, setFeedbackMetric] = useState<string>('road_accessibility');
  const [feedbackZone, setFeedbackZone] = useState<string>('zone-7');
  const [feedbackPredicted, setFeedbackPredicted] = useState<number>(70);
  const [feedbackActual, setFeedbackActual] = useState<number>(35);
  const [feedbackSource, setFeedbackSource] = useState<string>('Operator Observation');
  const [feedbackNotes, setFeedbackNotes] = useState<string>('');
  
  // Confirmation Modal State
  const [showConfirmModal, setShowConfirmModal] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [submitSuccessMsg, setSubmitSuccessMsg] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [st, perf, calibs, ins, history, outs] = await Promise.all([
        api.getAdaptiveStatus(),
        api.getAdaptivePerformance(),
        api.getAdaptiveCalibrations(),
        api.getAdaptiveInsights(),
        api.getAdaptiveHistory(),
        api.getAdaptiveOutcomes()
      ]);
      setStatus(st);
      setPerformance(perf);
      setCalibrations(calibs);
      setInsights(ins);
      setAuditEvents(history);
      setOutcomes(outs);
    } catch (err) {
      console.error('Failed to fetch adaptive data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Animate Learning Loop step cycler
  useEffect(() => {
    const timer = setInterval(() => {
      setActiveLoopStep((prev) => (prev + 1) % 7);
    }, 3500);
    return () => clearInterval(timer);
  }, []);

  const handleRunDemo = async () => {
    try {
      setDemoRunning(true);
      const res = await api.runCalibrationDemo();
      setDemoResult(res);
      await fetchData();
    } catch (err) {
      console.error('Failed to run calibration demo:', err);
    } finally {
      setDemoRunning(false);
    }
  };

  const handleConfirmSubmit = async () => {
    try {
      setSubmitting(true);
      const resp = await api.submitFeedback({
        metric: feedbackMetric,
        target_zone_id: feedbackZone,
        predicted_value: feedbackPredicted,
        actual_value: feedbackActual,
        source: feedbackSource,
        notes: feedbackNotes || `Observation submitted via Adaptive Command Form.`
      });
      setShowConfirmModal(false);
      setSubmitSuccessMsg(resp.recalibration_summary);
      setTimeout(() => setSubmitSuccessMsg(null), 6000);
      setFeedbackNotes('');
      await fetchData();
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const loopSteps = [
    { label: '1. PREDICT', desc: 'Hydrological & risk models project horizons (T+30m, T+60m)' },
    { label: '2. ACT', desc: 'Command team deploys resources & issues alerts' },
    { label: '3. OBSERVE', desc: 'Real/simulated ground truth observations recorded' },
    { label: '4. COMPARE', desc: 'Compute error (Predicted vs Reality divergence)' },
    { label: '5. ERROR', desc: 'Classify accurate vs systematic under/overprediction' },
    { label: '6. CALIBRATE', desc: 'Recalibrate model factors with safe bounds (±20 pts)' },
    { label: '7. PREDICT BETTER', desc: 'Future estimates apply explainable calibration factor' }
  ];

  // Error trend mock series for visualization
  const trendPoints = [
    { seq: 'Obs 1', err: 24 },
    { seq: 'Obs 2', err: 19 },
    { seq: 'Obs 3', err: 17 },
    { seq: 'Obs 4', err: 11 },
    { seq: 'Obs 5 (Post-Calib)', err: 7 }
  ];

  return (
    <div className="w-full h-full bg-[#060a12] text-slate-200 overflow-y-auto p-4 sm:p-6 font-mono select-none space-y-6">
      
      {/* Top Banner: Prototype & Demo Dataset Notice */}
      <div className="bg-gradient-to-r from-cyan-950/80 via-slate-900/90 to-blue-950/80 border border-cyan-500/40 rounded-xl p-3.5 flex flex-wrap items-center justify-between shadow-lg">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-[0_0_15px_rgba(0,240,255,0.3)]">
            <RotateCcw className="w-5 h-5 animate-spin-slow" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base font-black text-white tracking-wider">
                AEGIS ADAPTIVE INTELLIGENCE & LEARNING LOOP
              </h1>
              <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-black">
                DEMO DATASET
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Learn from outcomes. Detect systematic bias. Recalibrate future estimates.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3 mt-2 sm:mt-0">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs">
            <span className="text-slate-400">STATUS:</span>
            <span className="flex items-center space-x-1 text-cyan-400 font-bold">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
              <span>{status?.status || 'LEARNING'}</span>
            </span>
          </div>
          <button
            onClick={fetchData}
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700 transition-all"
            title="Refresh Recalibration Telemetry"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Success Notification Alert */}
      {submitSuccessMsg && (
        <div className="bg-emerald-950/80 border border-emerald-500/50 p-3 rounded-lg flex items-center space-x-2 text-emerald-200 text-xs animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{submitSuccessMsg}</span>
        </div>
      )}

      {/* Signature Visual: Interactive Animated AEGIS Learning Loop */}
      <div className="hud-card p-5 rounded-xl border border-cyan-500/50 shadow-[0_0_30px_rgba(0,240,255,0.15)] space-y-3 bg-[#080e1a]/95">
        <div className="flex justify-between items-center border-b border-slate-800 pb-2">
          <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs">
            <Zap className="w-4 h-4 text-amber-400" />
            <span className="tracking-wider uppercase">SIGNATURE VISUAL: THE AEGIS LEARNING LOOP</span>
          </div>
          <span className="text-[10px] text-slate-500">Autonomous Feedback & Explainable Recalibration</span>
        </div>

        {/* 7 Step Animated Ribbon */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 pt-2">
          {loopSteps.map((step, idx) => {
            const isActive = activeLoopStep === idx;
            return (
              <div
                key={idx}
                onClick={() => setActiveLoopStep(idx)}
                className={`p-2.5 rounded-lg border transition-all cursor-pointer flex flex-col justify-between ${
                  isActive
                    ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300 shadow-[0_0_20px_rgba(0,240,255,0.3)] scale-105'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between text-[11px] font-black">
                  <span>{step.label}</span>
                  {isActive && <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>}
                </div>
                <p className="text-[9px] font-sans mt-1 leading-snug text-slate-300">
                  {step.desc}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* KPI Performance Header Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        
        {/* Card 1: Overall Evaluated Accuracy */}
        <div className="hud-card p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>EVALUATED ACCURACY</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2">
            <div className="text-3xl font-black text-white tracking-tight">
              {status ? `${status.overall_accuracy_percent}%` : '82%'}
            </div>
            <div className="text-[10px] text-slate-400 mt-1">
              Based on {status?.total_evaluated_predictions || 24} evaluated demo outcomes
            </div>
          </div>
          <div className="mt-3 pt-2 border-t border-slate-800/80 text-[9px] text-slate-500 flex justify-between">
            <span>Benchmark: Prototype Dataset</span>
            <span className="text-emerald-400 font-bold">STABLE</span>
          </div>
        </div>

        {/* Card 2: Road Network Deterioration Status */}
        <div className="hud-card p-4 rounded-xl border border-amber-500/40 bg-amber-950/10 flex flex-col justify-between">
          <div className="flex items-center justify-between text-amber-300 text-xs">
            <span>ROAD ACCESSIBILITY</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-2">
            <div className="text-3xl font-black text-amber-400 tracking-tight">
              68%
            </div>
            <div className="text-[10px] text-amber-200/80 mt-1">
              Systematic Underprediction (-9.4 bias)
            </div>
          </div>
          <div className="mt-3 pt-2 border-t border-amber-500/30 text-[9px] text-amber-300 flex justify-between font-bold">
            <span>CALIBRATION:</span>
            <span>-8.0 PTS APPLIED</span>
          </div>
        </div>

        {/* Card 3: Hospital Trauma Access Status */}
        <div className="hud-card p-4 rounded-xl border border-emerald-500/40 bg-emerald-950/10 flex flex-col justify-between">
          <div className="flex items-center justify-between text-emerald-300 text-xs">
            <span>HOSPITAL ACCESS</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2">
            <div className="text-3xl font-black text-emerald-400 tracking-tight">
              89%
            </div>
            <div className="text-[10px] text-emerald-200/80 mt-1">
              High Accuracy (7 of 8 within ±5%)
            </div>
          </div>
          <div className="mt-3 pt-2 border-t border-emerald-500/30 text-[9px] text-emerald-300 flex justify-between font-bold">
            <span>CALIBRATION:</span>
            <span>STABLE (0.0 PTS)</span>
          </div>
        </div>

        {/* Card 4: Mission Travel Time Calibration */}
        <div className="hud-card p-4 rounded-xl border border-cyan-500/40 bg-cyan-950/10 flex flex-col justify-between">
          <div className="flex items-center justify-between text-cyan-300 text-xs">
            <span>MISSION ETA DRAG</span>
            <Clock className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-2">
            <div className="text-3xl font-black text-cyan-400 tracking-tight">
              +4.0m
            </div>
            <div className="text-[10px] text-cyan-200/80 mt-1">
              Hydrological Surface Drag Calibrated
            </div>
          </div>
          <div className="mt-3 pt-2 border-t border-cyan-500/30 text-[9px] text-cyan-300 flex justify-between font-bold">
            <span>CALIBRATION:</span>
            <span>ACTIVE (100% CONF)</span>
          </div>
        </div>

      </div>

      {/* Main Grid: Before vs After Replay Demo (Left) + Performance Trend Chart (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Before vs After Calibration Visualizer & Demo (7 cols) */}
        <div className="lg:col-span-7 hud-card p-5 rounded-xl border border-slate-800 flex flex-col justify-between space-y-4">
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span>BEFORE VS AFTER CALIBRATION DEMO</span>
            </div>
            <button
              onClick={handleRunDemo}
              disabled={demoRunning}
              className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-black text-xs shadow-[0_0_15px_rgba(0,240,255,0.4)] disabled:opacity-40 flex items-center space-x-1.5 transition-all"
            >
              <span>{demoRunning ? 'REPLAYING...' : 'RUN CALIBRATION DEMO'}</span>
              <RotateCcw className={`w-3.5 h-3.5 ${demoRunning ? 'animate-spin' : ''}`} />
            </button>
          </div>

          {/* Side-by-Side Comparison Visual */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-1">
            
            {/* BEFORE CALIBRATION */}
            <div className="p-4 rounded-xl bg-red-950/20 border border-red-500/40 space-y-3">
              <div className="flex justify-between items-center border-b border-red-500/30 pb-1.5">
                <span className="text-[10px] font-black text-red-400 uppercase tracking-wider">
                  BEFORE CALIBRATION
                </span>
                <span className="px-1.5 py-0.2 rounded bg-red-900/60 text-red-300 text-[9px] font-bold">
                  UNMITIGATED
                </span>
              </div>
              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Road Prediction:</span>
                  <span className="text-white font-bold">70%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Observed Actual:</span>
                  <span className="text-white font-bold">35%</span>
                </div>
                <div className="flex justify-between pt-1 border-t border-red-900/40 font-bold">
                  <span className="text-red-300">Historical Average Error:</span>
                  <span className="text-red-400 text-sm">22.0 pts</span>
                </div>
              </div>
              <div className="text-[10px] text-red-200/80 bg-red-950/40 p-2 rounded">
                Persistent underprediction of road degradation during peak river crests.
              </div>
            </div>

            {/* AFTER CALIBRATION */}
            <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/40 space-y-3">
              <div className="flex justify-between items-center border-b border-emerald-500/30 pb-1.5">
                <span className="text-[10px] font-black text-emerald-400 uppercase tracking-wider">
                  AFTER CALIBRATION
                </span>
                <span className="px-1.5 py-0.2 rounded bg-emerald-900/60 text-emerald-300 text-[9px] font-bold">
                  DEMO ESTIMATE
                </span>
              </div>
              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Adjusted Estimate:</span>
                  <span className="text-cyan-300 font-bold">59% (-11.0 pts)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Observed Actual:</span>
                  <span className="text-white font-bold">35%</span>
                </div>
                <div className="flex justify-between pt-1 border-t border-emerald-900/40 font-bold">
                  <span className="text-emerald-300">Expected Average Error:</span>
                  <span className="text-emerald-400 text-sm">11.0 pts</span>
                </div>
              </div>
              <div className="text-[10px] text-emerald-200/80 bg-emerald-950/40 p-2 rounded">
                Statistical bias compensation delivers 50.0% reduction in average error.
              </div>
            </div>

          </div>

          {/* Dynamic Result Banner */}
          {demoResult && (
            <div className="p-3 bg-cyan-950/40 border border-cyan-500/50 rounded-lg flex items-center justify-between text-xs animate-in zoom-in-95">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <span className="font-bold text-white">
                  CALIBRATION IMPROVEMENT: {demoResult.error_reduction_percent}% REDUCTION IN HISTORICAL ERROR
                </span>
              </div>
              <span className="text-emerald-400 font-black">
                -{demoResult.error_reduction_points} pts Error Drop
              </span>
            </div>
          )}

          <div className="text-[10px] text-slate-500 font-mono">
            * Note: Recalibration applies statistical empirical corrections to future predictions without destructively altering raw hydrodynamic models.
          </div>
        </div>

        {/* Right Column: Performance Error Trend Over Time (5 cols) */}
        <div className="lg:col-span-5 hud-card p-5 rounded-xl border border-slate-800 flex flex-col justify-between space-y-4">
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              <span>PREDICTION ERROR TREND OVER TIME</span>
            </div>
            <span className="text-[10px] text-emerald-400 font-bold">TREND: IMPROVING</span>
          </div>

          {/* SVG Trend Line Chart */}
          <div className="relative h-44 w-full bg-slate-950/80 rounded-lg p-3 border border-slate-800 flex flex-col justify-between">
            <div className="text-[9px] text-slate-500 flex justify-between">
              <span>High Error (30 pts)</span>
              <span>Low Error (0 pts)</span>
            </div>

            {/* Custom SVG Line */}
            <svg className="w-full h-24 overflow-visible">
              <polyline
                fill="none"
                stroke="#06b6d4"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
                points="20,15 90,32 160,40 230,62 300,78"
              />
              {/* Nodes */}
              <circle cx="20" cy="15" r="4" fill="#ef4444" />
              <circle cx="90" cy="32" r="4" fill="#f59e0b" />
              <circle cx="160" cy="40" r="4" fill="#f59e0b" />
              <circle cx="230" cy="62" r="4" fill="#10b981" />
              <circle cx="300" cy="78" r="5" fill="#06b6d4" />
            </svg>

            {/* Labels under nodes */}
            <div className="flex justify-between text-[8px] text-slate-400 px-1">
              <span>Obs 1 (24 pts)</span>
              <span>Obs 2 (19)</span>
              <span>Obs 3 (17)</span>
              <span>Obs 4 (11)</span>
              <span className="text-cyan-300 font-bold">Obs 5 (7 pts)</span>
            </div>
          </div>

          <div className="p-2.5 bg-slate-900/80 rounded border border-slate-800 text-[10px] text-slate-400">
            Average prediction divergence has systematically decreased by <strong className="text-emerald-400">70.8%</strong> across the last 5 observation sequences.
          </div>
        </div>

      </div>

      {/* Middle Grid: Human Observation Entry Form (Left) + Learning Insights Cards (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Human Operator Observation Submission Form (6 cols) */}
        <div className="lg:col-span-6 hud-card p-5 rounded-xl border border-slate-800 space-y-4">
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs">
              <FileCheck className="w-4 h-4 text-cyan-400" />
              <span>SUBMIT OPERATOR GROUND TRUTH OBSERVATION</span>
            </div>
            <span className="text-[10px] text-slate-400">Human-in-the-Loop Feedback</span>
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              setShowConfirmModal(true);
            }}
            className="space-y-3 text-xs"
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">TARGET METRIC</label>
                <select
                  value={feedbackMetric}
                  onChange={(e) => setFeedbackMetric(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400"
                >
                  <option value="road_accessibility">Road Accessibility (%)</option>
                  <option value="hospital_accessibility">Hospital Accessibility (%)</option>
                  <option value="mission_eta">Mission Travel Time (min)</option>
                  <option value="predicted_isolation_time">Sector Isolation Time (min)</option>
                  <option value="flood_risk">Flood Risk Score (0-100)</option>
                </select>
              </div>

              <div>
                <label className="text-[10px] text-slate-400 block mb-1">MONITORED ZONE</label>
                <select
                  value={feedbackZone}
                  onChange={(e) => setFeedbackZone(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400"
                >
                  <option value="zone-7">Zone 7 — River Bend Lowlands</option>
                  <option value="zone-4">Zone 4 — Riverside Slums</option>
                  <option value="zone-6">Zone 6 — Industrial Park</option>
                  <option value="zone-3">Zone 3 — North Suburbs</option>
                  <option value="zone-1">Zone 1 — City Core</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">PREDICTED VALUE</label>
                <input
                  type="number"
                  value={feedbackPredicted}
                  onChange={(e) => setFeedbackPredicted(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400"
                />
              </div>

              <div>
                <label className="text-[10px] text-slate-400 block mb-1">OBSERVED ACTUAL VALUE</label>
                <input
                  type="number"
                  value={feedbackActual}
                  onChange={(e) => setFeedbackActual(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400"
                />
              </div>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 block mb-1">OBSERVATION SOURCE</label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
                {['Operator Observation', 'Sensor Telemetry', 'Official Update', 'Simulation Feedback'].map((src) => (
                  <button
                    type="button"
                    key={src}
                    onClick={() => setFeedbackSource(src)}
                    className={`py-1.5 px-2 rounded text-[10px] font-bold border transition-all ${
                      feedbackSource === src
                        ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400'
                        : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    {src}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 block mb-1">FIELD OBSERVATION NOTES (OPTIONAL)</label>
              <input
                type="text"
                value={feedbackNotes}
                onChange={(e) => setFeedbackNotes(e.target.value)}
                placeholder="e.g. Bridge approach submerged earlier than forecasted..."
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                className="w-full py-2 rounded bg-cyan-500 hover:bg-cyan-400 text-black font-black text-xs flex items-center justify-center space-x-1.5 shadow-[0_0_15px_rgba(0,240,255,0.3)] transition-all"
              >
                <span>VERIFY & SUBMIT OBSERVATION</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </form>
        </div>

        {/* Right Column: Actionable Learning Insights (6 cols) */}
        <div className="lg:col-span-6 hud-card p-5 rounded-xl border border-slate-800 space-y-3">
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>AEGIS LEARNING INSIGHTS</span>
            </div>
            <span className="text-[10px] text-slate-400">Systematic Bias Findings</span>
          </div>

          <div className="space-y-2.5 overflow-y-auto max-h-[340px] pr-1 scrollbar-thin">
            {insights.map((ins) => (
              <div
                key={ins.id}
                className="p-3 bg-slate-950/70 rounded-lg border border-slate-800 space-y-1.5"
              >
                <div className="flex justify-between items-center">
                  <span className="font-bold text-white text-xs">{ins.title}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[9px] font-extrabold ${
                      ins.status === 'STABLE'
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40'
                        : ins.status === 'CALIBRATED'
                        ? 'bg-cyan-950 text-cyan-300 border border-cyan-500/40'
                        : 'bg-amber-950 text-amber-300 border border-amber-500/40'
                    }`}
                  >
                    {ins.status}
                  </span>
                </div>
                <p className="text-[11px] font-sans text-slate-300 leading-snug">
                  {ins.description}
                </p>
                <div className="pt-1 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
                  <span className="text-slate-500">Historical Bias: <strong className="text-amber-400">{ins.average_bias > 0 ? `+${ins.average_bias}` : ins.average_bias} pts</strong></span>
                  <span className="text-cyan-300 font-sans italic">{ins.recommendation}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Bottom Grid: Recent Evaluated Outcomes Stream (Left) + Calibration Audit Trail (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Recent Outcomes Timeline (7 cols) */}
        <div className="lg:col-span-7 hud-card p-5 rounded-xl border border-slate-800 space-y-3">
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs">
              <Activity className="w-4 h-4 text-cyan-400" />
              <span>RECENT EVALUATED OUTCOMES TIMELINE</span>
            </div>
            <span className="text-[10px] text-slate-400">{outcomes.length} Total Outcomes</span>
          </div>

          <div className="space-y-2 overflow-y-auto max-h-[300px] pr-1 scrollbar-thin">
            {outcomes.slice(0, 10).map((o) => (
              <div
                key={o.id}
                className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800/80 flex items-center justify-between text-xs"
              >
                <div className="space-y-0.5">
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-500 font-mono text-[10px]">{o.observation_time || '12:00'}</span>
                    <span className="text-white font-bold text-xs">{o.zone_name || o.zone_id}</span>
                    <span className="text-slate-400 text-[10px]">• {o.metric.replace('_', ' ')}</span>
                  </div>
                  <div className="text-[10px] text-slate-400 font-sans">
                    Predicted: <strong className="text-slate-200">{o.predicted_value}</strong> | Actual: <strong className="text-white">{o.actual_value}</strong> | Source: <span className="text-cyan-300">{o.source}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <div className="text-right">
                    <div className="text-[10px] text-slate-400">Error: <span className="font-bold text-amber-400">{o.error > 0 ? `+${o.error}` : o.error} pts</span></div>
                  </div>
                  <span
                    className={`px-2 py-1 rounded text-[9px] font-black ${
                      o.status === 'ACCURATE'
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40'
                        : o.status === 'UNDERPREDICTED'
                        ? 'bg-amber-950 text-amber-300 border border-amber-500/40'
                        : 'bg-blue-950 text-blue-300 border border-blue-500/40'
                    }`}
                  >
                    {o.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Calibration Audit Log (5 cols) */}
        <div className="lg:col-span-5 hud-card p-5 rounded-xl border border-slate-800 space-y-3">
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs">
              <FileCheck className="w-4 h-4 text-cyan-400" />
              <span>RECALIBRATION AUDIT TRAIL</span>
            </div>
            <span className="text-[10px] text-slate-400">Auditable Learning Events</span>
          </div>

          <div className="space-y-2 overflow-y-auto max-h-[300px] pr-1 scrollbar-thin">
            {auditEvents.map((evt) => (
              <div
                key={evt.id}
                className="p-2.5 bg-slate-950/70 rounded-lg border border-slate-800/80 space-y-1 text-xs"
              >
                <div className="flex justify-between items-center text-[10px]">
                  <span className="text-cyan-300 font-bold">{evt.metric.replace('_', ' ').toUpperCase()}</span>
                  <span className="text-slate-500">{evt.timestamp}</span>
                </div>
                <p className="text-[10px] font-sans text-slate-300 leading-snug">
                  {evt.reason}
                </p>
                <div className="flex justify-between items-center pt-1 border-t border-slate-900 text-[9px] text-slate-400">
                  <span>Adjustment: {evt.old_value} &rarr; <strong className="text-emerald-400">{evt.new_value > 0 ? `+${evt.new_value.toFixed(1)}` : evt.new_value.toFixed(1)} pts</strong></span>
                  <span>Evidence: {evt.evidence_count} samples</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Confirmation Modal to Prevent Accidental Submissions */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-[#0b1220] border border-cyan-500/60 rounded-xl p-5 shadow-2xl space-y-4 animate-in zoom-in-95">
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <div className="flex items-center space-x-2 text-cyan-400 font-bold text-sm">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>CONFIRM GROUND TRUTH OBSERVATION</span>
              </div>
              <button
                onClick={() => setShowConfirmModal(false)}
                className="p-1 text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Metric:</span>
                <span className="text-white font-bold">{feedbackMetric.replace('_', ' ').toUpperCase()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Sector:</span>
                <span className="text-cyan-300 font-bold">{feedbackZone.toUpperCase()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Predicted Value:</span>
                <span className="text-slate-200 font-bold">{feedbackPredicted}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Observed Actual:</span>
                <span className="text-white font-bold">{feedbackActual}</span>
              </div>
              <div className="flex justify-between pt-1 border-t border-slate-800">
                <span className="text-slate-400">Divergence:</span>
                <span className="text-amber-400 font-bold">{(feedbackActual - feedbackPredicted) > 0 ? `+${feedbackActual - feedbackPredicted}` : (feedbackActual - feedbackPredicted)} pts</span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-400">Source:</span>
                <span className="text-emerald-400 font-bold">{feedbackSource}</span>
              </div>
            </div>

            <p className="text-[10px] font-sans text-slate-400">
              Submitting this observation will update empirical error metrics and trigger statistical recalibration for {feedbackMetric}.
            </p>

            <div className="flex space-x-2 pt-2">
              <button
                onClick={() => setShowConfirmModal(false)}
                className="flex-1 py-2 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 text-xs font-bold"
              >
                CANCEL
              </button>
              <button
                onClick={handleConfirmSubmit}
                disabled={submitting}
                className="flex-1 py-2 rounded bg-cyan-500 hover:bg-cyan-400 text-black text-xs font-black shadow-[0_0_15px_rgba(0,240,255,0.4)]"
              >
                {submitting ? 'RECORDING...' : 'CONFIRM & RECALIBRATE'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
