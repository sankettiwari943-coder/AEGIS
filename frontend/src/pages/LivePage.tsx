import React, { useState } from 'react';
import { Zone, RoadSegment, Infrastructure, RescueTeam, MainNavMode, SilentRiskAssessment, ZoneCascadingRisk } from '../types';
import { TacticalMap } from '../components/map/TacticalMap';
import { ZoneDetailModal } from '../components/command-center/ZoneDetailModal';
import { RescueTeamModal } from '../components/command-center/RescueTeamModal';
import { CascadeModal } from '../components/cascading/CascadeModal';
import { EvidenceChain } from '../components/evidence/EvidenceChain';
import { CVAnalysisPanel } from '../components/gis/CVAnalysisPanel';
import { DataSourceBadge } from '../components/common/DataSourceBadge';
import { ConfidenceBadge } from '../components/common/ConfidenceBadge';
import { 
  AlertTriangle, 
  Radio, 
  ArrowRight, 
  Layers, 
  ShieldAlert, 
  Activity, 
  Sliders, 
  CheckCircle2, 
  TrendingUp,
  Droplets,
  Zap,
  Users,
  Compass,
  FileCheck,
  Search,
  ChevronRight,
  Flame,
  ArrowDown,
  Camera,
  Eye
} from 'lucide-react';


interface LivePageProps {
  zones: Zone[];
  roads: RoadSegment[];
  infrastructure: Infrastructure[];
  teams: RescueTeam[];
  silentRisks: SilentRiskAssessment[];
  cascadingRisks: ZoneCascadingRisk[];
  selectedZone: Zone | null;
  onSelectZone: (zone: Zone) => void;
  onNavigate: (mode: MainNavMode, zoneId?: string) => void;
}

export const LivePage: React.FC<LivePageProps> = ({
  zones,
  roads,
  infrastructure,
  teams,
  silentRisks,
  cascadingRisks,
  selectedZone,
  onSelectZone,
  onNavigate
}) => {
  // Modal states for full deep inspection
  const [inspectingZone, setInspectingZone] = useState<Zone | null>(null);
  const [inspectingTeam, setInspectingTeam] = useState<RescueTeam | null>(null);
  const [inspectingCascadeZone, setInspectingCascadeZone] = useState<Zone | null>(null);
  const [inspectingEvidenceDecision, setInspectingEvidenceDecision] = useState<string | null>(null);


  // Default focus on Zone 7 (the primary escalating zone in demo) or selected zone
  const activeZone = selectedZone || zones.find((z) => z.id === 'zone-7') || zones[0];
  const activeCascading = cascadingRisks.find((c) => c.zone_id === activeZone?.id) || cascadingRisks[0];

  // CV Reconnaissance Panel toggle state
  const [showCVPanel, setShowCVPanel] = useState<boolean>(false);

  const handleZoneClick = (zone: Zone) => {
    onSelectZone(zone);
    setInspectingZone(zone);
  };

  const handleTeamClick = (team: RescueTeam) => {
    setInspectingTeam(team);
  };

  return (
    <div className="w-full h-full flex flex-col space-y-3 p-4 overflow-y-auto font-mono text-xs">
      {/* 1. Incident Overview Header (Section 3) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
        <div className="hud-card p-2.5 rounded-lg border-l-2 border-l-cyan-400">
          <div className="flex justify-between items-center text-[9px] text-slate-400 uppercase font-bold">
            <span>ACTIVE INCIDENT</span>
            <DataSourceBadge sourceType="LIVE" size="sm" />
          </div>
          <div className="text-xs font-black text-white truncate mt-0.5">URBAN FLOOD</div>
          <div className="text-[10px] text-cyan-400">River Basin District</div>
        </div>

        <div className="hud-card p-2.5 rounded-lg border-l-2 border-l-red-500">
          <div className="flex justify-between items-center text-[9px] text-slate-400 uppercase font-bold">
            <span>SEVERITY STATE</span>
            <DataSourceBadge sourceType="SENSOR" size="sm" />
          </div>
          <div className="text-xs font-black text-red-400 flex items-center space-x-1 mt-0.5">
            <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping" />
            <span>ESCALATING</span>
          </div>
          <div className="text-[10px] text-slate-400">Peak crest in ~2.4h</div>
        </div>

        <div className="hud-card p-2.5 rounded-lg border-l-2 border-l-blue-400">
          <div className="text-[9px] text-slate-400 uppercase font-bold">POPULATION AT RISK</div>
          <div className="text-xs font-black text-blue-300 mt-0.5">11,800 EXPOSED</div>
          <div className="text-[10px] text-slate-400">12 monitored sectors</div>
        </div>

        <div className="hud-card p-2.5 rounded-lg border-l-2 border-l-amber-500">
          <div className="text-[9px] text-slate-400 uppercase font-bold">CURRENT FLOOD RISK</div>
          <div className="text-xs font-black text-amber-400 mt-0.5">INDEX: 82 / 100</div>
          <div className="text-[10px] text-slate-400">Cascading Index: 87</div>
        </div>

        <div className="hud-card p-2.5 rounded-lg border-l-2 border-l-emerald-500">
          <div className="text-[9px] text-slate-400 uppercase font-bold">RESCUE ASSETS</div>
          <div className="text-xs font-black text-emerald-400 mt-0.5">4 ACTIVE / 6 STAGED</div>
          <div className="text-[10px] text-slate-400">Guardian-4 Ready</div>
        </div>

        <div className="hud-card p-2.5 rounded-lg border-l-2 border-l-red-600">
          <div className="text-[9px] text-slate-400 uppercase font-bold">NEXT ESCALATION</div>
          <div className="text-xs font-black text-red-300 mt-0.5">ZONE 7 (~42 MIN)</div>
          <div className="text-[10px] text-red-400/90 font-bold">Corridor 14 Cutoff</div>
        </div>
      </div>

      {/* CV Aerial Reconnaissance Banner & Toggle */}
      <div className="bg-gradient-to-r from-teal-950/40 via-slate-900/90 to-slate-900/90 border border-teal-500/40 rounded-xl p-3 flex flex-wrap items-center justify-between gap-3 shadow-md">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-lg bg-teal-500/20 text-teal-300 border border-teal-500/40">
            <Camera className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-black text-white text-xs tracking-wider">AERIAL DRONE & SATELLITE CV RECONNAISSANCE</span>
              <DataSourceBadge sourceType="DEMO CV" size="sm" />
            </div>
            <span className="text-[10px] text-slate-400 font-sans">
              Automated image segmentation for flood extent, submerged roads, and damaged structures.
            </span>
          </div>
        </div>

        <button
          onClick={() => setShowCVPanel(!showCVPanel)}
          className="px-3.5 py-1.5 rounded-lg bg-teal-500 hover:bg-teal-400 text-black font-black text-xs shadow-[0_0_12px_rgba(20,184,166,0.3)] flex items-center space-x-1.5 transition-all"
        >
          <Eye className="w-3.5 h-3.5" />
          <span>{showCVPanel ? 'HIDE CV RECON VIEWER' : 'OPEN CV RECON VIEWER'}</span>
        </button>
      </div>

      {/* Conditional CV Analysis Panel Display */}
      {showCVPanel && (
        <CVAnalysisPanel
          selectedZoneId={activeZone?.id}
          onClose={() => setShowCVPanel(false)}
        />
      )}

      {/* Main Command Center Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 min-h-[520px]">

        {/* Left Column: AI Immediate Alert & Zone Inspector (3.5 cols) */}
        <div className="lg:col-span-4 flex flex-col space-y-3">
          {/* 4. AI ALERT Panel (Section 4) */}
          <div className="hud-card-active p-4 rounded-lg flex flex-col justify-between border border-cyan-500/50 shadow-[0_0_20px_rgba(0,240,255,0.15)]">
            <div>
              <div className="flex items-center justify-between border-b border-cyan-500/30 pb-2">
                <div className="flex items-center space-x-2 text-cyan-400 font-bold">
                  <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                  <span>AI OPERATIONAL ALERT</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-red-950 text-red-300 border border-red-500/50 font-extrabold text-[10px]">
                  CRITICAL THREAT
                </span>
              </div>

              <div className="mt-3 space-y-2.5">
                <div>
                  <h3 className="text-sm font-black text-white leading-snug">
                    Zone 7 may become isolated in approximately 42 minutes.
                  </h3>
                  <div className="text-[10px] text-slate-400 mt-0.5">
                    Sector: <span className="text-cyan-300 font-bold">Zone 7 — River Bend Lowlands</span> • Confidence: <span className="text-emerald-400 font-bold">87%</span>
                  </div>
                </div>

                {/* Reason & Grounding */}
                <div className="bg-slate-900/90 p-2.5 rounded border border-slate-800 space-y-1.5 text-[11px]">
                  <div className="text-slate-300 font-sans leading-relaxed">
                    <span className="text-cyan-400 font-bold font-mono text-[10px] uppercase">Reason: </span>
                    River crest velocity (+0.4m/hr) will overtop Corridor 14 bridge abutment at Pier 3 while Substation Delta-2 flooding shuts down Basin Pump #1.
                  </div>
                  <div className="pt-1 border-t border-slate-800 text-slate-300 font-sans leading-relaxed">
                    <span className="text-emerald-400 font-bold font-mono text-[10px] uppercase">Recommended Action: </span>
                    Preemptively deploy Tactical Unit R4 (Guardian-4) with trauma life support and activate Highland Shelter B before road passability drops to 0%.
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons: [ ASK AEGIS ], [ VIEW EVIDENCE ], [ PREDICT ], [ SIMULATE ] */}
            <div className="mt-4 pt-3 border-t border-slate-800 flex items-center space-x-1.5">
              <button
                onClick={() => {
                  window.dispatchEvent(new CustomEvent('aegis:ask-orchestrator', {
                    detail: { query: 'Explain the Zone 7 isolation alert in detail.' }
                  }));
                }}
                className="px-3 py-2 rounded bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-black text-[10px] flex items-center space-x-1 shadow-[0_0_15px_rgba(0,240,255,0.4)] transition-all"
                title="Query AEGIS Orchestrator about Zone 7 isolation"
              >
                <Search className="w-3.5 h-3.5" />
                <span>ASK AEGIS</span>
              </button>
              <button
                onClick={() => setInspectingEvidenceDecision('decision-zone-7-escalation')}
                className="flex-1 py-2 rounded bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-cyan-500/40 font-bold tracking-wider text-[10px] flex items-center justify-center space-x-1 transition-all"
              >
                <FileCheck className="w-3 h-3" />
                <span>EVIDENCE</span>
              </button>
              <button
                onClick={() => onNavigate('PREDICT', 'zone-7')}
                className="flex-1 py-2 rounded bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-slate-700 font-bold text-[10px] flex items-center justify-center space-x-1"
              >
                <TrendingUp className="w-3 h-3" />
                <span>PREDICT</span>
              </button>
              <button
                onClick={() => onNavigate('SIMULATE', 'zone-7')}
                className="p-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
                title="Simulate What-If Actions"
              >
                <Sliders className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>



          {/* Quick Zone Detail HUD */}
          {activeZone && (
            <div className="hud-card p-4 rounded-lg flex-1 flex flex-col justify-between border border-slate-800">
              <div>
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <div className="flex items-center space-x-2">
                    <span className="px-1.5 py-0.2 rounded bg-slate-800 text-cyan-300 font-bold text-[10px]">
                      {activeZone.code}
                    </span>
                    <span className="font-bold text-slate-200">{activeZone.name.split('—')[0]}</span>
                  </div>
                  <button
                    onClick={() => setInspectingZone(activeZone)}
                    className="text-[10px] text-cyan-400 hover:text-cyan-300 underline font-bold flex items-center"
                  >
                    <span>FULL TELEMETRY</span>
                    <ChevronRight className="w-3 h-3 ml-0.5" />
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-2 mt-3 text-[11px]">
                  <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
                    <div className="text-slate-400 text-[10px]">Primary Flood Risk</div>
                    <div className="text-amber-400 font-black text-sm">{activeZone.primary_risk_score}/100</div>
                  </div>
                  <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
                    <div className="text-slate-400 text-[10px]">Road Accessibility</div>
                    <div className={`font-black text-sm ${activeZone.road_accessibility_percent < 50 ? 'text-red-400' : 'text-emerald-400'}`}>
                      {activeZone.road_accessibility_percent}%
                    </div>
                  </div>
                  <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
                    <div className="text-slate-400 text-[10px]">Hospital Corridor</div>
                    <div className={`font-black text-sm ${activeZone.hospital_accessibility_percent < 50 ? 'text-red-400' : 'text-cyan-300'}`}>
                      {activeZone.hospital_accessibility_percent}%
                    </div>
                  </div>
                  <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
                    <div className="text-slate-400 text-[10px]">Connectivity</div>
                    <div className={`font-black text-sm uppercase ${
                      activeZone.connectivity_status === 'lost' ? 'text-red-400' :
                      activeZone.connectivity_status === 'degraded' ? 'text-amber-400' : 'text-emerald-400'
                    }`}>
                      {activeZone.connectivity_status}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
                <span>Click any map zone for deep inspection</span>
                <span className="text-cyan-400 font-bold">Confidence: 87%</span>
              </div>
            </div>
          )}
        </div>

        {/* Center Column: Interactive GIS Map (5 cols) */}
        <div className="lg:col-span-5 flex flex-col">
          <TacticalMap
            zones={zones}
            roads={roads}
            infrastructure={infrastructure}
            teams={teams}
            selectedZoneId={activeZone?.id}
            onSelectZone={handleZoneClick}
            onSelectTeam={handleTeamClick}
          />
        </div>

        {/* Right Column: Silent Risk Panel & Cascading Risk Chain (3 cols) */}
        <div className="lg:col-span-3 flex flex-col space-y-3">
          {/* 5. SILENT RISK PANEL (Section 5) */}
          <div className="hud-card p-4 rounded-lg border-l-4 border-l-red-600 space-y-2.5">
            <div className="flex items-center justify-between border-b border-red-500/30 pb-2">
              <div className="flex items-center space-x-1.5 text-red-400 font-bold">
                <Radio className="w-4 h-4 text-red-400 animate-pulse" />
                <span>SILENT RISK PANEL</span>
              </div>
              <span className="px-1.5 py-0.2 rounded bg-red-950 text-red-300 text-[9px] font-bold">
                2 BLINDSPOTS
              </span>
            </div>

            <div className="text-[10px] text-slate-400 leading-tight">
              Rule: <span className="text-slate-200 font-bold">No SOS does NOT mean no victims.</span>
            </div>

            <div className="space-y-2">
              {/* Zone 4 Card */}
              <div className="p-2.5 rounded bg-red-950/30 border border-red-500/40 space-y-1">
                <div className="flex justify-between items-center">
                  <span className="font-extrabold text-white text-xs">ZONE 4 (Riverside Slums)</span>
                  <span className="px-1.5 py-0.2 rounded bg-red-900 text-white font-black text-[9px]">
                    91% PROBABILITY
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-1 text-[10px] text-slate-300 pt-1">
                  <div>Comm: <span className="text-red-400 font-bold">LOST</span></div>
                  <div>Road: <span className="text-red-400 font-bold">BLOCKED</span></div>
                  <div>Pop: <span className="text-white font-bold">9,300</span></div>
                  <div>Reports: <span className="text-red-400 font-bold">0 (Tower Offline)</span></div>
                </div>
                <button
                  onClick={() => {
                    const z4 = zones.find((z) => z.id === 'zone-4');
                    if (z4) handleZoneClick(z4);
                  }}
                  className="mt-1.5 w-full py-1 rounded bg-red-900/60 hover:bg-red-800 text-white font-bold text-[10px] flex items-center justify-center space-x-1"
                >
                  <Search className="w-3 h-3" />
                  <span>INVESTIGATE ZONE 4</span>
                </button>
              </div>

              {/* Zone 9 Card */}
              <div className="p-2.5 rounded bg-red-950/20 border border-red-500/30 space-y-1">
                <div className="flex justify-between items-center">
                  <span className="font-extrabold text-slate-200 text-xs">ZONE 9 (Confluence South)</span>
                  <span className="px-1.5 py-0.2 rounded bg-red-950 text-red-300 font-black text-[9px]">
                    83% PROBABILITY
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-1 text-[10px] text-slate-300 pt-1">
                  <div>Comm: <span className="text-red-400 font-bold">LOST</span></div>
                  <div>Road: <span className="text-red-400 font-bold">18% (Submerged)</span></div>
                  <div>Pop: <span className="text-white font-bold">4,100</span></div>
                  <div>Reports: <span className="text-red-400 font-bold">0</span></div>
                </div>
                <button
                  onClick={() => {
                    const z9 = zones.find((z) => z.id === 'zone-9');
                    if (z9) handleZoneClick(z9);
                  }}
                  className="mt-1.5 w-full py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 font-bold text-[10px] flex items-center justify-center space-x-1 border border-slate-700"
                >
                  <Search className="w-3 h-3" />
                  <span>INVESTIGATE ZONE 9</span>
                </button>
              </div>
            </div>
          </div>

          {/* 6. ACTIVE CASCADE PANEL (Section 19) */}
          <div className="hud-card p-4 rounded-lg flex-1 flex flex-col justify-between border-l-4 border-l-amber-500">
            <div>
              <div className="flex items-center justify-between border-b border-amber-500/30 pb-2">
                <div className="flex items-center space-x-1.5 text-amber-400 font-bold">
                  <Zap className="w-4 h-4 animate-pulse" />
                  <span>ACTIVE CASCADE</span>
                </div>
                <span className="px-1.5 py-0.2 rounded bg-amber-950 text-amber-300 font-mono text-[9px] font-bold">
                  SCORE: {activeCascading?.combined_cascading_score ?? 87}
                </span>
              </div>

              {/* Compact Directional Flow */}
              <div className="mt-3 space-y-1 text-[11px]">
                {[
                  { name: 'Flood Inundation', score: activeZone?.primary_risk_score ?? 82, state: 'SURGING', color: 'text-amber-400' },
                  { name: 'Road Blockage', score: 91, state: 'CUTOFF', color: 'text-red-400' },
                  { name: 'Hospital Access ↓', score: 81, state: 'ISOLATED', color: 'text-red-400' },
                  { name: 'Medical Delay ↑', score: 78, state: 'CRITICAL', color: 'text-red-500' }
                ].map((step, idx, arr) => (
                  <div key={idx} className="flex flex-col">
                    <div className="flex items-center justify-between bg-slate-900/80 px-2.5 py-1 rounded border border-slate-800">
                      <div className="flex items-center space-x-1.5">
                        <span className="text-[9px] text-slate-500 font-bold">{idx + 1}.</span>
                        <span className="font-bold text-slate-200">{step.name}</span>
                      </div>
                      <span className={`text-[9px] font-black ${step.color}`}>{step.state}</span>
                    </div>
                    {idx < arr.length - 1 && (
                      <div className="flex justify-center py-0.5 text-slate-600 text-[10px] leading-none">
                        <span>↓</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="mt-2 text-[10px] text-slate-400">
                Cascading Risk: <span className="text-amber-400 font-black">{activeCascading?.combined_cascading_score ?? 87} / 100</span>
              </div>
            </div>

            <div className="mt-3 pt-2 border-t border-slate-800">
              <button
                onClick={() => setInspectingCascadeZone(activeZone)}
                className="w-full py-1.5 rounded bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/50 font-black text-[10px] flex items-center justify-center space-x-1.5 shadow-[0_0_10px_rgba(245,158,11,0.2)] transition-all"
              >
                <Zap className="w-3.5 h-3.5" />
                <span>VIEW CASCADE</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Modal Dialogs for Zone Detail, Rescue Team, and Cascading Inspection */}
      <ZoneDetailModal
        zone={inspectingZone}
        onClose={() => setInspectingZone(null)}
        onNavigate={onNavigate}
      />

      <RescueTeamModal
        team={inspectingTeam}
        onClose={() => setInspectingTeam(null)}
        onNavigate={onNavigate}
      />

      {inspectingCascadeZone && (
        <CascadeModal
          zoneId={inspectingCascadeZone.id}
          onClose={() => setInspectingCascadeZone(null)}
          onNavigate={onNavigate}
        />
      )}

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

