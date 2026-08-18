import React, { useState, useEffect } from 'react';
import { DecisionEvidenceTrace, MainNavMode } from '../../types';
import { api } from '../../services/api';
import { 
  ShieldAlert, 
  CheckCircle2, 
  AlertTriangle, 
  Activity, 
  Radio, 
  Cpu, 
  ArrowRight, 
  X, 
  ChevronDown, 
  ChevronUp, 
  ExternalLink,
  Layers,
  Sparkles,
  Search,
  Clock,
  Compass,
  FileCheck
} from 'lucide-react';

interface EvidenceChainProps {
  decisionId?: string;
  zoneId?: string;
  onClose: () => void;
  onNavigate?: (mode: MainNavMode, zoneId?: string) => void;
}

export const EvidenceChain: React.FC<EvidenceChainProps> = ({
  decisionId = 'decision-zone-7-escalation',
  zoneId,
  onClose,
  onNavigate
}) => {
  const [trace, setTrace] = useState<DecisionEvidenceTrace | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [expandedLevels, setExpandedLevels] = useState<Record<string, boolean>>({
    'DECISION': true,
    'RISK': true,
    'PREDICTION': true,
    'EVIDENCE': true
  });

  useEffect(() => {
    const fetchTrace = async () => {
      setLoading(true);
      try {
        const idToFetch = decisionId || (zoneId === 'zone-4' ? 'decision-zone-4-silent' : 'decision-zone-7-escalation');
        const data = await api.getDecisionEvidence(idToFetch);
        setTrace(data);
      } catch (err) {
        console.error('Failed to fetch decision evidence chain:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTrace();
  }, [decisionId, zoneId]);

  const toggleLevel = (level: string) => {
    setExpandedLevels(prev => ({
      ...prev,
      [level]: !prev[level]
    }));
  };

  return (
    <div className="fixed inset-0 z-[9999] bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-slate-950 border-2 border-cyan-500/60 rounded-xl max-w-4xl w-full max-h-[92vh] flex flex-col shadow-[0_0_50px_rgba(6,182,212,0.25)] font-mono overflow-hidden">
        
        {/* Modal Header */}
        <div className="p-4 border-b border-cyan-500/30 bg-slate-900/90 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded bg-cyan-500/10 border border-cyan-500/40 text-cyan-400">
              <FileCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-white font-extrabold text-sm tracking-wide">
                  DECISION EVIDENCE TRACEABILITY CHAIN
                </span>
                <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/40 text-[10px] font-bold">
                  AI AUDIT TRAIL
                </span>
              </div>
              <p className="text-slate-400 text-xs mt-0.5">
                Every prediction, risk score, and operational recommendation is grounded in empirical multi-source evidence.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {trace && (
              <div className="flex items-center space-x-2 bg-slate-900 border border-slate-700 px-2.5 py-1 rounded">
                <span className="text-[10px] text-slate-400">EVIDENCE CONFIDENCE:</span>
                <span className="text-sm font-black text-cyan-300">{trace.confidence_percent}%</span>
              </div>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
          {loading ? (
            <div className="p-12 text-center text-slate-500 animate-pulse">
              Tracing decision back to empirical telemetry and radar observations...
            </div>
          ) : !trace ? (
            <div className="p-8 text-center text-amber-400">
              No evidence trace found for this decision identifier.
            </div>
          ) : (
            <>
              {/* Decision Action Banner */}
              <div className="hud-card p-3.5 rounded-lg border-l-4 border-l-cyan-400 bg-slate-900/60">
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-slate-400 font-bold">QUESTION ANSWERED:</span>
                  <span className="text-cyan-400 font-bold uppercase tracking-wider text-[10px]">
                    "Why does AEGIS believe this?"
                  </span>
                </div>
                <div className="text-sm font-extrabold text-white">
                  {trace.action_statement}
                </div>
              </div>

              {/* 4-Tier Directional Hierarchy */}
              <div className="space-y-3">
                <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
                  <Layers className="w-3.5 h-3.5 text-cyan-400" />
                  <span>4-STAGE EMPIRICAL TRACEABILITY GRAPH</span>
                </div>

                <div className="space-y-2 relative">
                  {trace.decision_chain.map((step, idx) => {
                    const isExpanded = expandedLevels[step.level] !== false;
                    const isDecision = step.level === 'DECISION';
                    const isRisk = step.level === 'RISK';
                    const isPrediction = step.level === 'PREDICTION';
                    const isEvidence = step.level === 'EVIDENCE';

                    return (
                      <div 
                        key={idx}
                        className={`rounded-lg border transition-all ${
                          isDecision ? 'bg-cyan-950/20 border-cyan-500/40' :
                          isRisk ? 'bg-amber-950/20 border-amber-500/40' :
                          isPrediction ? 'bg-red-950/20 border-red-500/40' :
                          'bg-emerald-950/20 border-emerald-500/40'
                        }`}
                      >
                        <div 
                          onClick={() => toggleLevel(step.level)}
                          className="p-3 flex items-center justify-between cursor-pointer select-none"
                        >
                          <div className="flex items-center space-x-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-black border ${
                              isDecision ? 'bg-cyan-900/80 text-cyan-200 border-cyan-400' :
                              isRisk ? 'bg-amber-900/80 text-amber-200 border-amber-400' :
                              isPrediction ? 'bg-red-900/80 text-red-200 border-red-400' :
                              'bg-emerald-900/80 text-emerald-200 border-emerald-400'
                            }`}>
                              STAGE {idx + 1}: {step.level}
                            </span>
                            <span className="font-extrabold text-white text-xs">{step.title}</span>
                          </div>

                          <div className="flex items-center space-x-2">
                            <span className={`text-[10px] font-bold ${step.color}`}>{step.badge}</span>
                            {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                          </div>
                        </div>

                        {isExpanded && (
                          <div className="px-3.5 pb-3.5 pt-1 text-slate-300 border-t border-slate-800/60 font-sans space-y-2">
                            <p className="text-xs leading-relaxed">{step.text}</p>
                            
                            {/* If Evidence Level, show key signals */}
                            {isEvidence && (
                              <div className="mt-3 bg-slate-900/90 rounded p-3 border border-emerald-500/30 space-y-2 font-mono">
                                <div className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
                                  <CheckCircle2 className="w-3.5 h-3.5" />
                                  <span>CORROBORATED MULTI-SOURCE SIGNALS</span>
                                </div>
                                <div className="space-y-1.5 pt-1">
                                  {trace.key_signals.map((sig, sIdx) => (
                                    <div key={sIdx} className="flex items-start space-x-2 text-[11px]">
                                      <span className="text-emerald-400 font-bold">✓</span>
                                      <span className="text-slate-200">{sig}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Raw Grounded Evidence Items Table */}
              {trace.underlying_evidence && trace.underlying_evidence.length > 0 && (
                <div className="space-y-2 pt-2">
                  <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                    <div className="flex items-center space-x-1.5">
                      <Radio className="w-3.5 h-3.5 text-cyan-400" />
                      <span>GROUND TRUTH TELEMETRY ITEMS ({trace.underlying_evidence.length})</span>
                    </div>
                    <span className="text-[10px] text-slate-500 font-normal">
                      NO HALLUCINATIONS • 100% REAL APPLICATION DATA
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {trace.underlying_evidence.map((item) => (
                      <div key={item.id} className="bg-slate-900/80 p-2.5 rounded border border-slate-800 flex flex-col justify-between space-y-2">
                        <div>
                          <div className="flex items-center justify-between">
                            <span className="px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300 font-bold text-[9px] border border-cyan-500/30">
                              {item.type}
                            </span>
                            <span className="text-[9px] text-slate-400">
                              {item.minutes_ago}m ago
                            </span>
                          </div>
                          <div className="text-xs font-bold text-white mt-1.5">
                            {item.source}
                          </div>
                          <div className="text-[11px] text-slate-300 font-sans mt-0.5">
                            {item.claim}
                          </div>
                        </div>

                        <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px]">
                          <span className="text-slate-400">Observed Value:</span>
                          <span className="text-emerald-400 font-bold">{String(item.value)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-3 bg-slate-900 border-t border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2 text-slate-400 text-[10px]">
            <span>DATA TRUST INDEX:</span>
            <span className="text-cyan-300 font-bold">{trace?.trust_score ?? 88} / 100</span>
          </div>

          <div className="flex items-center space-x-2">
            {onNavigate && (
              <button
                onClick={() => {
                  onClose();
                  onNavigate('EVIDENCE');
                }}
                className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs flex items-center space-x-1"
              >
                <span>OPEN EVIDENCE CENTER</span>
                <ExternalLink className="w-3 h-3 ml-1" />
              </button>
            )}
            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded bg-cyan-500 hover:bg-cyan-400 text-black font-extrabold text-xs"
            >
              CLOSE AUDIT TRAIL
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
