import React from 'react';
import { RescueTeam, MainNavMode } from '../../types';
import { 
  X, 
  ShieldAlert, 
  Anchor, 
  HeartPulse, 
  MapPin, 
  Clock, 
  Users, 
  CheckCircle2, 
  AlertCircle,
  ArrowRight
} from 'lucide-react';

interface RescueTeamModalProps {
  team: RescueTeam | null;
  onClose: () => void;
  onNavigate: (mode: MainNavMode, zoneId?: string) => void;
}

export const RescueTeamModal: React.FC<RescueTeamModalProps> = ({ team, onClose, onNavigate }) => {
  if (!team) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md font-mono select-none animate-in fade-in duration-200">
      <div className="w-full max-w-lg bg-[#0b1220] border-2 border-cyan-500/50 rounded-xl shadow-[0_0_40px_rgba(0,240,255,0.25)] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-5 py-3.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-500/40">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-extrabold text-white">{team.callsign}</h2>
              <div className="text-[10px] text-slate-400">{team.unit_type} • ID: {team.id.toUpperCase()}</div>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <span className={`px-2 py-0.5 rounded text-[10px] font-black border uppercase ${
              team.status === 'ready' ? 'bg-emerald-950 text-emerald-300 border-emerald-500/50' :
              team.status === 'dispatched' ? 'bg-cyan-950 text-cyan-300 border-cyan-500/50' :
              'bg-amber-950 text-amber-300 border-amber-500/50'
            }`}>
              {team.status}
            </span>
            <button
              onClick={onClose}
              className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4 text-xs">
          <div className="grid grid-cols-2 gap-2 text-center">
            <div className="bg-slate-900/80 p-2.5 rounded border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase">Station Sector</div>
              <div className="text-sm font-extrabold text-cyan-300 mt-0.5">
                {team.assigned_zone_id ? team.assigned_zone_id.toUpperCase() : 'CENTRAL BASE'}
              </div>
            </div>
            <div className="bg-slate-900/80 p-2.5 rounded border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase">Crew Complement</div>
              <div className="text-sm font-extrabold text-white mt-0.5">{team.crew_size} Specialists</div>
            </div>
          </div>

          {/* Capabilities Grid */}
          <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 space-y-2">
            <div className="text-[10px] text-cyan-400 uppercase font-bold">
              EQUIPMENT & CAPABILITIES
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="flex items-center space-x-2 bg-slate-950 p-2 rounded border border-slate-800">
                <span className={`w-2 h-2 rounded-full ${team.has_boat ? 'bg-emerald-400' : 'bg-slate-600'}`} />
                <span className="text-slate-300">Rescue Boat: <span className={team.has_boat ? 'text-emerald-400 font-bold' : 'text-slate-500'}>{team.has_boat ? 'YES' : 'NO'}</span></span>
              </div>
              <div className="flex items-center space-x-2 bg-slate-950 p-2 rounded border border-slate-800">
                <span className={`w-2 h-2 rounded-full ${team.has_medical ? 'bg-emerald-400' : 'bg-slate-600'}`} />
                <span className="text-slate-300">Trauma Medics: <span className={team.has_medical ? 'text-emerald-400 font-bold' : 'text-slate-500'}>{team.has_medical ? 'YES' : 'NO'}</span></span>
              </div>
              <div className="flex items-center space-x-2 bg-slate-950 p-2 rounded border border-slate-800">
                <span className={`w-2 h-2 rounded-full ${team.has_swift_water ? 'bg-emerald-400' : 'bg-slate-600'}`} />
                <span className="text-slate-300">Swiftwater Unit: <span className={team.has_swift_water ? 'text-emerald-400 font-bold' : 'text-slate-500'}>{team.has_swift_water ? 'YES' : 'NO'}</span></span>
              </div>
              <div className="flex items-center space-x-2 bg-slate-950 p-2 rounded border border-slate-800">
                <span className={`w-2 h-2 rounded-full ${team.has_amphibious ? 'bg-emerald-400' : 'bg-slate-600'}`} />
                <span className="text-slate-300">Amphibious Hull: <span className={team.has_amphibious ? 'text-emerald-400 font-bold' : 'text-slate-500'}>{team.has_amphibious ? 'YES' : 'NO'}</span></span>
              </div>
            </div>
          </div>

          <div className="p-2.5 rounded bg-cyan-950/30 border border-cyan-500/30 text-slate-300 text-[11px] font-sans">
            <span className="font-mono text-cyan-400 font-bold uppercase text-[10px]">Mission Readiness: </span>
            {team.status === 'ready' 
              ? 'Asset fueled and staged for immediate high-priority dispatch.'
              : `Asset currently ${team.status} under active mission command.`}
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 bg-slate-900 border-t border-slate-800 flex justify-between items-center">
          <button
            onClick={onClose}
            className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs"
          >
            CLOSE
          </button>
          <button
            onClick={() => {
              onClose();
              onNavigate('MISSIONS', team.assigned_zone_id || 'zone-7');
            }}
            className="px-4 py-2 rounded bg-cyan-500 hover:bg-cyan-400 text-black font-extrabold text-xs flex items-center space-x-1.5 shadow-[0_0_15px_rgba(0,240,255,0.4)]"
          >
            <span>ASSIGN TO MISSION</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
