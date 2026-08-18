import React, { useState, useEffect } from 'react';
import { 
  Zone, RoadSegment, Infrastructure, RescueTeam, MainNavMode,
  PredictionResponse, TopPredictionItem, ZonePrediction
} from '../types';
import { TacticalMap } from '../components/map/TacticalMap';
import { CascadeModal } from '../components/cascading/CascadeModal';
import { EvidenceChain } from '../components/evidence/EvidenceChain';
import { 
  TrendingUp, 
  Clock, 
  AlertTriangle, 
  Sliders, 
  ShieldAlert, 
  Radio, 
  Zap, 
  CheckCircle2, 
  ArrowRight, 
  Users, 
  Droplets, 
  Building, 
  Activity, 
  Layers, 
  ChevronRight, 
  Info, 
  Calendar, 
  Compass, 
  ArrowUpRight, 
  Sparkles,
  FileCheck
} from 'lucide-react';

interface PredictPageProps {
  zones: Zone[];
  roads: RoadSegment[];
  infrastructure: Infrastructure[];
  teams: RescueTeam[];
  selectedZone: Zone | null;
  onSelectZone: (zone: Zone) => void;
  onNavigate: (mode: MainNavMode, zoneId?: string) => void;
}

export const PredictPage: React.FC<PredictPageProps> = ({
  zones,
  roads,
  infrastructure,
  teams,
  selectedZone,
  onSelectZone,
  onNavigate
}) => {
  // Selected Time Horizon: 0 (NOW), 30 (+30m), 60 (+60m), 180 (+3h)
  const [horizonMinutes, setHorizonMinutes] = useState<number>(60);
  const [showCascadeModal, setShowCascadeModal] = useState<boolean>(false);
  const [inspectingEvidenceDecision, setInspectingEvidenceDecision] = useState<string | null>(null);
  
  // Default to Zone 7 (the primary escalating zone) or active selection
  const activeZone = selectedZone || zones.find((z) => z.id === 'zone-7') || zones[0];



  // Dynamic zone predictive projection for selected zone
  const isZone7 = activeZone?.id === 'zone-7';
  const isZone4 = activeZone?.id === 'zone-4';

  const riskNow = isZone7 ? 82 : (isZone4 ? 92 : activeZone.primary_risk_score);
  const risk30 = isZone7 ? 87 : (isZone4 ? 95 : Math.min(96, riskNow + 6));
  const risk60 = isZone7 ? 94 : (isZone4 ? 98 : Math.min(99, riskNow + 12));
  const risk3h = isZone7 ? 97 : (isZone4 ? 99 : Math.min(99, riskNow + 16));

  const popNow = isZone7 ? 8240 : (isZone4 ? 9300 : Math.round(activeZone.population * 0.65));
  const pop30 = isZone7 ? 9760 : (isZone4 ? 9300 : Math.round(activeZone.population * 0.75));
  const pop60 = isZone7 ? 11800 : (isZone4 ? 9300 : Math.round(activeZone.population * 0.85));
  const pop3h = isZone7 ? 15200 : (isZone4 ? 9300 : Math.round(activeZone.population * 0.95));

  const roadNow = isZone7 ? 61 : (isZone4 ? 12 : activeZone.road_accessibility_percent);
  const road30 = isZone7 ? 48 : (isZone4 ? 5 : Math.max(10, Math.round(roadNow * 0.85)));
  const road60 = isZone7 ? 34 : (isZone4 ? 0 : Math.max(5, Math.round(roadNow * 0.70)));
  const road3h = isZone7 ? 18 : (isZone4 ? 0 : Math.max(0, Math.round(roadNow * 0.45)));

  const hospNow = isZone7 ? 61 : (isZone4 ? 15 : activeZone.hospital_accessibility_percent);
  const hosp30 = isZone7 ? 48 : (isZone4 ? 8 : Math.max(10, Math.round(hospNow * 0.85)));
  const hosp60 = isZone7 ? 34 : (isZone4 ? 0 : Math.max(5, Math.round(hospNow * 0.70)));
  const hosp3h = isZone7 ? 18 : (isZone4 ? 0 : Math.max(0, Math.round(hospNow * 0.45)));

  const driversList = isZone7 ? [
    "River level rising rapidly (+0.4m/hr crest velocity)",
    "Heavy precipitation continues (74 mm/h sustained)",
    "Corridor 14 bridge overtopping imminent at Pier 3",
    "Substation Delta-2 flooding disabling Basin Pump #1",
    "Secondary drainage backwater surge across lowland basin"
  ] : (isZone4 ? [
    "Extreme flood depth (145 cm) across low elevation marshland (8.1m MSL)",
    "Telecom Tower Delta-4 completely destroyed by floodwaters",
    "Road 04 completely impassable (0% passability)",
    "0 SOS calls received indicates total communications blackout"
  ] : [
    `Sustained heavy precipitation (${activeZone.rainfall_rate_mmh} mm/h)`,
    `Local water table saturation (${activeZone.current_flood_depth_cm} cm flood depth)`,
    `Road accessibility degrading to ${road60}% over next 60 minutes`,
    "Secondary runoff from upstream tributaries"
  ]);

  const escalationMins = isZone7 ? 42 : (isZone4 ? 25 : (activeZone.escalation_time_minutes || 65));
  const confidenceScore = isZone7 ? 87 : (isZone4 ? 91 : 84);

  // Top Operational Priority Predictions
  const topPredictions: TopPredictionItem[] = [
    {
      id: "pred-01",
      title: "Zone 7 Imminent Isolation",
      target_entity: "Zone 7 (River Bend)",
      category: "ZONE",
      predicted_event: "Corridor 14 bridge overtopping cuts off primary access",
      eta_minutes: 42,
      confidence_percent: 87,
      priority_score: 96,
      severity_level: "CRITICAL",
      action_label: "PREEMPTIVE EVACUATION"
    },
    {
      id: "pred-02",
      title: "Hospital A Access Drop",
      target_entity: "Hospital A (Riverbank)",
      category: "HOSPITAL",
      predicted_event: "Corridor accessibility drops from 61% to 34%",
      eta_minutes: 58,
      confidence_percent: 81,
      priority_score: 91,
      severity_level: "CRITICAL",
      action_label: "DEPLOY MOBILE GENERATOR"
    },
    {
      id: "pred-03",
      title: "Road 14 Bridge Blockage",
      target_entity: "Road 14 (Central River Bridge)",
      category: "ROAD",
      predicted_event: "River crest exceeding 8.0m will submerge approach ramps",
      eta_minutes: 35,
      confidence_percent: 84,
      priority_score: 87,
      severity_level: "HIGH",
      action_label: "REROUTE TRAFFIC"
    },
    {
      id: "pred-04",
      title: "Substation Delta-2 Trip",
      target_entity: "Substation Delta-2",
      category: "POWER",
      predicted_event: "Water breaching 90cm defense bund",
      eta_minutes: 50,
      confidence_percent: 88,
      priority_score: 84,
      severity_level: "HIGH",
      action_label: "DEPLOY BARRIER"
    }
  ];

  return (
    <div className="w-full h-full flex flex-col space-y-3 p-4 overflow-y-auto font-mono text-xs select-none">
      {/* 1. Header & Systematic Flow Guide */}
      <div className="hud-card p-3 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-2 border-l-4 border-l-cyan-400">
        <div>
          <div className="flex items-center space-x-2">
            <span className="p-1 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/40">
              <TrendingUp className="w-4 h-4" />
            </span>
            <h1 className="text-sm font-black text-white tracking-wider">
              PREDICTIVE DISASTER INTELLIGENCE CENTER
            </h1>
            <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/40 text-[9px] font-bold">
              MODEL ESTIMATE
            </span>
          </div>
          <div className="text-[10px] text-slate-400 mt-1 flex items-center space-x-2">
            <span className="text-slate-300 font-bold">CORE QUERY LOOP:</span>
            <span>WHAT IS HAPPENING?</span>
            <span className="text-cyan-400">➔</span>
            <span className="text-cyan-300 font-bold">WHAT WILL HAPPEN NEXT?</span>
            <span className="text-cyan-400">➔</span>
            <span>WHY?</span>
            <span className="text-cyan-400">➔</span>
            <span>WHAT SHOULD WE WATCH?</span>
          </div>
        </div>

        {/* Time Horizon Timeline Selector (Section 10) */}
        <div className="flex items-center space-x-1.5 bg-slate-900/90 p-1.5 rounded-lg border border-slate-700">
          <span className="text-[10px] text-slate-400 font-bold px-1.5 uppercase flex items-center space-x-1">
            <Clock className="w-3 h-3 text-cyan-400" />
            <span>HORIZON:</span>
          </span>
          {[
            { label: 'NOW', minutes: 0 },
            { label: '+30 MIN', minutes: 30 },
            { label: '+60 MIN', minutes: 60 },
            { label: '+3 HOURS', minutes: 180 }
          ].map((item) => (
            <button
              key={item.minutes}
              onClick={() => setHorizonMinutes(item.minutes)}
              className={`px-3 py-1 rounded text-[10px] font-black transition-all ${
                horizonMinutes === item.minutes
                  ? 'bg-cyan-500 text-black shadow-[0_0_12px_rgba(0,240,255,0.5)]'
                  : 'bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* 2. Top Predictions Operational Priority Bar (Section 9 & 17) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
        {topPredictions.map((pred) => (
          <div
            key={pred.id}
            onClick={() => {
              if (pred.id === 'pred-01') {
                const z7 = zones.find((z) => z.id === 'zone-7');
                if (z7) onSelectZone(z7);
              }
            }}
            className={`p-2.5 rounded-lg border cursor-pointer transition-all hover:scale-[1.01] ${
              pred.priority_score >= 90
                ? 'bg-red-950/30 border-red-500/50 hover:border-red-400 shadow-[0_0_15px_rgba(239,68,68,0.15)]'
                : 'bg-slate-900/80 border-slate-800 hover:border-cyan-500/50'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className={`px-1.5 py-0.2 rounded text-[9px] font-black border ${
                pred.priority_score >= 90
                  ? 'bg-red-950 text-red-300 border-red-500/60 animate-pulse'
                  : 'bg-amber-950 text-amber-300 border-amber-500/60'
              }`}>
                PRIORITY {pred.priority_score}
              </span>
              <span className="text-[10px] text-cyan-400 font-bold">
                ETA: ~{pred.eta_minutes} MIN
              </span>
            </div>

            <div className="mt-1.5">
              <div className="font-extrabold text-white text-xs truncate">{pred.title}</div>
              <div className="text-[10px] text-slate-400 truncate mt-0.5">{pred.predicted_event}</div>
            </div>

            <div className="mt-2 pt-1.5 border-t border-slate-800/80 flex items-center justify-between text-[9px]">
              <span className="text-slate-400">Confidence: <span className="text-emerald-400 font-bold">{pred.confidence_percent}%</span></span>
              <span className="text-cyan-300 font-bold flex items-center">
                <span>{pred.action_label}</span>
                <ChevronRight className="w-2.5 h-2.5 ml-0.5" />
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* 3. Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 min-h-[520px]">
        {/* Left Column: Escalation Clock & Explanations (4 cols) */}
        <div className="lg:col-span-4 flex flex-col space-y-3">
          {/* Escalation Clock Component (Section 14) */}
          <div className="hud-card-active p-4 rounded-lg border-2 border-red-500/60 shadow-[0_0_25px_rgba(239,68,68,0.2)]">
            <div className="flex items-center justify-between border-b border-red-500/30 pb-2">
              <div className="flex items-center space-x-1.5 text-red-400 font-bold">
                <AlertTriangle className="w-4 h-4 animate-ping" />
                <span>CRITICAL ESCALATION CLOCK</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-red-950 text-red-300 border border-red-500/60 text-[9px] font-black">
                THRESHOLD: 90 / 100
              </span>
            </div>

            <div className="mt-3 text-center">
              <div className="text-xs text-slate-400 uppercase font-bold">{activeZone.name}</div>
              <div className="text-3xl font-black text-red-400 tracking-wider mt-1 flex items-center justify-center space-x-2">
                <span>~{escalationMins} MIN</span>
              </div>
              <div className="text-[10px] text-amber-300 mt-0.5 font-bold">
                Expected Trajectory: {riskNow} ➔ {risk60} (Crossing 90 Critical in ~{escalationMins}m)
              </div>
            </div>

            {/* Visual Progress Countdown Meter */}
            <div className="mt-3 space-y-1">
              <div className="w-full bg-slate-950 rounded-full h-3 border border-slate-800 overflow-hidden p-0.5">
                <div 
                  className="h-full rounded-full bg-gradient-to-r from-amber-500 via-red-500 to-red-600 animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.6)]" 
                  style={{ width: `${Math.min(100, (60 - escalationMins) / 60 * 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-[9px] text-slate-500">
                <span>T+0m (Now: {riskNow})</span>
                <span>T+30m: {risk30}</span>
                <span>T+60m: {risk60}</span>
              </div>
            </div>

            {/* Quick Strategic Intervention Action */}
            <div className="mt-4 pt-3 border-t border-slate-800 flex items-center space-x-2">
              <button
                onClick={() => onNavigate('SIMULATE', activeZone.id)}
                className="flex-1 py-2 rounded bg-cyan-500 hover:bg-cyan-400 text-black font-black text-xs flex items-center justify-center space-x-1.5 shadow-[0_0_15px_rgba(0,240,255,0.4)]"
              >
                <Sliders className="w-3.5 h-3.5" />
                <span>SIMULATE INTERVENTIONS</span>
              </button>
            </div>
          </div>

          {/* "Why Will This Happen?" (Section 13) */}
          <div className="hud-card p-4 rounded-lg flex-1 flex flex-col justify-between border-l-4 border-l-cyan-400">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <div className="text-cyan-400 font-bold flex items-center space-x-1.5">
                  <Sparkles className="w-4 h-4 text-cyan-400" />
                  <span>WHY IS {activeZone.code} EXPECTED TO ESCALATE?</span>
                </div>
                <span className="text-[10px] text-emerald-400 font-bold">
                  CONFIDENCE: {confidenceScore}%
                </span>
              </div>

              {/* Structured Model Drivers Checklist */}
              <div className="mt-3 space-y-2">
                {driversList.map((driver, idx) => (
                  <div key={idx} className="flex items-start space-x-2 bg-slate-900/70 p-2 rounded border border-slate-800">
                    <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                    <span className="text-slate-200 text-[11px] font-sans leading-tight">{driver}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-3 pt-2 border-t border-slate-800 flex items-center justify-between">
              <button
                onClick={() => setInspectingEvidenceDecision(isZone4 ? 'decision-zone-4-silent' : 'decision-zone-7-escalation')}
                className="w-full py-1.5 rounded bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/50 font-black text-[10px] flex items-center justify-center space-x-1.5 shadow-[0_0_10px_rgba(6,182,212,0.2)] transition-all"
              >
                <FileCheck className="w-3.5 h-3.5" />
                <span>WHY? — VIEW FULL EVIDENCE CHAIN</span>
              </button>
            </div>
          </div>
        </div>


        {/* Center Column: Predictive GIS Map (4.5 cols) */}
        <div className="lg:col-span-5 flex flex-col">
          <div className="mb-2 flex items-center justify-between bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800 text-[10px]">
            <div className="flex items-center space-x-2">
              <span className="text-slate-400 uppercase font-bold">Active Horizon Layer:</span>
              <span className="text-cyan-300 font-black">
                {horizonMinutes === 0 ? 'CURRENT REAL-TIME (T+0)' : `PROJECTED T+${horizonMinutes} MINUTES`}
              </span>
            </div>
            <span className="text-amber-400 font-bold">
              {horizonMinutes > 0 ? `Zone 7 Projected Risk: ${horizonMinutes >= 180 ? risk3h : (horizonMinutes >= 60 ? risk60 : risk30)}` : `Zone 7 Current: ${riskNow}`}
            </span>
          </div>

          <TacticalMap
            zones={zones}
            roads={roads}
            infrastructure={infrastructure}
            teams={teams}
            selectedZoneId={activeZone?.id}
            onSelectZone={onSelectZone}
            predictionHorizonMinutes={horizonMinutes}
          />
        </div>

        {/* Right Column: Future State Comparison & Infrastructure Impact (3.5 cols) */}
        <div className="lg:col-span-3 flex flex-col space-y-3">
          {/* Future State Comparison Matrix (Section 12) */}
          <div className="hud-card p-4 rounded-lg border border-slate-800 space-y-2.5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="font-extrabold text-white text-xs">
                {activeZone.code} — FUTURE STATE PROJECTION
              </span>
              <span className="text-[10px] text-cyan-400 font-bold">
                {horizonMinutes === 0 ? 'T+0m' : `T+${horizonMinutes}m`}
              </span>
            </div>

            <div className="space-y-1.5 text-[11px]">
              <div className="grid grid-cols-4 text-[9px] text-slate-500 font-bold pb-1 border-b border-slate-800">
                <span>METRIC</span>
                <span className="text-center">NOW</span>
                <span className="text-center text-cyan-300">+{horizonMinutes || 60}m</span>
                <span className="text-right">TREND</span>
              </div>

              {/* Metric 1: Flood Risk */}
              <div className="grid grid-cols-4 items-center bg-slate-900/60 p-1.5 rounded border border-slate-800/80">
                <span className="text-slate-300 font-bold">Flood Risk</span>
                <span className="text-center font-mono text-slate-300">{riskNow}</span>
                <span className="text-center font-mono font-black text-red-400">{horizonMinutes >= 180 ? risk3h : (horizonMinutes >= 60 ? risk60 : risk30)}</span>
                <span className="text-right text-red-400 font-bold">↗ Escalating</span>
              </div>

              {/* Metric 2: Population Exposed */}
              <div className="grid grid-cols-4 items-center bg-slate-900/60 p-1.5 rounded border border-slate-800/80">
                <span className="text-slate-300 font-bold">Pop Risk</span>
                <span className="text-center font-mono text-slate-300">{popNow.toLocaleString()}</span>
                <span className="text-center font-mono font-black text-amber-300">{(horizonMinutes >= 180 ? pop3h : (horizonMinutes >= 60 ? pop60 : pop30)).toLocaleString()}</span>
                <span className="text-right text-amber-400 font-bold">↗ Expanding</span>
              </div>

              {/* Metric 3: Road Access */}
              <div className="grid grid-cols-4 items-center bg-slate-900/60 p-1.5 rounded border border-slate-800/80">
                <span className="text-slate-300 font-bold">Road Access</span>
                <span className="text-center font-mono text-emerald-400">{roadNow}%</span>
                <span className="text-center font-mono font-black text-red-400">{horizonMinutes >= 180 ? road3h : (horizonMinutes >= 60 ? road60 : road30)}%</span>
                <span className="text-right text-red-400 font-bold">↘ Blocked</span>
              </div>

              {/* Metric 4: Hospital Access */}
              <div className="grid grid-cols-4 items-center bg-slate-900/60 p-1.5 rounded border border-slate-800/80">
                <span className="text-slate-300 font-bold">Hosp Access</span>
                <span className="text-center font-mono text-cyan-300">{hospNow}%</span>
                <span className="text-center font-mono font-black text-red-400">{horizonMinutes >= 180 ? hosp3h : (horizonMinutes >= 60 ? hosp60 : hosp30)}%</span>
                <span className="text-right text-red-400 font-bold">↘ Cutoff</span>
              </div>
            </div>
          </div>

          {/* CASCADING CONSEQUENCES (Section 9 & 10) */}
          <div className="hud-card p-4 rounded-lg border-l-4 border-l-amber-500 space-y-2.5">
            <div className="flex items-center justify-between border-b border-amber-500/30 pb-2">
              <div className="flex items-center space-x-1.5 text-amber-400 font-bold">
                <Zap className="w-4 h-4" />
                <span>CASCADING CONSEQUENCES</span>
              </div>
              <span className="px-1.5 py-0.2 rounded bg-amber-950 text-amber-300 text-[9px] font-bold">
                SCORE: {isZone7 ? 87 : (isZone4 ? 94 : activeZone.cascading_risk_score)}
              </span>
            </div>

            <div className="text-[10px] text-slate-400 leading-tight">
              Directional Chain for <span className="text-white font-bold">{activeZone.code}</span>:
            </div>

            {/* Directional Step Chain */}
            <div className="space-y-1 text-[11px] pt-1">
              {[
                { label: 'Flood Risk', score: isZone7 ? 86 : activeZone.primary_risk_score, color: 'text-amber-400' },
                { label: 'Road Blockage', score: isZone7 ? 91 : Math.min(99, activeZone.primary_risk_score + 9), color: 'text-red-400' },
                { label: 'Hospital Access', score: isZone7 ? 81 : Math.min(99, activeZone.primary_risk_score + 4), color: 'text-red-400' },
                { label: 'Medical Response Delay', score: isZone7 ? 78 : Math.min(99, activeZone.primary_risk_score + 2), color: 'text-red-500' },
                { label: 'Victim Risk', score: isZone7 ? 73 : Math.max(50, activeZone.primary_risk_score - 4), color: 'text-rose-400' }
              ].map((step, idx, arr) => (
                <div key={idx} className="flex flex-col">
                  <div className="flex items-center justify-between bg-slate-900/80 px-2 py-1 rounded border border-slate-800">
                    <span className="font-bold text-slate-200 text-[10px]">{step.label}</span>
                    <span className={`font-mono font-black text-xs ${step.color}`}>{step.score}</span>
                  </div>
                  {idx < arr.length - 1 && (
                    <div className="flex justify-center text-slate-500 text-[10px] leading-none py-0.5">
                      <span>↓</span>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <button
              onClick={() => setShowCascadeModal(true)}
              className="mt-2 w-full py-1.5 rounded bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/50 font-bold text-[10px] flex items-center justify-center space-x-1.5 transition-all shadow-[0_0_10px_rgba(245,158,11,0.2)]"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>VIEW FULL CASCADE GRAPH</span>
            </button>
          </div>

          {/* Predicted Infrastructure Impact (Section 15) */}
          <div className="hud-card p-4 rounded-lg flex-1 flex flex-col justify-between border-l-4 border-l-amber-500">
            <div>
              <div className="flex items-center justify-between border-b border-amber-500/30 pb-2">
                <div className="flex items-center space-x-1.5 text-amber-400 font-bold">
                  <Building className="w-4 h-4" />
                  <span>PREDICTED INFRA IMPACT</span>
                </div>
                <span className="text-[9px] text-slate-400">3 ASSETS</span>
              </div>

              <div className="mt-3 space-y-2 text-[11px]">
                {/* Road 14 */}
                <div className="bg-slate-900/80 p-2 rounded border border-slate-800 space-y-0.5">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-white">ROAD 14 (Central Bridge)</span>
                    <span className="text-red-400 font-black text-[9px]">ETA: 35 MIN</span>
                  </div>
                  <div className="text-[10px] text-slate-400">Current: <span className="text-emerald-400 font-bold">OPEN</span> ➔ Predicted: <span className="text-red-400 font-bold">HIGH BLOCKAGE</span></div>
                </div>

                {/* Hospital A */}
                <div className="bg-slate-900/80 p-2 rounded border border-slate-800 space-y-0.5">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-white">HOSPITAL A (Riverbank)</span>
                    <span className="text-red-400 font-black text-[9px]">ETA: 58 MIN</span>
                  </div>
                  <div className="text-[10px] text-slate-400">Access: <span className="text-amber-400 font-bold">61%</span> ➔ Predicted: <span className="text-red-400 font-bold">34% (CRITICAL)</span></div>
                </div>

                {/* Substation Delta-2 */}
                <div className="bg-slate-900/80 p-2 rounded border border-slate-800 space-y-0.5">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-white">SUBSTATION DELTA-2</span>
                    <span className="text-amber-400 font-black text-[9px]">RISK: 72%</span>
                  </div>
                  <div className="text-[10px] text-slate-400">Defense: <span className="text-amber-400 font-bold">HIGH EXPOSURE</span> • Secondary Grid Trip</div>
                </div>
              </div>
            </div>

            {/* Population Trajectory Summary (Section 16) */}
            <div className="mt-3 pt-2 border-t border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-bold mb-1.5 flex justify-between">
                <span>TOTAL POPULATION EXPOSURE</span>
                <span className="text-cyan-400">MODEL ESTIMATE</span>
              </div>
              <div className="grid grid-cols-4 gap-1 text-center text-[10px]">
                <div className="bg-slate-950 p-1.5 rounded border border-slate-800">
                  <div className="text-slate-500">NOW</div>
                  <div className="font-bold text-white">8,240</div>
                </div>
                <div className="bg-slate-950 p-1.5 rounded border border-slate-800">
                  <div className="text-slate-500">+30m</div>
                  <div className="font-bold text-cyan-300">9,760</div>
                </div>
                <div className="bg-slate-950 p-1.5 rounded border border-slate-800">
                  <div className="text-slate-500">+60m</div>
                  <div className="font-bold text-amber-400">11,800</div>
                </div>
                <div className="bg-slate-950 p-1.5 rounded border border-slate-800">
                  <div className="text-slate-500">+3h</div>
                  <div className="font-bold text-red-400">15,200</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Deep Cascade Graph Modal */}
      {showCascadeModal && (
        <CascadeModal
          zoneId={activeZone.id}
          onClose={() => setShowCascadeModal(false)}
          onNavigate={onNavigate}
        />
      )}

      {/* Decision Evidence Traceability Modal */}
      {inspectingEvidenceDecision && (
        <EvidenceChain
          decisionId={inspectingEvidenceDecision}
          onClose={() => setInspectingEvidenceDecision(null)}
          onNavigate={onNavigate}
        />
      )}
    </div>
  );
};


