import React, { useState } from 'react';
import { MissionRecommendation, RescueTeam } from '../../types';
import { DataSourceBadge } from '../common/DataSourceBadge';
import { ConfidenceBadge } from '../common/ConfidenceBadge';
import {
  ShieldAlert,
  CheckCircle2,
  X,
  Sliders,
  AlertTriangle,
  Zap,
  Clock,
  MapPin,
  Users,
  Shield,
  FileCheck,
  ChevronRight
} from 'lucide-react';

interface HumanApprovalPanelProps {
  recommendation: MissionRecommendation;
  onApprove: () => void;
  onModify: () => void;
  onDismiss: () => void;
  status: 'PENDING' | 'APPROVED' | 'DISMISSED';
}

export const HumanApprovalPanel: React.FC<HumanApprovalPanelProps> = ({
  recommendation,
  onApprove,
  onModify,
  onDismiss,
  status
}) => {
  const team = recommendation.recommended_team;

  return (
    <div className="hud-card p-4 rounded-2xl border-2 border-emerald-500/40 bg-gradient-to-b from-slate-950 via-[#071510] to-slate-950 shadow-2xl font-mono text-xs select-none space-y-4">
      
      {/* Top Banner: Decision Workflow Status */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-emerald-500/30 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/50 shadow-[0_0_12px_rgba(16,185,129,0.3)]">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-xs sm:text-sm font-black text-white tracking-wider">
                HUMAN-IN-THE-LOOP MISSION DECISION SUPPORT
              </h3>
              <DataSourceBadge sourceType="OFFICIAL" sourceLabel="COMMAND APPROVAL" size="sm" />
            </div>
            <p className="text-[10px] text-slate-400 font-sans mt-0.5">
              AEGIS decision recommendations require explicit operator sign-off prior to tactical dispatch.
            </p>
          </div>
        </div>

        {/* Workflow State Pill */}
        <div className="flex items-center space-x-2">
          {status === 'APPROVED' ? (
            <span className="px-3 py-1 rounded-full bg-emerald-500 text-black font-black text-[10px] shadow-[0_0_12px_rgba(16,185,129,0.5)] flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>OPERATOR APPROVED</span>
            </span>
          ) : status === 'DISMISSED' ? (
            <span className="px-3 py-1 rounded-full bg-slate-800 text-slate-400 font-black text-[10px] border border-slate-700 flex items-center space-x-1">
              <X className="w-3.5 h-3.5" />
              <span>DEFERRED / DISMISSED</span>
            </span>
          ) : (
            <span className="px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/50 font-black text-[10px] flex items-center space-x-1 animate-pulse">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>AWAITING OPERATOR AUTHORIZATION</span>
            </span>
          )}
        </div>
      </div>

      {/* Recommended Action Summary */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
        
        {/* Left: Recommended Action & Required Resources (7 cols) */}
        <div className="md:col-span-7 space-y-3">
          
          <div className="bg-slate-900/90 p-3.5 rounded-xl border border-slate-800 space-y-2">
            <div className="flex justify-between items-center text-[10px] text-slate-400 font-bold">
              <span>RECOMMENDED OPERATIONAL ACTION</span>
              <span className="text-cyan-300 font-black">UTILITY SCORE: {team.total_mission_score}/100</span>
            </div>

            <div className="text-base font-black text-white flex items-center space-x-2">
              <span className="text-emerald-400">DEPLOY {team.callsign}</span>
              <span className="text-slate-500">&rarr;</span>
              <span>{recommendation.target_zone_name}</span>
            </div>

            <p className="text-xs text-slate-300 font-sans leading-relaxed">
              Dispatch certified heavy water rescue unit equipped with flood rescue boats and onboard paramedics to extract 12 stranded civilians and stabilize 3 trauma patients.
            </p>
          </div>

          {/* Required Resources & Capabilities */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
              <span className="text-[9px] text-slate-500 uppercase block">ESTIMATED ETA</span>
              <span className="text-sm font-black text-cyan-300 flex items-center space-x-1 mt-0.5">
                <Clock className="w-3 h-3 text-cyan-400" />
                <span>{team.travel_time_minutes} min</span>
              </span>
            </div>

            <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
              <span className="text-[9px] text-slate-500 uppercase block">DISTANCE</span>
              <span className="text-sm font-black text-slate-200 flex items-center space-x-1 mt-0.5">
                <MapPin className="w-3 h-3 text-slate-400" />
                <span>{team.distance_km} km</span>
              </span>
            </div>

            <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
              <span className="text-[9px] text-slate-500 uppercase block">CREW & ASSETS</span>
              <span className="text-xs font-black text-emerald-300 flex items-center space-x-1 mt-0.5 truncate">
                <Users className="w-3 h-3 text-emerald-400 shrink-0" />
                <span>15 Seats • Medics</span>
              </span>
            </div>

            <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
              <span className="text-[9px] text-slate-500 uppercase block">RISK REDUCTION</span>
              <span className="text-sm font-black text-emerald-400 flex items-center space-x-1 mt-0.5">
                <Zap className="w-3 h-3 text-emerald-400" />
                <span>-27 Pts (29%)</span>
              </span>
            </div>
          </div>

          {/* Why Rationale Bullets */}
          <div className="p-3 bg-emerald-950/20 rounded-xl border border-emerald-500/30 space-y-1.5">
            <span className="text-[10px] font-black text-emerald-300 uppercase tracking-wider block">
              SUPPORTING RATIONALE & TRADE-OFF JUSTIFICATION
            </span>
            <ul className="space-y-1 text-xs font-sans text-slate-300">
              {team.why_this_team?.map((bullet, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span>{bullet}</span>
                </li>
              ))}
            </ul>
          </div>

        </div>

        {/* Right: Supporting Evidence & Approval Actions (5 cols) */}
        <div className="md:col-span-5 flex flex-col justify-between space-y-3">
          
          {/* Supporting Evidence Chain */}
          <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 space-y-2 flex-1">
            <div className="flex justify-between items-center text-[10px] text-slate-400 font-bold border-b border-slate-800 pb-1.5">
              <span className="flex items-center space-x-1">
                <FileCheck className="w-3 h-3 text-cyan-400" />
                <span>SUPPORTING EVIDENCE SIGNALS</span>
              </span>
              <ConfidenceBadge confidencePercent={recommendation.evidence_confidence_percent || 91} size="sm" />
            </div>

            <ul className="space-y-1.5 text-[11px] font-sans text-slate-300">
              <li className="flex items-start space-x-2">
                <span className="text-cyan-400 font-bold">1.</span>
                <span>42 Ultrasonic Hydrological Gauges confirm 7.85m crest stage.</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-cyan-400 font-bold">2.</span>
                <span>SAR Satellite Inundation footprint reveals 78% low-lying flood.</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-cyan-400 font-bold">3.</span>
                <span>CAD dispatch #911-8812 verifies 3 oxygen-dependent casualties.</span>
              </li>
            </ul>
          </div>

          {/* Action Approval Bar */}
          <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 space-y-2">
            {status === 'APPROVED' ? (
              <div className="p-2.5 rounded-lg bg-emerald-950/80 border border-emerald-500 text-emerald-300 font-bold text-center space-y-0.5">
                <div className="flex items-center justify-center space-x-1.5 text-xs">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>MISSION AUTHORIZED & DISPATCHED (SIMULATION)</span>
                </div>
                <div className="text-[10px] text-emerald-400/80 font-sans">
                  Feedback recorded to Adaptive Learning Audit Log.
                </div>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <button
                  onClick={onApprove}
                  className="flex-1 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-black text-xs shadow-[0_0_15px_rgba(16,185,129,0.4)] flex items-center justify-center space-x-1.5 transition-all"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>AUTHORIZE & DISPATCH</span>
                </button>

                <button
                  onClick={onModify}
                  className="px-3 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs border border-slate-700 flex items-center space-x-1 transition-all"
                  title="Modify Team Assignment"
                >
                  <Sliders className="w-3.5 h-3.5 text-cyan-400" />
                  <span>MODIFY</span>
                </button>

                <button
                  onClick={onDismiss}
                  className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 transition-all"
                  title="Decline / Dismiss Recommendation"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

        </div>

      </div>

    </div>
  );
};
