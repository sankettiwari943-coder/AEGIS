import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { LiveFeedStepEvent, IngestionStatus, MainNavMode } from '../../types';
import { DataSourceBadge } from '../common/DataSourceBadge';
import {
  Radio,
  Play,
  Square,
  FastForward,
  RotateCcw,
  AlertTriangle,
  Zap,
  Activity,
  CheckCircle2,
  TrendingUp,
  Droplets
} from 'lucide-react';

interface LiveFeedPanelProps {
  onNavigate: (mode: MainNavMode, zoneId?: string) => void;
  onStepTriggered?: (event: LiveFeedStepEvent) => void;
}

export const LiveFeedPanel: React.FC<LiveFeedPanelProps> = ({
  onNavigate,
  onStepTriggered
}) => {
  const [status, setStatus] = useState<IngestionStatus | null>(null);
  const [lastEvent, setLastEvent] = useState<LiveFeedStepEvent | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeStep, setActiveStep] = useState<number>(0);

  const fetchStatus = async () => {
    try {
      const st = await api.getIngestionStatus();
      setStatus(st);
      setActiveStep(st.simulation_step || 0);
    } catch (err) {
      console.error('Failed to fetch ingestion status:', err);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleStep = async () => {
    try {
      setLoading(true);
      const event = await api.stepLiveFeed();
      setLastEvent(event);
      setActiveStep(event.step);
      if (onStepTriggered) onStepTriggered(event);
      await fetchStatus();
    } catch (err) {
      console.error('Failed to step live feed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      setLoading(true);
      await api.resetLiveFeed();
      setLastEvent(null);
      setActiveStep(0);
      await fetchStatus();
    } catch (err) {
      console.error('Failed to reset live feed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[#0a101f] border border-cyan-500/40 rounded-2xl p-4 shadow-xl select-none space-y-3">
      
      {/* Top Controller Strip */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
        
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">
            <Radio className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-xs sm:text-sm font-black text-white tracking-wider flex items-center space-x-1.5">
                <span>LIVE FEED SIMULATOR & TELEMETRY STREAM</span>
              </h3>
              <DataSourceBadge sourceType="SIMULATED" sourceLabel="DEMO STREAM" size="sm" />
            </div>
            <p className="text-[10px] text-slate-400 font-sans mt-0.5">
              Injects realistic incident telemetry updates into the Prediction, Cascade, and Mission engines.
            </p>
          </div>
        </div>

        {/* Simulator Control Action Buttons */}
        <div className="flex items-center space-x-2">
          
          {/* Step Progression Button */}
          <button
            onClick={handleStep}
            disabled={loading}
            className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-black text-xs shadow-[0_0_15px_rgba(6,182,212,0.35)] disabled:opacity-40 flex items-center space-x-1.5 transition-all"
          >
            <FastForward className="w-3.5 h-3.5" />
            <span>{loading ? 'SIMULATING...' : activeStep === 0 ? 'START SIMULATOR (STEP 1)' : `TRIGGER NEXT STEP (${activeStep + 1 > 5 ? 1 : activeStep + 1}/5)`}</span>
          </button>

          {/* Reset Button */}
          <button
            onClick={handleReset}
            disabled={loading || activeStep === 0}
            className="px-2.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-700 text-xs font-bold disabled:opacity-30 flex items-center space-x-1 transition-all"
            title="Reset to Baseline T+0"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>RESET</span>
          </button>
        </div>

      </div>

      {/* Step Progression Indicators */}
      <div className="grid grid-cols-5 gap-2">
        {[
          { step: 1, label: "1. Rain Surge", desc: "Doppler +28%", target: "Zone 7" },
          { step: 2, label: "2. River Crest", desc: "Depth 185cm", target: "Zone 7" },
          { step: 3, label: "3. Road 14 Cut", desc: "Passability 18%", target: "Zone 7" },
          { step: 4, label: "4. Telecom Loss", desc: "Tower Outage", target: "Zone 4" },
          { step: 5, label: "5. Substation", desc: "Cascade Alarm", target: "Zone 7" }
        ].map((s) => {
          const isDone = activeStep >= s.step;
          const isCurrent = activeStep === s.step;
          return (
            <div
              key={s.step}
              className={`p-2 rounded-lg border text-[10px] transition-all flex flex-col justify-between space-y-1 ${
                isCurrent
                  ? 'bg-cyan-950/70 border-cyan-400 text-cyan-200 shadow-[0_0_10px_rgba(6,182,212,0.25)]'
                  : isDone
                  ? 'bg-slate-900/90 border-emerald-500/50 text-emerald-300'
                  : 'bg-slate-950/60 border-slate-800 text-slate-500'
              }`}
            >
              <div className="flex items-center justify-between font-bold">
                <span>{s.label}</span>
                {isDone && <CheckCircle2 className="w-3 h-3 text-emerald-400" />}
              </div>
              <div className="text-[9px] font-sans opacity-80 truncate">{s.desc}</div>
            </div>
          );
        })}
      </div>

      {/* Dynamic Telemetry Event Banner */}
      {lastEvent ? (
        <div className="p-3 bg-gradient-to-r from-red-950/40 via-slate-900/90 to-slate-900/90 border border-red-500/40 rounded-xl space-y-2 animate-in fade-in">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2 text-red-400 font-bold text-xs">
              <AlertTriangle className="w-4 h-4 animate-pulse" />
              <span>SIMULATED EVENT INJECTED: {lastEvent.title.toUpperCase()}</span>
            </div>
            <span className="text-[9px] px-2 py-0.5 rounded bg-red-950 text-red-300 border border-red-500/50 font-bold font-mono">
              TARGET: {lastEvent.target_zone}
            </span>
          </div>

          <p className="text-xs text-slate-300 font-sans leading-relaxed">
            {lastEvent.description}
          </p>

          <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-slate-800/80 text-[10px]">
            <div className="text-cyan-300 font-mono">
              <strong>Telemetry Delta:</strong> {lastEvent.delta_description}
            </div>
            <div className="flex items-center space-x-1 text-slate-400">
              <span>Engines Recalculated:</span>
              <span className="text-white font-bold">{lastEvent.impacted_engines.join(', ')}</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-2.5 bg-slate-950/60 rounded-xl border border-slate-800/80 text-[11px] text-slate-400 font-sans flex items-center justify-between">
          <span>Ready to simulate evolving disaster timeline. Click <strong>"START SIMULATOR"</strong> to advance live flood progression.</span>
          <span className="text-[10px] text-cyan-400 font-mono font-bold">T+0 BASELINE</span>
        </div>
      )}

    </div>
  );
};
