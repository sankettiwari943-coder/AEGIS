import React from 'react';
import { Zone, MainNavMode } from '../../types';
import { 
  X, 
  AlertTriangle, 
  Radio, 
  TrendingUp, 
  Sliders, 
  ShieldAlert, 
  Activity, 
  Users, 
  Droplets, 
  Zap, 
  Building, 
  FileCheck,
  ArrowRight,
  Compass
} from 'lucide-react';

interface ZoneDetailModalProps {
  zone: Zone | null;
  onClose: () => void;
  onNavigate: (mode: MainNavMode, zoneId?: string) => void;
}

export const ZoneDetailModal: React.FC<ZoneDetailModalProps> = ({ zone, onClose, onNavigate }) => {
  if (!zone) return null;

  const getRiskBadge = (score: number) => {
    if (score >= 80) return { label: 'CRITICAL', bg: 'bg-red-950 text-red-300 border-red-500/60' };
    if (score >= 60) return { label: 'HIGH', bg: 'bg-amber-950 text-amber-300 border-amber-500/60' };
    if (score >= 35) return { label: 'MODERATE', bg: 'bg-blue-950 text-blue-300 border-blue-500/60' };
    return { label: 'LOW', bg: 'bg-emerald-950 text-emerald-300 border-emerald-500/60' };
  };

  const riskBadge = getRiskBadge(zone.primary_risk_score);
  const evidenceCount = zone.id === 'zone-7' ? 5 : (zone.id === 'zone-4' ? 4 : 2);
  const modelConfidence = zone.id === 'zone-7' ? 87 : (zone.id === 'zone-4' ? 91 : 84);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md font-mono select-none animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-[#0b1220] border-2 border-cyan-500/50 rounded-xl shadow-[0_0_50px_rgba(0,240,255,0.2)] overflow-hidden flex flex-col">
        {/* Modal Header */}
        <div className="px-5 py-3.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/40 text-xs font-black">
              {zone.code}
            </span>
            <div>
              <h2 className="text-sm font-extrabold text-white tracking-wide">{zone.name}</h2>
              <div className="text-[10px] text-slate-400 font-sans">{zone.district} • Elev: {zone.elevation_meters}m MSL</div>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <span className={`px-2 py-0.5 rounded text-[10px] font-black border ${riskBadge.bg}`}>
              {riskBadge.label} ({zone.primary_risk_score}/100)
            </span>
            <button
              onClick={onClose}
              className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Modal Body Content */}
        <div className="p-5 space-y-4 max-h-[75vh] overflow-y-auto text-xs">
          {/* Silent Risk Warning if applicable */}
          {zone.is_silent_risk && (
            <div className="p-3 rounded-lg bg-red-950/40 border border-red-500/50 flex items-center justify-between text-red-300">
              <div className="flex items-center space-x-2">
                <Radio className="w-4 h-4 text-red-400 animate-pulse" />
                <span className="font-bold text-[11px]">
                  SILENT CRISIS DETECTED (Anomaly Index: {zone.silent_risk_score}%)
                </span>
              </div>
              <span className="text-[10px] text-red-400 font-sans">
                Cellular Tower Offline • 0 SOS Reports Received
              </span>
            </div>
          )}

          {/* Key Sensor Telemetry Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
            <div className="bg-slate-900/80 p-2.5 rounded border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase">Population</div>
              <div className="text-sm font-extrabold text-white mt-0.5">{zone.population.toLocaleString()}</div>
            </div>
            <div className="bg-slate-900/80 p-2.5 rounded border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase">Flood Depth</div>
              <div className="text-sm font-extrabold text-amber-400 mt-0.5">{zone.current_flood_depth_cm} cm</div>
            </div>
            <div className="bg-slate-900/80 p-2.5 rounded border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase">Precipitation</div>
              <div className="text-sm font-extrabold text-cyan-300 mt-0.5">{zone.rainfall_rate_mmh} mm/h</div>
            </div>
            <div className="bg-slate-900/80 p-2.5 rounded border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase">River Level</div>
              <div className="text-sm font-extrabold text-blue-400 mt-0.5">{zone.river_level_meters} m</div>
            </div>
          </div>

          {/* Infrastructure & Accessibility Telemetry */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Road & Hospital Accessibility */}
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 space-y-2">
              <div className="text-[10px] text-cyan-400 uppercase font-bold">
                ACCESSIBILITY & LOGISTICS
              </div>
              <div className="space-y-1.5 text-[11px]">
                <div className="flex justify-between">
                  <span className="text-slate-400">Road Passability:</span>
                  <span className={`font-bold ${zone.road_accessibility_percent < 50 ? 'text-red-400' : 'text-emerald-400'}`}>
                    {zone.road_accessibility_percent}%
                  </span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${zone.road_accessibility_percent < 50 ? 'bg-red-500' : 'bg-emerald-500'}`} 
                    style={{ width: `${zone.road_accessibility_percent}%` }}
                  />
                </div>

                <div className="flex justify-between pt-1">
                  <span className="text-slate-400">Hospital Corridor Access:</span>
                  <span className={`font-bold ${zone.hospital_accessibility_percent < 50 ? 'text-red-400' : 'text-cyan-300'}`}>
                    {zone.hospital_accessibility_percent}%
                  </span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${zone.hospital_accessibility_percent < 50 ? 'bg-red-500' : 'bg-cyan-400'}`} 
                    style={{ width: `${zone.hospital_accessibility_percent}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Communications & Evidence Grounding */}
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 space-y-2">
              <div className="text-[10px] text-cyan-400 uppercase font-bold">
                COMMUNICATIONS & EVIDENCE
              </div>
              <div className="space-y-1.5 text-[11px]">
                <div className="flex justify-between">
                  <span className="text-slate-400">Connectivity Status:</span>
                  <span className={`font-bold uppercase ${
                    zone.connectivity_status === 'lost' ? 'text-red-400' :
                    zone.connectivity_status === 'degraded' ? 'text-amber-400' :
                    'text-emerald-400'
                  }`}>
                    {zone.connectivity_status}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">SOS Reports (Last Hour):</span>
                  <span className="text-white font-bold">{zone.sos_reports_last_hour} reports</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Verified Evidence Claims:</span>
                  <span className="text-cyan-300 font-bold">{evidenceCount} multi-source matches</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Model Confidence:</span>
                  <span className="text-emerald-400 font-bold">{modelConfidence}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Secondary Risks Breakdown */}
          <div className="bg-slate-900/90 p-3.5 rounded-lg border border-slate-800 space-y-2.5">
            <div className="text-[10px] text-slate-400 uppercase font-bold flex justify-between">
              <span>SECONDARY SYSTEMIC RISKS</span>
              <span className="text-cyan-400">Cascading Score: {zone.cascading_risk_score}/100</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center text-[10px]">
              <div className="bg-slate-950 p-2 rounded border border-slate-800/80">
                <div className="text-slate-500">Power Failure</div>
                <div className="font-bold text-amber-400 text-xs mt-0.5">{zone.secondary_risks.power || 20}%</div>
              </div>
              <div className="bg-slate-950 p-2 rounded border border-slate-800/80">
                <div className="text-slate-500">Medical Access</div>
                <div className="font-bold text-red-400 text-xs mt-0.5">{zone.secondary_risks.medical || 30}%</div>
              </div>
              <div className="bg-slate-950 p-2 rounded border border-slate-800/80">
                <div className="text-slate-500">Water Contam</div>
                <div className="font-bold text-cyan-300 text-xs mt-0.5">{zone.secondary_risks.water || 25}%</div>
              </div>
              <div className="bg-slate-950 p-2 rounded border border-slate-800/80">
                <div className="text-slate-500">Telecom Loss</div>
                <div className="font-bold text-indigo-400 text-xs mt-0.5">{zone.secondary_risks.telecom || 10}%</div>
              </div>
              <div className="bg-slate-950 p-2 rounded border border-slate-800/80 col-span-2 sm:col-span-1">
                <div className="text-slate-500">Road Cutoff</div>
                <div className="font-bold text-red-400 text-xs mt-0.5">{zone.secondary_risks.roads || 35}%</div>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Action Footer */}
        <div className="px-5 py-3 bg-slate-900 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2">
          <button
            onClick={() => {
              onClose();
              onNavigate('PREDICT', zone.id);
            }}
            className="px-3 py-2 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 font-bold text-xs flex items-center space-x-1.5 border border-slate-700"
          >
            <TrendingUp className="w-3.5 h-3.5" />
            <span>PREDICT TRAJECTORY</span>
          </button>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => {
                onClose();
                onNavigate('SIMULATE', zone.id);
              }}
              className="px-3.5 py-2 rounded bg-cyan-500 hover:bg-cyan-400 text-black font-extrabold text-xs flex items-center space-x-1.5 shadow-[0_0_15px_rgba(0,240,255,0.4)]"
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>SIMULATE ACTIONS</span>
            </button>
            <button
              onClick={() => {
                onClose();
                onNavigate('MISSIONS', zone.id);
              }}
              className="px-3.5 py-2 rounded bg-emerald-500 hover:bg-emerald-400 text-black font-extrabold text-xs flex items-center space-x-1.5"
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>DISPATCH RESCUE TEAM</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
