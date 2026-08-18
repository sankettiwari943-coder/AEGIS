import React, { useState } from 'react';
import { MainNavMode, DisasterEvent } from '../../types';
import { useDemo } from '../../context/DemoContext';
import { 
  ShieldAlert, 
  Activity, 
  Radio, 
  Layers, 
  Cpu, 
  FileCheck, 
  Sliders, 
  AlertTriangle,
  Flame,
  CheckCircle2,
  Clock,
  RotateCcw,
  Sparkles,
  LayoutDashboard
} from 'lucide-react';

interface HeaderProps {
  currentMode: MainNavMode;
  onSelectMode: (mode: MainNavMode) => void;
  event: DisasterEvent | null;
}

export const Header: React.FC<HeaderProps> = ({ currentMode, onSelectMode, event }) => {
  const { health } = useDemo();
  const [showHealthModal, setShowHealthModal] = useState(false);

  const modes: { id: MainNavMode; label: string; icon: any; hotkey: string }[] = [
    { id: 'COMMAND', label: 'COMMAND', icon: LayoutDashboard, hotkey: '1' },
    { id: 'LIVE', label: 'LIVE HUD', icon: Activity, hotkey: '2' },
    { id: 'PREDICT', label: 'PREDICT', icon: Clock, hotkey: '3' },
    { id: 'SIMULATE', label: 'SIMULATE', icon: Sliders, hotkey: '4' },
    { id: 'MISSIONS', label: 'MISSIONS', icon: ShieldAlert, hotkey: '5' },
    { id: 'EVIDENCE', label: 'EVIDENCE', icon: FileCheck, hotkey: '6' },
    { id: 'ADAPTIVE', label: 'ADAPTIVE', icon: RotateCcw, hotkey: '7' },
    { id: 'AI', label: 'AI', icon: Sparkles, hotkey: '8' }
  ];



  return (
    <header className="w-full bg-[#070b12] border-b border-slate-800/80 px-4 py-2 flex flex-wrap items-center justify-between z-30 select-none shadow-2xl relative">
      {/* Brand & Incident Banner */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2.5">
          <div className="relative flex items-center justify-center w-9 h-9 rounded-lg bg-cyan-950/60 border border-cyan-500/40 text-cyan-400 font-mono font-black text-xl shadow-[0_0_15px_rgba(0,240,255,0.25)]">
            <span>Æ</span>
            <div className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-cyan-400 animate-ping"></div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono font-extrabold tracking-widest text-lg text-white">AEGIS</span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                v1.0.0-PRO
              </span>
            </div>
            <p className="text-[10px] tracking-wider text-slate-400 uppercase font-mono">
              AI Emergency & Geospatial Intelligence
            </p>
          </div>
        </div>

        {/* Tactical Separator */}
        <div className="h-7 w-[1px] bg-slate-800 hidden md:block"></div>

        {/* Operational Status & Active Incident */}
        <div className="hidden lg:flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-emerald-950/40 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="font-semibold">OPERATIONAL</span>
          </div>

          <div className="flex items-center space-x-2 px-2.5 py-1 rounded bg-slate-900 border border-slate-700/60 text-xs font-mono">
            <Flame className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
            <span className="text-slate-400">INCIDENT:</span>
            <span className="text-amber-300 font-bold tracking-wide">
              {event ? event.disaster_type : 'URBAN FLOOD'}
            </span>
            <span className="px-1.5 py-0.2 rounded text-[10px] bg-red-950/80 text-red-400 border border-red-500/40 font-semibold animate-pulse">
              ESCALATING
            </span>
          </div>
        </div>
      </div>

      {/* Primary 8 Modes Navigation HUD */}
      <nav className="flex items-center space-x-1 sm:space-x-1.5 my-1 sm:my-0">
        {modes.map((mode) => {
          const Icon = mode.icon;
          const isActive = currentMode === mode.id;
          
          return (
            <button
              key={mode.id}
              onClick={() => onSelectMode(mode.id)}
              className={`flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg text-xs font-mono font-bold tracking-wider transition-all duration-200 ${
                isActive
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400 shadow-[0_0_15px_rgba(0,240,255,0.35)]'
                  : 'bg-slate-900/90 text-slate-400 border border-slate-800 hover:border-slate-700 hover:text-slate-200'
              }`}
              title={`Navigate to ${mode.label} (Hotkey: ${mode.hotkey})`}
            >
              <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400 animate-pulse' : 'text-slate-400'}`} />
              <span>{mode.label}</span>
              <span className={`text-[9px] px-1 rounded ${isActive ? 'bg-cyan-500 text-black font-black' : 'bg-slate-950 text-slate-600'}`}>
                {mode.hotkey}
              </span>
            </button>
          );
        })}
      </nav>

      {/* Real-time System Metrics HUD & System Health */}
      <div className="flex items-center space-x-2.5">
        
        {/* System Health Status Button & Popover */}
        <div className="relative">
          <button
            onClick={() => setShowHealthModal(!showHealthModal)}
            className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700/80 text-xs font-mono hover:border-cyan-500/50 transition-all"
            title="Click to view AI Engine Health"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span className="text-slate-400 hidden lg:inline">ENGINES:</span>
            <span className="text-emerald-400 font-bold">ONLINE</span>
          </button>

          {showHealthModal && (
            <div className="absolute right-0 top-full mt-2 w-72 bg-[#090f1c] border border-cyan-500/40 rounded-xl p-3.5 shadow-2xl z-50 space-y-2.5 font-mono text-xs animate-in zoom-in-95">
              <div className="flex justify-between items-center border-b border-slate-800 pb-1.5">
                <span className="text-cyan-400 font-bold">AEGIS SYSTEM HEALTH</span>
                <span className="text-[10px] text-slate-500">v1.0.0</span>
              </div>
              <div className="space-y-1 text-[11px] font-sans">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Prediction Engine:</span>
                  <span className="text-emerald-400 font-bold">● ONLINE</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Cascading Risk Engine:</span>
                  <span className="text-emerald-400 font-bold">● ONLINE</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Evidence & Silent Risk:</span>
                  <span className="text-emerald-400 font-bold">● ONLINE</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Multi-Mission Optimizer:</span>
                  <span className="text-emerald-400 font-bold">● ONLINE</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">What-If Simulation Engine:</span>
                  <span className="text-emerald-400 font-bold">● ONLINE</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Adaptive Learning Loop:</span>
                  <span className="text-cyan-400 font-bold">● LEARNING</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">AI Disaster Orchestrator:</span>
                  <span className="text-purple-400 font-bold">● ONLINE</span>
                </div>
              </div>
              <div className="pt-1.5 border-t border-slate-800 text-[10px] text-slate-400 flex justify-between">
                <span>Active Disaster:</span>
                <span className="text-white font-bold truncate max-w-[140px]">Flood Event — Northern Corridor</span>
              </div>
            </div>
          )}
        </div>

        {/* Silent Risk Warning Badge */}
        <div className="hidden sm:flex items-center space-x-1.5 px-2 py-1 rounded-lg bg-red-950/40 border border-red-500/40 text-red-400 text-xs font-mono">
          <Radio className="w-3.5 h-3.5 animate-pulse" />
          <span className="font-bold">SILENT:</span>
          <span className="bg-red-900/60 px-1.5 py-0.2 rounded font-black text-red-200">
            {event?.silent_risk_zones_count ?? 2}
          </span>
        </div>

      </div>
    </header>
  );

};
