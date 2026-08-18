import React from 'react';
import { useDemo } from '../../context/DemoContext';
import { MainNavMode } from '../../types';
import {
  BookOpen,
  X,
  ArrowRight,
  ShieldAlert,
  Clock,
  Layers,
  Radio,
  Sliders,
  Sparkles,
  RotateCcw,
  CheckCircle2,
  Activity,
  RefreshCw
} from 'lucide-react';

interface DemoGuideModalProps {
  onNavigate: (mode: MainNavMode, zoneId?: string) => void;
}

export const DemoGuideModal: React.FC<DemoGuideModalProps> = ({ onNavigate }) => {
  const { demoGuideOpen, setDemoGuideOpen, setScenarioTime, setPendingSimulationParams, setShowResetModal } = useDemo();

  if (!demoGuideOpen) return null;

  const steps = [
    {
      stepNum: 1,
      title: 'Problem Detection & Live Ingestion',
      mode: 'COMMAND' as MainNavMode,
      time: 'T+0',
      zoneId: 'zone-7',
      icon: ShieldAlert,
      tag: 'DETECT',
      keyLine: '"AEGIS does not just report what has happened. It anticipates what happens next."',
      details: 'Start at Command Home. Ingestion pipeline streams Doppler radar ($74 mm/h) and river gauges ($7.90m). Flag Zone 7 isolation in ~42 minutes.',
      actionLabel: '1. COMMAND CENTER'
    },
    {
      stepNum: 2,
      title: 'Tactical GIS & Aerial CV Scans',
      mode: 'LIVE' as MainNavMode,
      time: 'T+0',
      zoneId: 'zone-7',
      icon: Activity,
      tag: 'VISION',
      keyLine: '"Automated Computer Vision extracts 78% flood coverage and 91% road inundation from satellite scans."',
      details: 'Inspect 12 live polygon zones on MapLibre HUD. Open Computer Vision panel for Sentinel-2/drone structural damage heatmaps.',
      actionLabel: '2. TACTICAL GIS HUD'
    },
    {
      stepNum: 3,
      title: 'Forward Horizon Prediction',
      mode: 'PREDICT' as MainNavMode,
      time: 'T+30',
      zoneId: 'zone-7',
      icon: Clock,
      tag: 'PREDICT',
      keyLine: '"T+0 (82) → T+30m (89) → T+60m (94) — forecast curves warn while evacuation routes remain open."',
      details: 'Inspect timeline escalation curves. Observe how Zone 7 road passability drops from 42% to 15% as countdown reaches zero.',
      actionLabel: '3. PREDICTION ENGINE'
    },
    {
      stepNum: 4,
      title: 'Cascading Infrastructure Chain',
      mode: 'PREDICT' as MainNavMode,
      time: 'T+0',
      zoneId: 'zone-7',
      icon: Layers,
      tag: 'CASCADE',
      keyLine: '"A flood is never an isolated event: Bridge cutoff → Hospital cutoff -45% → Substation #2 failure."',
      details: 'Trace multi-hop failure chain. Backwater overtopping Substation #2 trips Basin Drainage Pump #1, flooding Zone 6 industrial sector.',
      actionLabel: '4. CASCADING RISKS'
    },
    {
      stepNum: 5,
      title: 'Evidence & Silent Crisis Anomaly',
      mode: 'EVIDENCE' as MainNavMode,
      time: 'T+0',
      zoneId: 'zone-4',
      icon: Radio,
      tag: 'SILENT RISK',
      keyLine: '"Zero civilian SOS reports do not mean zero victims—Tower Delta-4 is down!"',
      details: 'Highlight Zone 4 (Riverside Slums, Pop: 9,300). Cross-reference zero SOS calls with dead cell tower amid 145cm waters to flag Silent Crisis.',
      actionLabel: '5. EVIDENCE & SILENT RISK'
    },
    {
      stepNum: 6,
      title: 'Mission Optimization & Human Approval',
      mode: 'MISSIONS' as MainNavMode,
      time: 'T+0',
      zoneId: 'zone-7',
      icon: CheckCircle2,
      tag: 'DISPATCH',
      keyLine: '"Team R2 (Boats + Meds) is chosen over closer Team R1 (Trucks) due to submerged bridge constraints."',
      details: 'Demonstrate multi-criteria optimization. Inspect staged dispatch with cryptographic authorization token under Awaiting Human Approval.',
      actionLabel: '6. FLEET MISSIONS'
    },
    {
      stepNum: 7,
      title: 'The WOW Moment: What-If Sandbox',
      mode: 'SIMULATE' as MainNavMode,
      time: 'T+60',
      zoneId: 'zone-7',
      icon: Sliders,
      tag: 'SIMULATE',
      keyLine: '"Compare: Do Nothing (91 Risk) vs Evacuate Z7 + Deploy R2 (64 Risk) → 27 pts net reduction!"',
      details: 'Execute dual-scenario comparison in real time. Validate tactical intervention impact before committing first responders in the field.',
      actionLabel: '7. WHAT-IF SANDBOX'
    },
    {
      stepNum: 8,
      title: 'AI Orchestrator & SOP RAG',
      mode: 'AI' as MainNavMode,
      time: 'T+0',
      zoneId: 'zone-7',
      icon: Sparkles,
      tag: 'ORCHESTRATE',
      keyLine: '"Deterministic engine tools + SOP vector citations provide hallucination-free tactical reasoning."',
      details: 'Submit query: What should we do in Zone 7? Inspect live tool execution trace, SOP-FL-04 grounding, and click [APPLY TO MISSION PLAN].',
      actionLabel: '8. AI ORCHESTRATOR'
    },
    {
      stepNum: 9,
      title: 'Adaptive Learning & Calibration',
      mode: 'ADAPTIVE' as MainNavMode,
      time: 'T+0',
      zoneId: 'zone-7',
      icon: RotateCcw,
      tag: 'LEARN',
      keyLine: '"Detect systematic model bias and achieve 50% historical error reduction post-calibration."',
      details: 'Inspect the closed-loop feedback engine, outcome divergence history, and run the Before vs After Calibration Replay Demo.',
      actionLabel: '9. ADAPTIVE LEARNING'
    },
    {
      stepNum: 10,
      title: 'Instant Sub-Second Demo Reset',
      mode: 'COMMAND' as MainNavMode,
      time: 'T+0',
      zoneId: 'zone-7',
      icon: RefreshCw,
      tag: 'RESET',
      keyLine: '"Restore all simulation states, mission approvals, and telemetry back to T+0 in <100ms."',
      details: 'Click [RESET DEMO] in the top controller bar or execute POST /api/demo/reset to return to a pristine operational starting state.',
      actionLabel: '10. RESET SCENARIO'
    }
  ];

  const handleStepClick = (step: typeof steps[0]) => {
    if (step.stepNum === 10) {
      setDemoGuideOpen(false);
      setShowResetModal(true);
      return;
    }
    setScenarioTime(step.time);
    if (step.mode === 'SIMULATE') {
      setPendingSimulationParams({
        zoneId: 'zone-7',
        scenarioName: 'Evacuate Zone 7 + Deploy Delta-2',
        interventions: ['evacuate_zone_7', 'deploy_team_r2'],
        timeHorizon: 60
      });
    }
    onNavigate(step.mode, step.zoneId);
    setDemoGuideOpen(false);
  };

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="w-full max-w-5xl max-h-[92vh] bg-[#070b14] border border-cyan-500/60 rounded-2xl shadow-[0_0_50px_rgba(0,240,255,0.2)] flex flex-col overflow-hidden font-mono text-slate-200 animate-in zoom-in-95">
        
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-slate-800 flex justify-between items-center bg-[#090f1c]">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-[0_0_15px_rgba(0,240,255,0.3)]">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-black text-white tracking-wider flex items-center space-x-2">
                <span>AEGIS HACKATHON DEMO GUIDE</span>
                <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 text-[10px] font-bold">
                  10-STEP COMPLETE ARC (5-7 MIN)
                </span>
              </h2>
            </div>
          </div>

          <button
            onClick={() => setDemoGuideOpen(false)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Steps Grid */}
        <div className="p-4 sm:p-5 overflow-y-auto space-y-3 flex-1 scrollbar-thin">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {steps.map((s) => {
              const Icon = s.icon;
              return (
                <div
                  key={s.stepNum}
                  className="hud-card p-3.5 rounded-xl border border-slate-800/90 hover:border-cyan-500/60 transition-all flex flex-col justify-between space-y-2 bg-slate-950/70"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex items-center space-x-2">
                      <span className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 flex items-center justify-center text-xs font-black shrink-0">
                        {s.stepNum}
                      </span>
                      <h3 className="font-bold text-white text-xs">{s.title}</h3>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-cyan-400 text-[9px] font-black tracking-wider shrink-0">
                      {s.tag}
                    </span>
                  </div>

                  <blockquote className="text-[11px] font-sans text-amber-300/90 italic bg-amber-950/20 p-2 rounded border-l-2 border-amber-400 leading-snug">
                    {s.keyLine}
                  </blockquote>

                  <p className="text-[10px] font-sans text-slate-400 leading-snug">
                    {s.details}
                  </p>

                  <div className="pt-2 border-t border-slate-800/80 flex justify-between items-center">
                    <span className="text-[9px] text-slate-500">Target Time: <strong className="text-cyan-300">{s.time}</strong></span>
                    <button
                      onClick={() => handleStepClick(s)}
                      className="px-2.5 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500 text-cyan-300 hover:text-black border border-cyan-500/50 font-black text-[10px] flex items-center space-x-1 transition-all shadow-[0_0_10px_rgba(0,240,255,0.2)]"
                    >
                      <span>{s.actionLabel}</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="p-3.5 bg-[#090f1c] border-t border-slate-800 flex justify-between items-center text-xs">
          <span className="text-slate-400 font-sans text-[11px]">
            Tip: Press keyboard hotkeys <strong className="text-cyan-300 font-mono">1–8</strong> for fast instant navigation during your presentation.
          </span>
          <button
            onClick={() => setDemoGuideOpen(false)}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs"
          >
            CLOSE GUIDE
          </button>
        </div>

      </div>
    </div>
  );
};
