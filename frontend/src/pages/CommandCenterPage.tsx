import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useDemo } from '../context/DemoContext';
import {
  DisasterEvent,
  Zone,
  RoadSegment,
  Infrastructure,
  RescueTeam,
  MainNavMode,
  OrchestratorStructuredResponse
} from '../types';
import { TacticalMap } from '../components/map/TacticalMap';
import { IntelligencePipeline } from '../components/command-center/IntelligencePipeline';
import { LiveFeedPanel } from '../components/command-center/LiveFeedPanel';
import { DataSourceBadge } from '../components/common/DataSourceBadge';
import { ConfidenceBadge } from '../components/common/ConfidenceBadge';
import {
  ShieldAlert,
  AlertTriangle,
  Clock,
  Radio,
  Sliders,
  Sparkles,
  FileCheck,
  CheckCircle2,
  Send,
  Zap,
  ArrowRight,
  TrendingUp,
  Layers,
  Cpu,
  Activity,
  Info,
  BookOpen
} from 'lucide-react';



interface CommandCenterPageProps {
  event: DisasterEvent | null;
  zones: Zone[];
  roads: RoadSegment[];
  infrastructure: Infrastructure[];
  rescueTeams: RescueTeam[];
  selectedZone: Zone | null;
  onSelectZone: (zone: Zone) => void;
  onNavigate: (mode: MainNavMode, zoneId?: string) => void;
}

export const CommandCenterPage: React.FC<CommandCenterPageProps> = ({
  event,
  zones,
  roads,
  infrastructure,
  rescueTeams,
  selectedZone,
  onSelectZone,
  onNavigate
}) => {
  const { scenarioTime, setScenarioTime, currentTimelineStepData, setPendingSimulationParams } = useDemo();
  
  // AI Quick Query State
  const [queryInput, setQueryInput] = useState<string>('');
  const [aiThinking, setAiThinking] = useState<boolean>(false);
  const [aiResponse, setAiResponse] = useState<OrchestratorStructuredResponse | null>(null);
  const [activeAiTab, setActiveAiTab] = useState<'REC' | 'FACTS' | 'RAG' | 'UNCERTAINTY'>('REC');

  // Default to Zone 7 if not explicitly set
  const activeZone = selectedZone || zones.find((z) => z.id === 'zone-7') || zones[0];

  const handleSimulateShortcut = () => {
    setPendingSimulationParams({
      zoneId: 'zone-7',
      scenarioName: 'Evacuate Zone 7 + Deploy Delta-2',
      interventions: ['evacuate_zone_7', 'deploy_team_r2'],
      timeHorizon: 60
    });
    onNavigate('SIMULATE', 'zone-7');
  };

  const handleAiQuery = async (queryText: string) => {
    if (!queryText.trim()) return;
    try {
      setAiThinking(true);
      const res = await api.orchestratorChat(
        queryText,
        'command-center-session',
        activeZone?.id || 'zone-7',
        'COMMAND'
      );
      setAiResponse(res);
    } catch (err) {
      console.error('Failed to query AI:', err);
    } finally {
      setAiThinking(false);
    }
  };

  const quickPrompts = [
    "What's happening right now?",
    "What happens next?",
    "Why is Zone 7 critical?",
    "Which team should respond?",
    "What if we do nothing?",
    "Generate command briefing"
  ];

  return (
    <div className="w-full h-full bg-[#060a12] text-slate-200 overflow-y-auto p-4 sm:p-5 font-mono select-none space-y-5">
      
      {/* Top Banner: Command Status & Time Horizon Switcher */}
      <div className="bg-gradient-to-r from-slate-900/95 via-cyan-950/40 to-slate-900/95 border border-cyan-500/30 rounded-2xl p-4 shadow-xl flex flex-wrap items-center justify-between gap-4">
        
        {/* Left: Title & Status */}
        <div className="space-y-1">
          <div className="flex items-center space-x-2.5">
            <h1 className="text-lg sm:text-xl font-black text-white tracking-wider flex items-center space-x-2">
              <span className="text-cyan-400">AEGIS</span>
              <span>COMMAND CENTER</span>
            </h1>
            <span className="flex items-center space-x-1.5 px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[10px] font-black">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>SYSTEM OPERATIONAL</span>
            </span>
          </div>
          <p className="text-xs text-slate-400 font-sans">
            Predictive Disaster Command Intelligence • Operational Horizon Overview
          </p>
        </div>

        {/* Center: Top Timeline Horizon Switcher */}
        <div className="flex items-center bg-slate-950/90 rounded-xl border border-slate-800 p-1 space-x-1">
          {[
            { id: 'T+0', label: 'CURRENT', sub: 'T+0m' },
            { id: 'T+60', label: 'NEXT 60 MIN', sub: 'T+60m' },
            { id: 'T+180', label: 'NEXT 3 HOURS', sub: 'T+180m' }
          ].map((h) => {
            const isActive = scenarioTime === h.id;
            return (
              <button
                key={h.id}
                onClick={() => setScenarioTime(h.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex flex-col items-center ${
                  isActive
                    ? 'bg-cyan-500 text-black shadow-[0_0_15px_rgba(0,240,255,0.4)]'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <span>{h.label}</span>
                <span className={`text-[9px] ${isActive ? 'text-slate-900 font-black' : 'text-slate-500'}`}>
                  {h.sub}
                </span>
              </button>
            );
          })}
        </div>

        {/* Right: Key Decision Metrics */}
        <div className="flex items-center space-x-3 text-xs">
          <div className="bg-slate-950/80 px-3 py-2 rounded-xl border border-slate-800 text-right">
            <span className="text-[10px] text-slate-500 block">TIME TO CRITICAL EVENT</span>
            <span className="text-base font-black text-amber-400">
              {currentTimelineStepData?.zone7_isolation_minutes ? `${currentTimelineStepData.zone7_isolation_minutes} MIN` : 'IMMINENT'}
            </span>
          </div>
          <div className="bg-slate-950/80 px-3 py-2 rounded-xl border border-slate-800 text-right">
            <span className="text-[10px] text-slate-500 block">CASCADING RISK</span>
            <span className="text-base font-black text-red-400">87/100</span>
          </div>
        </div>

      </div>

      {/* Priority 4: Realistic Live-Data Simulator Widget */}
      <LiveFeedPanel onNavigate={onNavigate} />

      {/* Priority 9: One Unified Intelligence Pipeline View */}
      <IntelligencePipeline onNavigate={onNavigate} selectedZoneId={activeZone?.id} />

      {/* Main Grid: GIS Map (Left) + AI Priority Alert (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">

        
        {/* Left: GIS Map Panel (7 cols) */}
        <div className="lg:col-span-7 hud-card p-4 rounded-2xl border border-slate-800/90 flex flex-col space-y-3 bg-[#080d18]/90">
          
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs">
              <Layers className="w-4 h-4 text-cyan-400" />
              <span className="tracking-wider">LIVE TACTICAL GIS MAP</span>
            </div>
            <div className="flex items-center space-x-2 text-[10px] text-slate-400">
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-red-500"></span>
                <span>Critical (&gt;80)</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                <span>Severe</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                <span>Accessible</span>
              </span>
            </div>
          </div>

          {/* Interactive Map View */}
          <div className="h-[360px] sm:h-[400px] w-full rounded-xl overflow-hidden border border-slate-800/80 relative">
            <TacticalMap
              zones={zones}
              roads={roads}
              infrastructure={infrastructure}
              teams={rescueTeams}
              selectedZoneId={activeZone?.id}
              onSelectZone={onSelectZone}
            />
          </div>


          {/* Quick Zone Selector Strip */}
          <div className="flex items-center space-x-1.5 overflow-x-auto pt-1 pb-1 scrollbar-thin">
            <span className="text-[10px] text-slate-500 font-bold shrink-0 mr-1">SECTOR:</span>
            {zones.map((z) => {
              const isSelected = activeZone?.id === z.id;
              const isCritical = z.primary_risk_score >= 80;
              return (
                <button
                  key={z.id}
                  onClick={() => onSelectZone(z)}
                  className={`px-2.5 py-1 rounded-lg text-[10px] font-bold shrink-0 border transition-all flex items-center space-x-1.5 ${
                    isSelected
                      ? 'bg-cyan-500 text-black border-cyan-400 shadow-[0_0_10px_rgba(0,240,255,0.4)]'
                      : isCritical
                      ? 'bg-red-950/40 text-red-300 border-red-500/40 hover:border-red-400'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <span>{z.name.split('—')[0].trim()}</span>
                  <span className={`text-[9px] font-black ${isSelected ? 'text-slate-900' : isCritical ? 'text-red-400' : 'text-slate-500'}`}>
                    {z.primary_risk_score}
                  </span>
                </button>
              );
            })}

          </div>

        </div>

        {/* Right: AI Priority Decision Card (5 cols) */}
        <div className="lg:col-span-5 hud-card p-5 rounded-2xl border border-red-500/50 flex flex-col justify-between space-y-4 bg-gradient-to-b from-red-950/20 via-slate-950/80 to-[#080d18]">
          
          <div className="flex justify-between items-center border-b border-red-500/30 pb-2">
            <div className="flex items-center space-x-2 text-red-400 font-black text-xs">
              <AlertTriangle className="w-4 h-4 text-red-400 animate-pulse" />
              <span>AI PRIORITY ALERT — CRITICAL ESCALATION</span>
            </div>
            <span className="px-2 py-0.5 rounded bg-red-900/60 text-red-200 text-[10px] font-bold">
              PRIORITY #1
            </span>
          </div>

          {/* Main Headline */}
          <div className="space-y-2">
            <h2 className="text-base font-black text-white leading-snug">
              ⚠ Zone 7 (River Bend) may become completely isolated in approximately 42 minutes.
            </h2>
            <p className="text-xs text-slate-300 font-sans leading-relaxed">
              Hydrological surge model forecasts river cresting +90cm over Corridor 14 bridge threshold.
            </p>
          </div>

          {/* Why Rationale Box */}
          <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 space-y-1.5">
            <span className="text-[10px] font-black text-amber-400 uppercase tracking-wider block">
              WHY IS THIS HAPPENING?
            </span>
            <ul className="space-y-1 text-xs font-sans text-slate-300">
              <li className="flex items-start space-x-2">
                <span className="text-red-400 font-bold">•</span>
                <span><strong>Flood Escalation:</strong> Water depth rising to 185cm (3.8m river crest).</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-red-400 font-bold">•</span>
                <span><strong>Road Cutoff:</strong> Corridor 14 access drops to 29% within 42 minutes.</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-red-400 font-bold">•</span>
                <span><strong>Medical Emergency:</strong> Memorial Hospital cutoff from regional trauma units.</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-red-400 font-bold">•</span>
                <span><strong>Silent Risk Anomaly:</strong> Telecom degradation at 72% risks civilian blackout.</span>
              </li>
            </ul>
          </div>

          {/* Recommended Mission Action */}
          <div className="p-3 bg-cyan-950/30 rounded-xl border border-cyan-500/40 flex items-center justify-between">
            <div>
              <span className="text-[9px] font-bold text-cyan-400 uppercase tracking-wider block">
                RECOMMENDED MISSION
              </span>
              <span className="text-sm font-black text-white">
                R2 (Swiftwater Alpha) &rarr; Zone 7
              </span>
              <span className="text-[10px] text-slate-400 block font-sans">
                Equipped with Rescue Boats + Paramedics (Score: 92/100)
              </span>
            </div>
            <button
              onClick={() => onNavigate('MISSIONS', 'zone-7')}
              className="px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black text-xs font-black shadow-[0_0_10px_rgba(0,240,255,0.3)] transition-all"
            >
              DEPLOY
            </button>
          </div>

          {/* Action Deep Links Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
            <button
              onClick={() => onNavigate('EVIDENCE', 'zone-7')}
              className="py-2 px-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-slate-700 hover:border-cyan-400 text-[10px] font-black flex items-center justify-center space-x-1 transition-all"
            >
              <FileCheck className="w-3 h-3" />
              <span>EVIDENCE</span>
            </button>

            <button
              onClick={handleSimulateShortcut}
              className="py-2 px-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-black text-[10px] flex items-center justify-center space-x-1 shadow-[0_0_10px_rgba(0,240,255,0.3)] transition-all"
            >
              <Sliders className="w-3 h-3" />
              <span>SIMULATE</span>
            </button>

            <button
              onClick={() => onNavigate('MISSIONS', 'zone-7')}
              className="py-2 px-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 hover:border-slate-500 text-[10px] font-black flex items-center justify-center space-x-1 transition-all"
            >
              <ShieldAlert className="w-3 h-3 text-amber-400" />
              <span>MISSION</span>
            </button>

            <button
              onClick={() => onNavigate('AI', 'zone-7')}
              className="py-2 px-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-purple-300 border border-purple-500/40 text-[10px] font-black flex items-center justify-center space-x-1 transition-all"
            >
              <Sparkles className="w-3 h-3 text-purple-400" />
              <span>ASK AI</span>
            </button>
          </div>

        </div>

      </div>

      {/* Bottom Intelligence Grid: Silent Risk (Left) + Multi-Mission Summary (Mid) + System Confidence (Right) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        {/* Card 1: Silent Crisis Alert */}
        <div className="hud-card p-4 rounded-xl border border-amber-500/40 bg-amber-950/10 flex flex-col justify-between space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-[10px] font-black text-amber-400 tracking-wider uppercase flex items-center space-x-1.5">
              <Radio className="w-3.5 h-3.5" />
              <span>SILENT CRISIS DETECTED</span>
            </span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-900/60 text-amber-200 font-bold">
              ZONE 4
            </span>
          </div>
          <p className="text-[11px] font-sans text-slate-300 leading-snug">
            <strong className="text-white">0 civilian SOS reports</strong> despite 145cm inundation and 2,300 exposed population due to cellular tower blackout.
          </p>
          <div className="text-[10px] text-amber-300/90 italic font-sans">
            "Zero reports do not mean zero victims."
          </div>
          <button
            onClick={() => onNavigate('EVIDENCE', 'zone-4')}
            className="w-full py-1.5 rounded bg-slate-900 hover:bg-slate-800 text-amber-300 border border-amber-500/40 text-[10px] font-bold flex items-center justify-center space-x-1 transition-all"
          >
            <span>INSPECT SILENT RISK SECTOR</span>
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        {/* Card 2: Mission Fleet Summary */}
        <div className="hud-card p-4 rounded-xl border border-slate-800 flex flex-col justify-between space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-[10px] font-black text-slate-400 tracking-wider uppercase flex items-center space-x-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>OPTIMIZED FLEET READINESS</span>
            </span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-500/40 font-bold">
              3 TEAMS ACTIVE
            </span>
          </div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Primary Dispatch:</span>
              <span className="text-cyan-300 font-bold">R2 &rarr; Zone 7 (ETA: 14m)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Recon Dispatch:</span>
              <span className="text-white font-bold">R1 &rarr; Zone 4 (ETA: 8m)</span>
            </div>
          </div>
          <button
            onClick={() => onNavigate('MISSIONS', 'zone-7')}
            className="w-full py-1.5 rounded bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 text-[10px] font-bold flex items-center justify-center space-x-1 transition-all"
          >
            <span>VIEW MULTI-MISSION PLAN</span>
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        {/* Card 3: Global System Confidence Breakdown */}
        <div className="hud-card p-4 rounded-xl border border-slate-800 flex flex-col justify-between space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-[10px] font-black text-slate-400 tracking-wider uppercase flex items-center space-x-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-cyan-400" />
              <span>SYSTEM CONFIDENCE TRACE</span>
            </span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/40 font-bold">
              HIGH CONFIDENCE
            </span>
          </div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Prediction Confidence:</span>
              <span className="text-emerald-400 font-bold">81% (Calibrated)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Evidence Trust Index:</span>
              <span className="text-emerald-400 font-bold">91% (14 Claims)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Simulation Stability:</span>
              <span className="text-cyan-300 font-bold">78% (Monte Carlo)</span>
            </div>
          </div>
          <button
            onClick={() => onNavigate('ADAPTIVE')}
            className="w-full py-1.5 rounded bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-slate-700 text-[10px] font-bold flex items-center justify-center space-x-1 transition-all"
          >
            <span>VIEW ADAPTIVE LEARNING LOOP</span>
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>

      </div>

      {/* Compact ASK AEGIS Command Bar */}
      <div className="hud-card p-4 rounded-2xl border border-purple-500/40 bg-gradient-to-r from-purple-950/20 via-slate-950/90 to-slate-950/90 space-y-3 shadow-xl">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2 text-purple-300 font-bold text-xs">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span>ASK AEGIS — DISASTER INTELLIGENCE ORCHESTRATOR</span>
          </div>
          <button
            onClick={() => onNavigate('AI')}
            className="text-[10px] text-purple-400 hover:text-purple-300 flex items-center space-x-1"
          >
            <span>EXPAND FULL AI WORKSPACE</span>
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        {/* Prompt Pills */}
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 scrollbar-thin">
          {quickPrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleAiQuery(p)}
              className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-purple-950/60 text-slate-300 hover:text-purple-200 border border-slate-800 hover:border-purple-500/50 text-[10px] font-bold shrink-0 transition-all"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAiQuery(queryInput);
            setQueryInput('');
          }}
          className="flex items-center space-x-2"
        >
          <input
            type="text"
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
            placeholder="Query AEGIS... (e.g. What is the cascading risk if Substation #2 fails?)"
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-400 font-mono"
          />
          <button
            type="submit"
            disabled={aiThinking}
            className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-black text-xs shadow-[0_0_15px_rgba(168,85,247,0.4)] disabled:opacity-40 flex items-center space-x-1.5 transition-all"
          >
            <span>{aiThinking ? 'ANALYZING...' : 'QUERY'}</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>

        {/* Instant Grounded AI Response Preview */}
        {aiResponse && (
          <div className="p-4 bg-slate-950/90 rounded-2xl border border-purple-500/50 text-xs space-y-3 animate-in fade-in shadow-xl">
            
            {/* Header: Provenance & Tabs */}
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-purple-500/30 pb-2.5">
              <div className="flex items-center space-x-2">
                <span className="font-black text-purple-300 flex items-center space-x-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                  <span>GROUNDED AI REASONING OUTPUT</span>
                </span>
                <DataSourceBadge sourceType="AI-INFERRED" size="sm" />
              </div>

              {/* 4 Grounded Section Switcher Tabs */}
              <div className="flex items-center space-x-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800 text-[10px]">
                <button
                  onClick={() => setActiveAiTab('REC')}
                  className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                    activeAiTab === 'REC'
                      ? 'bg-purple-600 text-white shadow-[0_0_10px_rgba(168,85,247,0.4)]'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  RECOMMENDATION
                </button>
                <button
                  onClick={() => setActiveAiTab('FACTS')}
                  className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                    activeAiTab === 'FACTS'
                      ? 'bg-cyan-500 text-black shadow-[0_0_10px_rgba(6,182,212,0.4)]'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  LIVE FACTS
                </button>
                <button
                  onClick={() => setActiveAiTab('RAG')}
                  className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                    activeAiTab === 'RAG'
                      ? 'bg-indigo-600 text-white shadow-[0_0_10px_rgba(99,102,241,0.4)]'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  RETRIEVED SOPS
                </button>
                <button
                  onClick={() => setActiveAiTab('UNCERTAINTY')}
                  className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                    activeAiTab === 'UNCERTAINTY'
                      ? 'bg-amber-500 text-black shadow-[0_0_10px_rgba(245,158,11,0.4)]'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  UNCERTAINTIES
                </button>
              </div>

              <ConfidenceBadge confidencePercent={aiResponse.confidence_score} size="sm" />
            </div>

            {/* TAB 1: AI RECOMMENDATION */}
            {activeAiTab === 'REC' && (
              <div className="space-y-2">
                <p className="text-slate-100 font-sans text-xs sm:text-sm leading-relaxed">
                  {aiResponse.direct_answer || aiResponse.answer}
                </p>
                {aiResponse.why_rationale && aiResponse.why_rationale.length > 0 && (
                  <div className="p-2.5 bg-slate-900/80 rounded-xl border border-slate-800 space-y-1">
                    <span className="text-[10px] font-bold text-amber-400 uppercase block">WHY THIS ACTION?</span>
                    <ul className="space-y-1 text-[11px] font-sans text-slate-300">
                      {aiResponse.why_rationale.map((r, i) => (
                        <li key={i} className="flex items-start space-x-1.5">
                          <span className="text-purple-400 font-bold">•</span>
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* TAB 2: LIVE OPERATIONAL FACTS */}
            {activeAiTab === 'FACTS' && (
              <div className="space-y-2">
                <div className="flex justify-between items-center text-[10px] text-slate-400">
                  <span className="font-bold text-cyan-400">VERIFIED OPERATIONAL TELEMETRY FACTS</span>
                  <DataSourceBadge sourceType="SENSOR" size="sm" />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {(aiResponse.live_facts && aiResponse.live_facts.length > 0 ? aiResponse.live_facts : aiResponse.facts).map((f, i) => (
                    <div key={i} className="p-2.5 rounded-xl bg-cyan-950/20 border border-cyan-500/30 text-slate-200 text-[11px] flex items-start space-x-2">
                      <span className="text-cyan-400 font-bold font-mono">0{i + 1}.</span>
                      <span className="font-sans">{f}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 3: RETRIEVED EMERGENCY SOPS (RAG) */}
            {activeAiTab === 'RAG' && (
              <div className="space-y-2">
                <div className="flex justify-between items-center text-[10px] text-slate-400">
                  <span className="font-bold text-indigo-400">EMERGENCY GUIDELINES & DOCTRINE RETRIEVED</span>
                  <DataSourceBadge sourceType="RAG" size="sm" />
                </div>
                <div className="space-y-2">
                  {(aiResponse.retrieved_guidance || [
                    "[SOP-FL-001] Urban Riverine Flood: Proactive evacuation mandatory before arterial routes submerge below 30cm passability.",
                    "[SOP-RES-005] Swiftwater USAR: Heavy Evacuation Units with boat capability prioritized for stranded clusters > 10 victims."
                  ]).map((g, i) => (
                    <div key={i} className="p-2.5 rounded-xl bg-indigo-950/20 border border-indigo-500/30 text-slate-200 text-[11px] font-sans flex items-start space-x-2">
                      <BookOpen className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                      <span>{g}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 4: UNCERTAINTIES & RISK MODEL */}
            {activeAiTab === 'UNCERTAINTY' && (
              <div className="space-y-2">
                <div className="flex justify-between items-center text-[10px] text-slate-400">
                  <span className="font-bold text-amber-400">MODEL UNCERTAINTIES & SENSOR LIMITATIONS</span>
                  <ConfidenceBadge confidencePercent={aiResponse.confidence_score} size="sm" />
                </div>
                <div className="space-y-1.5">
                  {(aiResponse.uncertainties || [
                    "Corridor 14 road bridge structural integrity unconfirmed by physical inspection",
                    "Rainfall runoff velocity may accelerate isolation timing by 8-12 minutes"
                  ]).map((u, i) => (
                    <div key={i} className="p-2 rounded-xl bg-amber-950/20 border border-amber-500/30 text-amber-200 text-[11px] font-sans flex items-start space-x-2">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                      <span>{u}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        )}


      </div>

    </div>
  );
};
