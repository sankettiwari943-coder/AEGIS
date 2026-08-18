import React from 'react';
import { useDemo } from '../../context/DemoContext';
import { MainNavMode } from '../../types';
import {
  RotateCcw,
  BookOpen,
  Clock
} from 'lucide-react';

interface DemoControllerBarProps {
  currentMode?: MainNavMode;
  onNavigate?: (mode: MainNavMode, zoneId?: string) => void;
}

export const DemoControllerBar: React.FC<DemoControllerBarProps> = () => {
  const {
    scenarioTime,
    setScenarioTime,
    scenarioIntensity,
    setDemoGuideOpen,
    setShowResetModal,
    currentTimelineStepData
  } = useDemo();

  const timelineOptions = ['T+0', 'T+30', 'T+60', 'T+180'];
  const intensityOptions: ('Normal' | 'Escalating' | 'Critical')[] = ['Normal', 'Escalating', 'Critical'];

  return (
    <div className="w-full bg-[#050810] border-b border-cyan-500/20 px-3 py-1.5 flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-300 z-20 shadow-md">
      
      {/* Left: Scenario & Intensity Indicator */}
      <div className="flex items-center space-x-2.5">
        <div className="flex items-center space-x-1 px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-black tracking-wider">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
          <span>DEMO MODE</span>
        </div>

        <span className="text-slate-400 hidden sm:inline">
          SCENARIO: <strong className="text-white">Flood — Northern Corridor</strong>
        </span>

        {/* Intensity indicator */}
        <div className="hidden md:flex items-center space-x-1 pl-1">
          <span className="text-[10px] text-slate-500 mr-1">INTENSITY:</span>
          {intensityOptions.map((lvl) => {
            const isActive = scenarioIntensity === lvl;
            return (
              <span
                key={lvl}
                className={`px-1.5 py-0.5 rounded text-[9px] font-bold border transition-all cursor-default select-none ${
                  isActive
                    ? lvl === 'Critical'
                      ? 'bg-red-500/20 text-red-300 border-red-500/60 shadow-[0_0_8px_rgba(239,68,68,0.3)]'
                      : lvl === 'Escalating'
                      ? 'bg-amber-500/20 text-amber-300 border-amber-500/60 shadow-[0_0_8px_rgba(245,158,11,0.3)]'
                      : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/60 shadow-[0_0_8px_rgba(16,185,129,0.3)]'
                    : 'bg-slate-950/80 text-slate-600 border-slate-800/60 opacity-60'
                }`}
              >
                {lvl}
              </span>
            );
          })}
        </div>
      </div>

      {/* Center: Timeline Scrubber */}
      <div className="flex items-center space-x-2 my-1 sm:my-0">
        <div className="flex items-center space-x-1">
          <Clock className="w-3 h-3 text-cyan-400" />
          <span className="text-[10px] text-slate-400 font-bold">TIMELINE:</span>
        </div>

        <div className="flex items-center bg-slate-900/90 rounded border border-slate-700/80 p-0.5 space-x-0.5">
          {timelineOptions.map((t) => {
            const active = scenarioTime === t;
            return (
              <button
                key={t}
                onClick={() => setScenarioTime(t)}
                className={`px-2 py-0.5 rounded text-[10px] font-black transition-all ${
                  active
                    ? 'bg-cyan-500 text-black shadow-[0_0_10px_rgba(0,240,255,0.4)]'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {t}
              </button>
            );
          })}
        </div>

        {currentTimelineStepData && (
          <span className="text-[10px] text-cyan-300 hidden lg:inline pl-1">
            Z7 Risk: <strong className="text-white">{currentTimelineStepData.zone7_risk}</strong>
            {currentTimelineStepData.zone7_isolation_minutes > 0 ? (
              <> | Isolation: <strong className="text-amber-400">~{currentTimelineStepData.zone7_isolation_minutes}m</strong></>
            ) : (
              <strong className="text-red-400"> | ISOLATED</strong>
            )}
          </span>
        )}
      </div>

      {/* Right: Guide & Reset */}
      <div className="flex items-center space-x-2">
        {/* Demo Guide Modal Trigger */}
        <button
          onClick={() => setDemoGuideOpen(true)}
          className="px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 text-cyan-300 hover:text-cyan-200 border border-cyan-500/40 text-[10px] font-bold flex items-center space-x-1 transition-all shadow-[0_0_10px_rgba(0,240,255,0.15)]"
        >
          <BookOpen className="w-3 h-3 text-cyan-400" />
          <span>DEMO GUIDE</span>
        </button>

        {/* Reset Demo Trigger */}
        <button
          onClick={() => setShowResetModal(true)}
          className="px-2 py-1 rounded bg-slate-900 hover:bg-red-950/60 text-slate-400 hover:text-red-300 border border-slate-700 hover:border-red-500/50 text-[10px] font-bold flex items-center space-x-1 transition-all"
          title="Reset Demo Scenario to Baseline T+0"
        >
          <RotateCcw className="w-3 h-3 text-red-400" />
          <span className="hidden sm:inline">RESET DEMO</span>
        </button>
      </div>

    </div>
  );
};
