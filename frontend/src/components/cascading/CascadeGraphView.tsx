import React, { useState, useMemo } from 'react';
import { 
  ZoneCascadeGraphResponse, CascadeNode, CascadeEdge, CascadeChain, 
  CascadeAlert, CascadeContributor, MainNavMode 
} from '../../types';
import { 
  Zap, 
  AlertTriangle, 
  ShieldAlert, 
  Activity, 
  Sliders, 
  CheckCircle2, 
  ChevronRight, 
  Layers, 
  Radio, 
  RotateCw, 
  ArrowRight, 
  Info, 
  Droplets, 
  Building, 
  Users, 
  Crosshair, 
  Sparkles,
  X,
  ExternalLink,
  Flame
} from 'lucide-react';

interface CascadeGraphViewProps {
  graphData: ZoneCascadeGraphResponse;
  onNavigate?: (mode: MainNavMode, zoneId?: string) => void;
  compact?: boolean;
}

export const CascadeGraphView: React.FC<CascadeGraphViewProps> = ({
  graphData,
  onNavigate,
  compact = false
}) => {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>("road_blockage");
  const [selectedEdge, setSelectedEdge] = useState<CascadeEdge | null>(null);
  const [activeChainId, setActiveChainId] = useState<string | null>(graphData.top_chains[0]?.chain_id || null);

  const selectedNode = useMemo(() => {
    return graphData.nodes.find((n) => n.id === selectedNodeId) || null;
  }, [graphData.nodes, selectedNodeId]);

  const activeChain = useMemo(() => {
    return graphData.top_chains.find((c) => c.chain_id === activeChainId) || graphData.top_chains[0];
  }, [graphData.top_chains, activeChainId]);

  // Layout node positions organized by depth levels
  const nodePositions: Record<string, { x: number; y: number }> = {
    // Level 0: Triggers / Meteorological
    rainfall_surge: { x: 80, y: 70 },
    river_crest: { x: 230, y: 70 },

    // Level 1: Core Primary Hazard
    flood: { x: 155, y: 175 },

    // Level 2: Municipal Subsystems
    power_failure: { x: 75, y: 285 },
    road_blockage: { x: 235, y: 285 },
    telecom_blackout: { x: 395, y: 285 },
    water_contamination: { x: 550, y: 285 },

    // Level 3: Intermediate Collapses
    pump_failure: { x: 75, y: 395 },
    hospital_isolation: { x: 235, y: 395 },
    reporting_blackout: { x: 395, y: 395 },
    population_isolation: { x: 550, y: 395 },

    // Level 4: Secondary Emergencies
    medical_delay: { x: 195, y: 505 },
    medical_supply_shortage: { x: 315, y: 505 },
    silent_crisis_blindspot: { x: 435, y: 505 },
    sanitation_failure: { x: 75, y: 505 },

    // Level 5: Systemic Casualty Endpoint
    victim_risk: { x: 315, y: 610 }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'hazard':
        return { border: 'border-cyan-500', text: 'text-cyan-400', bg: 'bg-cyan-950/80', glow: 'rgba(0,240,255,0.4)', fill: '#06b6d4' };
      case 'infrastructure':
        return { border: 'border-amber-500', text: 'text-amber-400', bg: 'bg-amber-950/80', glow: 'rgba(245,158,11,0.4)', fill: '#f59e0b' };
      case 'medical':
        return { border: 'border-red-500', text: 'text-red-400', bg: 'bg-red-950/80', glow: 'rgba(239,68,68,0.5)', fill: '#ef4444' };
      case 'communication':
      case 'silent_crisis':
        return { border: 'border-purple-500', text: 'text-purple-400', bg: 'bg-purple-950/80', glow: 'rgba(168,85,247,0.4)', fill: '#a855f7' };
      case 'population':
        return { border: 'border-rose-500', text: 'text-rose-400', bg: 'bg-rose-950/80', glow: 'rgba(244,63,94,0.5)', fill: '#f43f5e' };
      case 'environmental':
        return { border: 'border-emerald-500', text: 'text-emerald-400', bg: 'bg-emerald-950/80', glow: 'rgba(16,185,129,0.4)', fill: '#10b981' };
      default:
        return { border: 'border-slate-500', text: 'text-slate-300', bg: 'bg-slate-900', glow: 'rgba(148,163,184,0.3)', fill: '#94a3b8' };
    }
  };

  const isNodeInActiveChain = (nodeId: string) => {
    if (!activeChain) return false;
    return activeChain.steps.some((s) => s.node_id === nodeId);
  };

  const isEdgeInActiveChain = (source: string, target: string) => {
    if (!activeChain) return false;
    const steps = activeChain.steps;
    for (let i = 0; i < steps.length - 1; i++) {
      if (steps[i].node_id === source && steps[i + 1].node_id === target) {
        return true;
      }
    }
    return false;
  };

  return (
    <div className="w-full flex flex-col space-y-3 font-mono text-xs select-none">
      {/* 1. Top Cascading Threats Selector Bar */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-2 bg-slate-900/90 p-2.5 rounded-lg border border-slate-800">
        <div className="flex items-center space-x-2">
          <span className="p-1 rounded bg-amber-950 text-amber-400 border border-amber-500/40">
            <Zap className="w-4 h-4 animate-pulse" />
          </span>
          <div>
            <div className="text-[11px] font-black text-white uppercase tracking-wider flex items-center space-x-2">
              <span>{graphData.zone_name} — CASCADING THREAT CHAINS</span>
              <span className="px-1.5 py-0.2 rounded bg-amber-950 text-amber-300 border border-amber-500/40 text-[9px] font-bold">
                CASCADE SCORE: {graphData.cascading_risk} / 100
              </span>
            </div>
            <div className="text-[10px] text-slate-400">
              Depth: <span className="text-cyan-300 font-bold">4 levels</span> • Max: <span className="text-slate-300">5</span> • Feedback Loops: <span className="text-amber-400 font-bold">{graphData.cycles_detected.length} Detected</span>
            </div>
          </div>
        </div>

        {/* Chain selector pills */}
        <div className="flex items-center space-x-1 overflow-x-auto w-full md:w-auto pb-1 md:pb-0">
          {graphData.top_chains.map((chain, idx) => (
            <button
              key={chain.chain_id}
              onClick={() => {
                setActiveChainId(chain.chain_id);
                setSelectedEdge(null);
                if (chain.steps.length > 1) {
                  setSelectedNodeId(chain.steps[1].node_id);
                }
              }}
              className={`px-2.5 py-1 rounded text-[10px] font-black transition-all flex items-center space-x-1 shrink-0 ${
                activeChainId === chain.chain_id
                  ? 'bg-amber-500 text-black shadow-[0_0_12px_rgba(245,158,11,0.5)]'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white border border-slate-700'
              }`}
            >
              <span>THREAT 0{idx + 1}</span>
              <span className={`text-[9px] font-bold ${activeChainId === chain.chain_id ? 'text-black' : 'text-amber-400'}`}>
                ({chain.priority_score})
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* 2. Operational Cascade Alerts (Section 14) */}
      {graphData.alerts.length > 0 && (
        <div className="bg-red-950/40 border border-red-500/50 p-2.5 rounded-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-2 shadow-[0_0_15px_rgba(239,68,68,0.15)]">
          <div className="flex items-center space-x-2">
            <span className="p-1 rounded bg-red-900 text-red-300 animate-pulse">
              <AlertTriangle className="w-4 h-4" />
            </span>
            <div>
              <div className="text-xs font-black text-red-300 flex items-center space-x-1.5">
                <span>⚠ CASCADE ALERT: {graphData.alerts[0].title}</span>
                <span className="px-1.5 py-0.2 rounded bg-red-900 text-white text-[9px] font-black">
                  SECONDARY RISK: {graphData.alerts[0].secondary_risk_score}
                </span>
              </div>
              <div className="text-[10px] text-slate-300 mt-0.5">
                {graphData.alerts[0].description} (Current: <span className="text-emerald-400 font-bold">{graphData.alerts[0].current_value}</span> ➔ Predicted: <span className="text-red-400 font-bold">{graphData.alerts[0].predicted_value}</span>)
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-1.5 shrink-0">
            {graphData.alerts[0].target_node && (
              <button
                onClick={() => {
                  setSelectedNodeId(graphData.alerts[0].target_node || null);
                  setSelectedEdge(null);
                }}
                className="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-cyan-500/40 font-bold text-[10px] flex items-center space-x-1"
              >
                <Crosshair className="w-3 h-3" />
                <span>VIEW CHAIN</span>
              </button>
            )}
            {onNavigate && (
              <button
                onClick={() => onNavigate('SIMULATE', graphData.zone_id)}
                className="px-3 py-1 rounded bg-red-600 hover:bg-red-500 text-white font-black text-[10px] flex items-center space-x-1 shadow-[0_0_10px_rgba(239,68,68,0.4)]"
              >
                <Sliders className="w-3 h-3" />
                <span>SIMULATE</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* 3. Main Split View: Tactical Interactive Graph + Explainability Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 min-h-[520px]">
        {/* Left / Center Column: Interactive SVG Graph Canvas (8 cols) */}
        <div className="lg:col-span-8 bg-[#090e17] rounded-lg border border-slate-800 p-3 flex flex-col relative overflow-hidden">
          {/* Subtle Grid Background */}
          <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-40 pointer-events-none" />

          {/* Graph Header Legend */}
          <div className="flex items-center justify-between z-10 mb-2 text-[10px] text-slate-400 border-b border-slate-800/80 pb-2">
            <div className="flex items-center space-x-3">
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-cyan-400" />
                <span>Hazard</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-amber-400" />
                <span>Infrastructure</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-red-400" />
                <span>Medical</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-purple-400" />
                <span>Telecom / Silent</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-rose-500" />
                <span>Population</span>
              </span>
            </div>
            <div className="flex items-center space-x-1 text-slate-400">
              <Sparkles className="w-3 h-3 text-cyan-400" />
              <span>Click any node or edge for deep telemetry</span>
            </div>
          </div>

          {/* SVG Dependency Flow Canvas */}
          <div className="flex-1 relative overflow-auto flex items-center justify-center min-h-[460px]">
            <svg 
              viewBox="0 0 640 680" 
              className="w-full h-full max-h-[640px] select-none"
              style={{ minWidth: '580px' }}
            >
              <defs>
                {/* Directional Arrowheads */}
                <marker
                  id="arrow-default"
                  viewBox="0 0 10 10"
                  refX="8"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 9 5 L 0 9 z" fill="#64748b" />
                </marker>
                <marker
                  id="arrow-active"
                  viewBox="0 0 10 10"
                  refX="8"
                  refY="5"
                  markerWidth="7"
                  markerHeight="7"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 9 5 L 0 9 z" fill="#f59e0b" />
                </marker>
                <marker
                  id="arrow-feedback"
                  viewBox="0 0 10 10"
                  refX="8"
                  refY="5"
                  markerWidth="7"
                  markerHeight="7"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 9 5 L 0 9 z" fill="#ef4444" />
                </marker>

                {/* Animated Edge Glow Gradient */}
                <linearGradient id="edge-glow" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#00f0ff" stopOpacity="0.8" />
                  <stop offset="50%" stopColor="#f59e0b" stopOpacity="0.9" />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity="1" />
                </linearGradient>
              </defs>

              {/* 1. Render Graph Edges */}
              {graphData.edges.map((edge, idx) => {
                const srcPos = nodePositions[edge.source];
                const dstPos = nodePositions[edge.target];
                if (!srcPos || !dstPos) return null;

                const isFeedback = edge.is_feedback_loop;
                const inActive = isEdgeInActiveChain(edge.source, edge.target);
                const isSelected = selectedEdge?.source === edge.source && selectedEdge?.target === edge.target;

                // Path construction (curved for feedback loop, direct bezier for downward flow)
                let pathD = '';
                if (isFeedback) {
                  // Curve back up to flood
                  pathD = `M ${srcPos.x - 20} ${srcPos.y} C ${srcPos.x - 70} ${srcPos.y - 80}, ${dstPos.x - 70} ${dstPos.y + 60}, ${dstPos.x - 25} ${dstPos.y + 10}`;
                } else {
                  const dx = dstPos.x - srcPos.x;
                  const dy = dstPos.y - srcPos.y;
                  const cy1 = srcPos.y + dy * 0.5;
                  const cy2 = srcPos.y + dy * 0.5;
                  pathD = `M ${srcPos.x} ${srcPos.y + 18} C ${srcPos.x} ${cy1}, ${dstPos.x} ${cy2}, ${dstPos.x} ${dstPos.y - 18}`;
                }

                return (
                  <g key={`edge-${idx}`} className="cursor-pointer" onClick={() => {
                    setSelectedEdge(edge);
                    setSelectedNodeId(null);
                  }}>
                    {/* Background wider hit target for easy clicking */}
                    <path
                      d={pathD}
                      fill="none"
                      stroke="transparent"
                      strokeWidth="14"
                    />

                    {/* Visible Edge Line */}
                    <path
                      d={pathD}
                      fill="none"
                      stroke={
                        isSelected ? '#00f0ff' :
                        isFeedback ? '#ef4444' :
                        inActive ? '#f59e0b' : '#334155'
                      }
                      strokeWidth={isSelected ? '3.5' : (inActive || isFeedback ? '2.5' : '1.5')}
                      strokeDasharray={isFeedback ? '4,4' : 'none'}
                      markerEnd={
                        isFeedback ? 'url(#arrow-feedback)' :
                        (inActive || isSelected ? 'url(#arrow-active)' : 'url(#arrow-default)')
                      }
                      className={inActive || isFeedback ? 'transition-all' : ''}
                    />

                    {/* Edge Label for Feedback Loops or Active Chains */}
                    {isFeedback && (
                      <g transform={`translate(${srcPos.x - 85}, ${(srcPos.y + dstPos.y) / 2})`}>
                        <rect x="-4" y="-8" width="76" height="16" rx="3" fill="#450a0a" stroke="#ef4444" strokeWidth="1" />
                        <text x="34" y="3" fill="#fca5a5" fontSize="8" fontWeight="bold" textAnchor="middle">
                          FEEDBACK ↺
                        </text>
                      </g>
                    )}
                  </g>
                );
              })}

              {/* 2. Render Graph Nodes */}
              {graphData.nodes.map((node) => {
                const pos = nodePositions[node.id];
                if (!pos) return null;

                const color = getCategoryColor(node.category);
                const isSelected = selectedNodeId === node.id;
                const inActive = isNodeInActiveChain(node.id);

                return (
                  <g
                    key={`node-${node.id}`}
                    transform={`translate(${pos.x}, ${pos.y})`}
                    className="cursor-pointer transition-transform duration-150 hover:scale-105"
                    onClick={() => {
                      setSelectedNodeId(node.id);
                      setSelectedEdge(null);
                    }}
                  >
                    {/* Node Selection Halo */}
                    {isSelected && (
                      <rect
                        x="-68"
                        y="-22"
                        width="136"
                        height="44"
                        rx="8"
                        fill="none"
                        stroke="#00f0ff"
                        strokeWidth="2"
                        strokeDasharray="4,2"
                        className="animate-pulse"
                      />
                    )}

                    {/* Active Chain Highlight Backing */}
                    {inActive && !isSelected && (
                      <rect
                        x="-64"
                        y="-19"
                        width="128"
                        height="38"
                        rx="6"
                        fill={color.bg}
                        stroke={color.fill}
                        strokeWidth="1.5"
                        style={{ filter: `drop-shadow(0 0 8px ${color.glow})` }}
                      />
                    )}

                    {/* Base Node Box */}
                    <rect
                      x="-60"
                      y="-16"
                      width="120"
                      height="32"
                      rx="5"
                      fill="#0b1322"
                      stroke={isSelected ? '#00f0ff' : (inActive ? color.fill : '#1e293b')}
                      strokeWidth={isSelected ? '2' : '1'}
                    />

                    {/* Category Indicator Dot */}
                    <circle
                      cx="-48"
                      cy="0"
                      r="4"
                      fill={color.fill}
                      className={node.current_risk >= 70 ? 'animate-ping' : ''}
                    />
                    <circle
                      cx="-48"
                      cy="0"
                      r="4"
                      fill={color.fill}
                    />

                    {/* Node Title */}
                    <text
                      x="-38"
                      y="-1"
                      fill="#f8fafc"
                      fontSize="9"
                      fontWeight="bold"
                      textAnchor="start"
                    >
                      {node.label.length > 14 ? node.label.substring(0, 13) + '…' : node.label}
                    </text>

                    {/* Risk Badge */}
                    <text
                      x="-38"
                      y="10"
                      fill={node.current_risk >= 80 ? '#ef4444' : (node.current_risk >= 60 ? '#f59e0b' : '#38bdf8')}
                      fontSize="8"
                      fontWeight="black"
                      textAnchor="start"
                    >
                      RISK: {node.current_risk}
                    </text>

                    {/* Feedback loop icon badge */}
                    {node.is_feedback_source && (
                      <g transform="translate(46, -10)">
                        <circle cx="0" cy="0" r="6" fill="#7f1d1d" stroke="#ef4444" strokeWidth="1" />
                        <text x="0" y="2.5" fill="#ffffff" fontSize="7" fontWeight="bold" textAnchor="middle">↺</text>
                      </g>
                    )}
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Bottom Active Chain Step-by-Step Flow Ribbon */}
          {activeChain && (
            <div className="mt-2 pt-2 border-t border-slate-800 z-10 flex items-center space-x-1.5 overflow-x-auto text-[10px]">
              <span className="text-slate-400 font-bold uppercase shrink-0 flex items-center space-x-1">
                <Activity className="w-3 h-3 text-amber-400" />
                <span>PROPAGATION CHAIN:</span>
              </span>
              {activeChain.steps.map((step, idx) => (
                <React.Fragment key={idx}>
                  <div
                    onClick={() => {
                      setSelectedNodeId(step.node_id);
                      setSelectedEdge(null);
                    }}
                    className={`px-2 py-0.5 rounded cursor-pointer border flex items-center space-x-1 shrink-0 ${
                      selectedNodeId === step.node_id
                        ? 'bg-amber-500 text-black font-black border-amber-400 shadow-[0_0_8px_rgba(245,158,11,0.6)]'
                        : 'bg-slate-900/80 text-slate-300 hover:text-white border-slate-700'
                    }`}
                  >
                    <span className="font-bold">{step.node_name.split('(')[0]}</span>
                    <span className={`font-black ${selectedNodeId === step.node_id ? 'text-black' : 'text-red-400'}`}>
                      {step.risk_score}
                    </span>
                  </div>
                  {idx < activeChain.steps.length - 1 && (
                    <ChevronRight className="w-3 h-3 text-slate-500 shrink-0" />
                  )}
                </React.Fragment>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Deep Explainability Inspector (4 cols) */}
        <div className="lg:col-span-4 flex flex-col space-y-3">
          {/* Node Inspector Drawer (Section 11) */}
          {selectedNode && (
            <div className="hud-card p-4 rounded-lg border-l-4 border-l-cyan-400 space-y-3 flex-1 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <div className="flex items-center space-x-1.5">
                    <span className="p-1 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/40">
                      <Activity className="w-3.5 h-3.5" />
                    </span>
                    <span className="font-black text-white text-xs">{selectedNode.label}</span>
                  </div>
                  <span className="px-1.5 py-0.2 rounded bg-slate-800 text-cyan-300 font-mono text-[9px] uppercase font-bold">
                    {selectedNode.category}
                  </span>
                </div>

                {/* Risk Telemetry Metric Bar */}
                <div className="grid grid-cols-2 gap-2 mt-3 text-[11px]">
                  <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400 uppercase font-bold">CURRENT RISK</div>
                    <div className="text-base font-black text-amber-400 mt-0.5">
                      {selectedNode.current_risk} <span className="text-[10px] text-slate-400 font-normal">/ 100</span>
                    </div>
                  </div>
                  <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400 uppercase font-bold">PREDICTED (+60m)</div>
                    <div className="text-base font-black text-red-400 mt-0.5">
                      {selectedNode.predicted_risk} <span className="text-[10px] text-slate-400 font-normal">/ 100</span>
                    </div>
                  </div>
                </div>

                {/* Trigger & Impact Mechanism */}
                <div className="mt-3 space-y-2 text-[11px]">
                  <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800/80 space-y-1">
                    <div className="text-[10px] text-cyan-400 font-bold uppercase flex items-center space-x-1">
                      <ChevronRight className="w-3 h-3 text-cyan-400" />
                      <span>TRIGGERED BY:</span>
                    </div>
                    <div className="text-slate-200 font-sans leading-relaxed text-[11px]">
                      {selectedNode.triggered_by || 'Primary flood inundation and basin runoff saturation.'}
                    </div>
                  </div>

                  <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800/80 space-y-1">
                    <div className="text-[10px] text-amber-400 font-bold uppercase flex items-center space-x-1">
                      <ChevronRight className="w-3 h-3 text-amber-400" />
                      <span>SYSTEMIC DOWNSTREAM IMPACT:</span>
                    </div>
                    <div className="text-slate-200 font-sans leading-relaxed text-[11px]">
                      {selectedNode.impact_description || 'Compounding failure across connected service infrastructure.'}
                    </div>
                  </div>
                </div>

                {/* Grounding Evidence Signals */}
                {selectedNode.evidence_signals.length > 0 && (
                  <div className="mt-3">
                    <div className="text-[10px] text-slate-400 uppercase font-bold mb-1.5 flex items-center justify-between">
                      <span>GROUNDING EVIDENCE SIGNALS</span>
                      <span className="text-emerald-400 font-bold">CONFIDENCE: {selectedNode.confidence}%</span>
                    </div>
                    <div className="space-y-1">
                      {selectedNode.evidence_signals.map((sig, idx) => (
                        <div key={idx} className="flex items-start space-x-1.5 bg-slate-950 p-1.5 rounded border border-slate-800/60 text-[10px]">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0 mt-0.5" />
                          <span className="text-slate-300 font-sans">{sig}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
                <span>Model Confidence: {selectedNode.confidence}%</span>
                <span className="text-cyan-400 font-bold">MODEL ESTIMATE</span>
              </div>
            </div>
          )}

          {/* Edge Inspector Drawer (Section 12) */}
          {selectedEdge && (
            <div className="hud-card p-4 rounded-lg border-l-4 border-l-amber-500 space-y-3 flex-1 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <div className="flex items-center space-x-1.5 text-amber-400 font-bold">
                    <Zap className="w-4 h-4" />
                    <span>CAUSAL DEPENDENCY LINK</span>
                  </div>
                  <span className="px-1.5 py-0.2 rounded bg-amber-950 text-amber-300 font-mono text-[9px] uppercase font-bold">
                    {selectedEdge.relationship}
                  </span>
                </div>

                <div className="mt-3 p-2.5 rounded bg-slate-900 border border-slate-800 text-center">
                  <div className="flex items-center justify-center space-x-2 text-xs font-black text-white">
                    <span className="text-cyan-300">{selectedEdge.source.replace('_', ' ').toUpperCase()}</span>
                    <ArrowRight className="w-4 h-4 text-amber-400" />
                    <span className="text-red-300">{selectedEdge.target.replace('_', ' ').toUpperCase()}</span>
                  </div>
                  <div className="text-[10px] text-amber-300 mt-1 font-bold">
                    RELATIONSHIP: {selectedEdge.relationship.toUpperCase()}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 mt-3 text-[11px]">
                  <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400 uppercase font-bold">EDGE IMPACT</div>
                    <div className="text-base font-black text-amber-400 mt-0.5">
                      {selectedEdge.impact} <span className="text-[10px] text-slate-400 font-normal">/ 100</span>
                    </div>
                  </div>
                  <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400 uppercase font-bold">CONFIDENCE</div>
                    <div className="text-base font-black text-emerald-400 mt-0.5">
                      {selectedEdge.confidence}%
                    </div>
                  </div>
                </div>

                <div className="mt-3 bg-slate-900/60 p-2.5 rounded border border-slate-800/80 space-y-1">
                  <div className="text-[10px] text-cyan-400 font-bold uppercase">PHYSICAL & OPERATIONAL REASONING:</div>
                  <div className="text-slate-200 font-sans leading-relaxed text-[11px]">
                    {selectedEdge.reason}
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800 text-[10px] text-slate-400">
                Deterministic Multi-Sector Propagation Estimate
              </div>
            </div>
          )}

          {/* Cascade Score Contributor Breakdown (Section 13) */}
          <div className="hud-card p-3.5 rounded-lg border border-slate-800 space-y-2">
            <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
              <span className="font-extrabold text-white text-xs">
                CASCADING RISK SCORE BREAKDOWN
              </span>
              <span className="text-amber-400 font-black text-sm">
                {graphData.cascading_risk} / 100
              </span>
            </div>

            <div className="text-[10px] text-slate-400">
              Why is this score elevated? Additive risk contributor attribution:
            </div>

            <div className="space-y-1.5 text-[11px] pt-1">
              {graphData.contributors.map((contrib, idx) => (
                <div key={idx} className="flex items-center justify-between bg-slate-900/70 px-2 py-1 rounded border border-slate-800">
                  <span className="text-slate-200 font-bold">{contrib.name}</span>
                  <span className="text-amber-400 font-mono font-black">+{contrib.points} pts</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
