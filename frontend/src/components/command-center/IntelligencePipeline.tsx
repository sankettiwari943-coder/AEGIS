import React, { useState } from 'react';
import { MainNavMode } from '../../types';
import { DataSourceBadge } from '../common/DataSourceBadge';
import { ConfidenceBadge } from '../common/ConfidenceBadge';
import {
  Layers,
  ChevronDown,
  ChevronUp,
  Activity,
  Cpu,
  TrendingUp,
  Share2,
  Radio,
  FileCheck,
  BookOpen,
  ShieldAlert,
  Sliders,
  Sparkles,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';

interface IntelligencePipelineProps {
  onNavigate: (mode: MainNavMode, zoneId?: string) => void;
  selectedZoneId?: string;
  activeSimulatorStep?: number;
}

export const IntelligencePipeline: React.FC<IntelligencePipelineProps> = ({
  onNavigate,
  selectedZoneId = 'zone-7',
  activeSimulatorStep = 0
}) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(true);

  const pipelineStages = [
    {
      id: 'ingestion',
      number: '01',
      title: 'DATA INGESTION',
      subtitle: 'Multi-Connector Adapter Grid',
      status: 'ACTIVE',
      statusColor: 'emerald',
      sourceType: 'SENSOR',
      metric: '5 Live Feeds Active',
      confidence: 94,
      icon: Activity,
      navMode: 'LIVE' as MainNavMode,
      description: 'Doppler radar, ultrasonic river gauges, municipal SCADA, and citizen CAD dispatch.'
    },
    {
      id: 'situation',
      number: '02',
      title: 'SITUATION STATE',
      subtitle: 'Multi-Source Geospatial Fusion',
      status: 'UPDATED',
      statusColor: 'cyan',
      sourceType: 'LIVE',
      metric: '12 Sectors Monitored',
      confidence: 92,
      icon: Layers,
      navMode: 'LIVE' as MainNavMode,
      description: 'Dynamic hydrological depth aggregation and critical infrastructure coordinate mapping.'
    },
    {
      id: 'prediction',
      number: '03',
      title: 'PREDICTION ENGINE',
      subtitle: 'Escalation & Isolation Models',
      status: 'CRITICAL WARNING',
      statusColor: 'red',
      sourceType: 'AI-INFERRED',
      metric: 'Z7 Cutoff in ~42m',
      confidence: 86,
      icon: TrendingUp,
      navMode: 'PREDICT' as MainNavMode,
      description: 'Continuous predictive trajectories modeled across 30m, 60m, and 3-hour horizons.'
    },
    {
      id: 'cascade',
      number: '04',
      title: 'CASCADE ANALYSIS',
      subtitle: 'Cross-Infrastructure Ripple Graph',
      status: 'ELEVATED',
      statusColor: 'amber',
      sourceType: 'AI-INFERRED',
      metric: 'Index: 87/100',
      confidence: 88,
      icon: Share2,
      navMode: 'COMMAND' as MainNavMode,
      description: 'Substation #2 inundation threats to Basin Drainage Pumps and hospital ICU access.'
    },
    {
      id: 'silent_risk',
      number: '05',
      title: 'SILENT CRISIS ENGINE',
      subtitle: 'Zero-Report Anomaly Detection',
      status: 'ANOMALY DETECTED',
      statusColor: 'amber',
      sourceType: 'SENSOR',
      metric: 'Zone 4 Flagged (91%)',
      confidence: 91,
      icon: Radio,
      navMode: 'EVIDENCE' as MainNavMode,
      description: 'Identifies high-hazard civilian clusters masked by cellular telecom blackout.'
    },
    {
      id: 'evidence',
      number: '06',
      title: 'EVIDENCE & TRUTH',
      subtitle: 'Contradiction & Sensor Cross-Check',
      status: 'VERIFIED',
      statusColor: 'emerald',
      sourceType: 'OFFICIAL',
      metric: '91% Trust (14 Claims)',
      confidence: 91,
      icon: FileCheck,
      navMode: 'EVIDENCE' as MainNavMode,
      description: 'Corroborates SAR radar overpass against physical river sensors and emergency CAD.'
    },
    {
      id: 'rag',
      number: '07',
      title: 'RAG KNOWLEDGE LAYER',
      subtitle: 'Emergency SOP & Doctrinal Retrieval',
      status: 'INDEXED',
      statusColor: 'indigo',
      sourceType: 'RAG',
      metric: '6 Standard SOPs Loaded',
      confidence: 95,
      icon: BookOpen,
      navMode: 'AI' as MainNavMode,
      description: 'Embeds NDMA riverine flood manuals, evacuation routing, and critical hospital protocols.'
    },
    {
      id: 'mission_optimizer',
      number: '08',
      title: 'MISSION OPTIMIZER',
      subtitle: 'Multi-Attribute Utility Allocation',
      status: 'RECOMMENDED',
      statusColor: 'cyan',
      sourceType: 'AI-INFERRED',
      metric: 'Delta-2 (Score: 97)',
      confidence: 94,
      icon: ShieldAlert,
      navMode: 'MISSIONS' as MainNavMode,
      description: 'Balances travel ETA against boat/medical payload capabilities and flood obstacle hazards.'
    },
    {
      id: 'simulation',
      number: '09',
      title: 'WHAT-IF SIMULATOR',
      subtitle: 'Counterfactual Scenario Testing',
      status: 'CALCULATED',
      statusColor: 'cyan',
      sourceType: 'SIMULATED',
      metric: '-27 Pts Risk Cut (29.7%)',
      confidence: 88,
      icon: Sliders,
      navMode: 'SIMULATE' as MainNavMode,
      description: 'Compares unmitigated baseline against proactive evacuation + rescue intervention.'
    },
    {
      id: 'human_approval',
      number: '10',
      title: 'HUMAN-IN-THE-LOOP',
      subtitle: 'Commander Decision Support',
      status: 'AWAITING APPROVAL',
      statusColor: 'emerald',
      sourceType: 'OFFICIAL',
      metric: 'Zero Autonomous Action',
      confidence: 100,
      icon: CheckCircle2,
      navMode: 'MISSIONS' as MainNavMode,
      description: 'Explicit commander authorization required for every simulated dispatch and resource order.'
    }
  ];

  return (
    <div className="hud-card p-4 rounded-2xl border border-cyan-500/30 bg-gradient-to-r from-slate-950 via-[#070e1b] to-slate-950 shadow-xl select-none">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-xs sm:text-sm font-black text-white tracking-wider flex items-center space-x-1.5">
                <span>AEGIS UNIFIED INTELLIGENCE PIPELINE</span>
              </h2>
              <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/40 text-cyan-300 text-[9px] font-black">
                10-STAGE DETERMINISTIC REASONING
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-sans mt-0.5">
              End-to-end data provenance from raw telemetry ingestion to operator decision sign-off.
            </p>
          </div>
        </div>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-700 text-xs flex items-center space-x-1 transition-all"
        >
          <span className="text-[10px] font-bold">{isExpanded ? 'COLLAPSE' : 'EXPAND PIPELINE'}</span>
          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Expanded Pipeline Stages Horizontal Flow */}
      {isExpanded && (
        <div className="mt-3 pt-1">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-10 gap-2">
            {pipelineStages.map((st, idx) => {
              const Icon = st.icon;
              return (
                <div
                  key={st.id}
                  onClick={() => onNavigate(st.navMode, selectedZoneId)}
                  className="bg-slate-950/80 hover:bg-slate-900 border border-slate-800/90 hover:border-cyan-500/50 p-2.5 rounded-xl flex flex-col justify-between space-y-2 cursor-pointer transition-all hover:scale-[1.02] shadow-sm group"
                >
                  {/* Top: Stage Number & Icon */}
                  <div className="flex items-center justify-between">
                    <span className="text-[9px] font-black text-slate-500 group-hover:text-cyan-400">
                      #{st.number}
                    </span>
                    <Icon className="w-3.5 h-3.5 text-slate-400 group-hover:text-cyan-400 transition-colors" />
                  </div>

                  {/* Title & Subtitle */}
                  <div>
                    <div className="text-[10px] font-black text-white group-hover:text-cyan-300 truncate leading-tight">
                      {st.title}
                    </div>
                    <div className="text-[8px] text-slate-400 truncate font-sans">
                      {st.subtitle}
                    </div>
                  </div>

                  {/* Provenance & Metric */}
                  <div className="space-y-1 pt-1 border-t border-slate-800/80">
                    <div className="text-[9px] font-bold text-cyan-300 truncate">
                      {st.metric}
                    </div>
                    <div className="flex items-center justify-between">
                      <DataSourceBadge sourceType={st.sourceType} size="sm" />
                      <span className="text-[8px] text-slate-500 font-mono">{st.confidence}%</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

    </div>
  );
};
