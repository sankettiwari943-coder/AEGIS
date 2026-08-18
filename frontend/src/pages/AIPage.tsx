import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  OrchestratorStructuredResponse,
  CommandBriefingResponse,
  MainNavMode,
  ToolCallRecord
} from '../types';
import { RAGInsightPanel } from '../components/rag/RAGInsightPanel';
import { DataSourceBadge } from '../components/common/DataSourceBadge';
import { ConfidenceBadge } from '../components/common/ConfidenceBadge';
import {
  Sparkles,
  Send,
  Cpu,
  FileCheck,
  ShieldAlert,
  Sliders,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Clock,
  Layers,
  Terminal,
  Zap,
  Info,
  BookOpen
} from 'lucide-react';

interface AIPageProps {
  onNavigate?: (mode: MainNavMode, zoneId?: string) => void;
  initialZoneId?: string;
}


export const AIPage: React.FC<AIPageProps> = ({ onNavigate, initialZoneId = 'zone-7' }) => {
  const [queryInput, setQueryInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<OrchestratorStructuredResponse | null>(null);
  const [briefing, setBriefing] = useState<CommandBriefingResponse | null>(null);
  const [generatingBriefing, setGeneratingBriefing] = useState<boolean>(false);
  const [availableTools, setAvailableTools] = useState<any[]>([]);

  // Default initial query on mount
  useEffect(() => {
    handleQuery("What should we do right now?");
    loadTools();
  }, []);

  const loadTools = async () => {
    try {
      const tools = await api.getOrchestratorTools();
      setAvailableTools(tools);
    } catch (err) {
      console.error('Failed to fetch tools:', err);
    }
  };

  const handleQuery = async (text: string) => {
    if (!text.trim()) return;
    try {
      setLoading(true);
      const res = await api.orchestratorChat(text, 'ai-page-session', initialZoneId, 'AI');
      setResponse(res);
    } catch (err) {
      console.error('AI query failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateBriefing = async () => {
    try {
      setGeneratingBriefing(true);
      const b = await api.getCommandBriefing('ai-page-session');
      setBriefing(b);
    } catch (err) {
      console.error('Failed to generate briefing:', err);
    } finally {
      setGeneratingBriefing(false);
    }
  };

  const quickPrompts = [
    "What should we do right now?",
    "Why is Zone 7 critical?",
    "Which team should respond to Zone 7?",
    "What happens if we do nothing in Zone 7?",
    "What has AEGIS learned?",
    "How accurate have our predictions been?"
  ];

  return (
    <div className="w-full h-full bg-[#060a12] text-slate-200 overflow-y-auto p-4 sm:p-6 font-mono select-none space-y-6">
      
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-purple-950/80 via-slate-900/90 to-blue-950/80 border border-purple-500/40 rounded-2xl p-4 sm:p-5 flex flex-wrap items-center justify-between shadow-xl">
        <div className="flex items-center space-x-3.5">
          <div className="p-2.5 rounded-xl bg-purple-500/20 text-purple-300 border border-purple-500/50 shadow-[0_0_20px_rgba(168,85,247,0.35)]">
            <Sparkles className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base sm:text-lg font-black text-white tracking-wider">
                AEGIS AI DISASTER ORCHESTRATOR
              </h1>
              <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/40 text-[10px] font-black">
                GROUNDED REASONING
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5 font-sans">
              Autonomous coordination and synthesis layer above deterministic AEGIS engines.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3 mt-3 sm:mt-0">
          <button
            onClick={handleGenerateBriefing}
            disabled={generatingBriefing}
            className="px-3.5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-black text-xs shadow-[0_0_15px_rgba(168,85,247,0.4)] disabled:opacity-40 flex items-center space-x-1.5 transition-all"
          >
            <Zap className="w-3.5 h-3.5" />
            <span>{generatingBriefing ? 'GENERATING BRIEFING...' : 'GENERATE COMMAND BRIEFING'}</span>
          </button>
        </div>
      </div>

      {/* Command Briefing Modal / Banner */}
      {briefing && (
        <div className="hud-card p-5 rounded-2xl border border-purple-500/60 bg-gradient-to-b from-purple-950/30 to-slate-950/90 space-y-3 shadow-2xl animate-in fade-in">
          <div className="flex justify-between items-center border-b border-purple-500/30 pb-2">
            <div className="flex items-center space-x-2 text-purple-300 font-bold text-xs">
              <Zap className="w-4 h-4 text-purple-400" />
              <span>{briefing.title.toUpperCase()}</span>
            </div>
            <span className="text-[10px] text-slate-400">Generated: {briefing.timestamp}</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-500 font-bold uppercase block">PRIMARY ACTION</span>
              <div className="font-bold text-white text-sm">{briefing.recommended_mission}</div>
              <div className="text-[10px] text-emerald-400 font-sans">Mission Score: {briefing.mission_score}/100</div>
            </div>

            <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-500 font-bold uppercase block">CRITICAL SECTOR</span>
              <div className="font-bold text-amber-300 text-sm">{briefing.top_priority_zone}</div>
              <div className="text-[10px] text-red-400 font-sans">Risk: {briefing.current_risk_score}/100 • {briefing.predicted_escalation}</div>
            </div>

            <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-500 font-bold uppercase block">SIMULATION OUTCOME</span>
              <div className="font-bold text-cyan-300 text-sm leading-snug">{briefing.simulation_summary}</div>
              <div className="text-[10px] text-slate-400 font-sans">Confidence: {briefing.confidence_percent}%</div>
            </div>
          </div>

          <p className="text-xs font-sans text-slate-300 leading-relaxed pt-1">
            {briefing.situation_summary}
          </p>
        </div>
      )}

      {/* Main Orchestrator Workspace Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Interactive Chat & Response Synthesis (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          
          {/* Quick Prompts */}
          <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 scrollbar-thin">
            {quickPrompts.map((p, idx) => (
              <button
                key={idx}
                onClick={() => handleQuery(p)}
                className="px-2.5 py-1.5 rounded-lg bg-slate-950 hover:bg-purple-950/50 text-slate-300 hover:text-purple-200 border border-slate-800 hover:border-purple-500/50 text-[10px] font-bold shrink-0 transition-all"
              >
                {p}
              </button>
            ))}
          </div>

          {/* Chat Query Input */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleQuery(queryInput);
              setQueryInput('');
            }}
            className="flex items-center space-x-2"
          >
            <input
              type="text"
              value={queryInput}
              onChange={(e) => setQueryInput(e.target.value)}
              placeholder="Ask AEGIS Disaster Intelligence..."
              className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-400 font-mono"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-black text-xs shadow-[0_0_15px_rgba(168,85,247,0.4)] disabled:opacity-40 flex items-center space-x-1.5 transition-all"
            >
              <span>{loading ? 'ANALYZING...' : 'ASK'}</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>

          {/* Structured Response Card */}
          {response && (
            <div className="hud-card p-5 rounded-2xl border border-slate-800/90 space-y-4 bg-slate-950/80">
              
              <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                <div className="flex items-center space-x-2">
                  <Cpu className="w-4 h-4 text-purple-400" />
                  <span className="text-xs font-bold text-white">ORCHESTRATOR SYNTHESIS</span>
                </div>
                <div className="flex items-center space-x-2 text-[10px]">
                  <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-500/40 font-bold">
                    CONFIDENCE: {Math.round(response.confidence_score * 100)}%
                  </span>
                  <span className="text-slate-500">{response.safety_label}</span>
                </div>
              </div>

              {/* Direct Answer */}
              <div className="space-y-1">
                <span className="text-[10px] text-purple-400 font-bold uppercase tracking-wider block">
                  DIRECT ANSWER
                </span>
                <p className="text-sm font-sans text-white leading-relaxed font-bold">
                  {response.direct_answer || response.answer}
                </p>
              </div>

              {/* Why Rationale */}
              {response.why_rationale && response.why_rationale.length > 0 && (
                <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800/80 space-y-1.5">
                  <span className="text-[10px] text-amber-400 font-bold uppercase tracking-wider block">
                    WHY RATIONALE
                  </span>
                  <ul className="space-y-1 text-xs font-sans text-slate-300">
                    {response.why_rationale.map((r, i) => (
                      <li key={i} className="flex items-start space-x-2">
                        <span className="text-amber-400 font-bold">•</span>
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommendations */}
              {response.recommendations && response.recommendations.length > 0 && (
                <div className="p-3 bg-cyan-950/20 rounded-xl border border-cyan-500/30 space-y-1.5">
                  <span className="text-[10px] text-cyan-400 font-bold uppercase tracking-wider block">
                    RECOMMENDED ACTIONS
                  </span>
                  <ul className="space-y-1 text-xs font-sans text-slate-300">
                    {response.recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start space-x-2">
                        <span className="text-cyan-400 font-bold">&rarr;</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Grounded Live Facts */}
              {response.facts && response.facts.length > 0 && (
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between items-center text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                    <span>GROUNDED ENGINE FACTS</span>
                    <DataSourceBadge sourceType="SENSOR" size="sm" />
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {(response.live_facts && response.live_facts.length > 0 ? response.live_facts : response.facts).map((f, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 rounded bg-cyan-950/40 text-cyan-200 border border-cyan-500/30 text-[10px]"
                      >
                        {f}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Retrieved SOP Guidance (RAG) */}
              {(response.retrieved_guidance || (response.rag_sources && response.rag_sources.length > 0)) && (
                <div className="p-3 bg-indigo-950/20 rounded-xl border border-indigo-500/40 space-y-1.5 text-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] text-indigo-300 font-bold uppercase tracking-wider flex items-center space-x-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                      <span>RETRIEVED DOCTRINAL SOP GUIDANCE</span>
                    </span>
                    <DataSourceBadge sourceType="RAG" size="sm" />
                  </div>
                  <ul className="space-y-1 text-[11px] font-sans text-slate-300">
                    {(response.retrieved_guidance || [
                      "[SOP-FL-001] Urban Riverine Flood: Proactive evacuation mandatory before arterial routes submerge below 30cm passability."
                    ]).map((g, i) => (
                      <li key={i} className="flex items-start space-x-1.5">
                        <span className="text-indigo-400 font-bold">•</span>
                        <span>{g}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Deep Links */}
              {response.deep_links && response.deep_links.length > 0 && (
                <div className="pt-2 border-t border-slate-800 flex flex-wrap items-center gap-2">
                  <span className="text-[10px] text-slate-500 font-bold uppercase mr-1">ACTION HOOKS:</span>
                  {response.deep_links.map((dl, i) => (
                    <button
                      key={i}
                      onClick={() => onNavigate && onNavigate(dl.target_mode as MainNavMode, dl.target_zone_id)}
                      className="px-3 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500 text-cyan-300 hover:text-black border border-cyan-500/40 text-[10px] font-black flex items-center space-x-1 transition-all"
                    >
                      <span>{dl.label}</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  ))}
                </div>
              )}

            </div>
          )}

        </div>

        {/* Right Column: Live Engine Tool Calls & Execution Trace (5 cols) */}
        <div className="lg:col-span-5 hud-card p-5 rounded-2xl border border-slate-800 space-y-4 bg-slate-950/70 flex flex-col justify-between">
          
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs">
              <Terminal className="w-4 h-4 text-cyan-400" />
              <span>LIVE TOOL EXECUTION TRACE</span>
            </div>
            <span className="text-[10px] text-slate-400">{response?.tool_calls?.length || 0} Tools Called</span>
          </div>

          {/* Tools Called Stream */}
          <div className="space-y-2.5 overflow-y-auto max-h-[380px] pr-1 scrollbar-thin">
            {response?.tool_calls && response.tool_calls.length > 0 ? (
              response.tool_calls.map((tc, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-slate-900/80 rounded-xl border border-slate-800 space-y-1.5 text-xs font-mono"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-cyan-300 font-bold text-xs">{tc.tool_name}()</span>
                    <span className="px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-400 border border-emerald-500/30 text-[9px] font-bold">
                      200 OK
                    </span>
                  </div>
                  {tc.output_summary && (
                    <div className="text-[10px] text-slate-300 font-sans bg-slate-950/60 p-2 rounded border border-slate-800/80">
                      {tc.output_summary}
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="p-4 text-center text-xs text-slate-500">
                Tool call trace will appear here upon executing queries.
              </div>
            )}
          </div>

          {/* Available AEGIS Engine Tools */}
          <div className="pt-3 border-t border-slate-800 space-y-2">
            <span className="text-[10px] text-slate-500 font-bold uppercase block">
              CONNECTED AEGIS ENGINE TOOLS ({availableTools.length})
            </span>
            <div className="flex flex-wrap gap-1.5">
              {availableTools.map((t, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded bg-slate-900/90 text-slate-400 border border-slate-800 text-[9px]"
                  title={t.description}
                >
                  {t.name}
                </span>
              ))}
            </div>
          </div>

        </div>

      </div>

      {/* Embedded Priority 2: RAG Emergency SOP Knowledge Search Viewer */}
      <RAGInsightPanel />

    </div>
  );
};

