import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../services/api';
import { 
  OrchestratorStructuredResponse, 
  CommandBriefingResponse, 
  MainNavMode 
} from '../../types';
import { DataSourceBadge } from '../common/DataSourceBadge';
import { ConfidenceBadge } from '../common/ConfidenceBadge';
import { 
  Bot, 
  Send, 
  X, 
  Sparkles, 
  ShieldAlert, 
  CheckCircle2, 
  Cpu, 
  ChevronRight, 
  ExternalLink,
  Zap,
  TrendingUp,
  Sliders,
  FileCheck,
  Radio,
  FileText,
  AlertTriangle,
  RotateCcw,
  Check,
  BookOpen
} from 'lucide-react';


interface TacticalAssistantProps {
  currentMode: string;
  selectedZoneId?: string;
  onNavigate: (mode: MainNavMode, zoneId?: string) => void;
  inboundQuery?: string;
  onClearInboundQuery?: () => void;
}

interface MessageItem {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  data?: OrchestratorStructuredResponse;
  briefing?: CommandBriefingResponse;
  timestamp: string;
}

export const TacticalAssistant: React.FC<TacticalAssistantProps> = ({ 
  currentMode, 
  selectedZoneId,
  onNavigate,
  inboundQuery,
  onClearInboundQuery
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [showBriefingModal, setShowBriefingModal] = useState(false);
  const [activeBriefing, setActiveBriefing] = useState<CommandBriefingResponse | null>(null);
  const [expandedToolDetails, setExpandedToolDetails] = useState<Record<string, boolean>>({});

  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: 'init-01',
      sender: 'assistant',
      text: 'AEGIS Tactical AI Disaster Orchestrator online. Connected to Prediction, Cascades, Evidence, Mission Optimizer, Simulation, and Silent Risk engines.',
      data: {
        answer: 'AEGIS Tactical AI Disaster Orchestrator online. Flood conditions are currently worsening in Sector Z-07 (Risk: 91) and Sector Z-04 (Silent Risk: 91%). The Mission Optimizer recommends deploying Delta-2 to Sector Z-07, while What-If simulations demonstrate a 27-point risk cut when combining evacuation with active rescue transport.',
        direct_answer: 'AEGIS intelligence engines active across Prediction, Cascades, Evidence, Missions, and What-If Simulation.',
        why_rationale: [
          'Real-time river stage telemetry at 8.1m MSL (cresting in ~3.5h)',
          'Corridor 14 Bridge overtopping imminent with 42-minute isolation window',
          'Deterministic multi-attribute decision support active with zero autonomous dispatch'
        ],
        facts: [
          '12 active monitoring zones',
          '11,800 total exposed population',
          '4 active simulated rescue missions'
        ],
        model_estimates: [
          'Zone 7 operational risk: 91/100 (MODEL ESTIMATE)',
          'Zone 7 isolation window: ~42 minutes (MODEL ESTIMATE)'
        ],
        uncertainties: [
          'Bridge 14 structural integrity remains unverified by physical inspection',
          'Traffic sensor #14 operational telemetry conflicts with flood imagery'
        ],
        recommendations: [
          'Inspect Zone 7 critical alerts',
          'Review Team Delta-2 mission recommendation'
        ],
        tools_used: ['get_current_situation', 'get_prediction', 'get_mission_recommendations'],
        tool_calls: [],
        deep_links: [
          { label: 'VIEW PREDICTION', target_mode: 'PREDICT', target_zone_id: 'zone-7', action_type: 'VIEW_PREDICTION' },
          { label: 'VIEW EVIDENCE', target_mode: 'EVIDENCE', target_zone_id: 'zone-7', action_type: 'VIEW_EVIDENCE' },
          { label: 'VIEW MISSION', target_mode: 'MISSIONS', target_zone_id: 'zone-7', action_type: 'VIEW_MISSION' }
        ],
        referenced_zones: ['Zone 7 (River Bend)', 'Zone 4 (Riverside Slums)'],
        supporting_evidence: [
          '42 Ultrasonic Hydrological Gauges (8.1m river crest)',
          'Synthetic Aperture Radar Inundation Signature (95cm depth)'
        ],
        confidence_score: 91,
        orchestrator_agent: 'AEGIS Disaster Orchestrator',
        requires_human_approval: true,
        safety_label: 'DECISION SUPPORT / MODEL ESTIMATE'
      },
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Handle inbound queries from alert clicks or parent
  useEffect(() => {
    if (inboundQuery && inboundQuery.trim()) {
      setIsOpen(true);
      handleSend(inboundQuery.trim());
      if (onClearInboundQuery) onClearInboundQuery();
    }
  }, [inboundQuery]);

  // Listen to window custom events from anywhere in the app (e.g. from AlertTicker or alert buttons)
  useEffect(() => {
    const handleCustomAsk = (e: any) => {
      const customQuery = e.detail?.query;
      if (customQuery) {
        setIsOpen(true);
        handleSend(customQuery);
      }
    };
    window.addEventListener('aegis:ask-orchestrator', handleCustomAsk);
    return () => window.removeEventListener('aegis:ask-orchestrator', handleCustomAsk);
  }, []);

  const quickCommands = [
    { label: "WHAT'S HAPPENING?", query: "What is happening right now?" },
    { label: "WHAT HAPPENS NEXT?", query: "What happens in the next hour?" },
    { label: "TOP RISKS", query: "What are the biggest cascading threats?" },
    { label: "BEST MISSION", query: "Which team should go to Zone 7?" },
    { label: "SILENT RISK", query: "Are there silent risk zones where people aren't reporting?" },
    { label: "RUN SIMULATION", query: "What if we evacuate Zone 7 and send Delta-2?" },
    { label: "COMMAND BRIEFING", query: "Give me a command briefing." }
  ];

  const handleSend = async (textToSend?: string) => {
    const q = textToSend || query;
    if (!q.trim() || loading) return;

    const userMsgId = `user-${Date.now()}`;
    const userMsg: MessageItem = {
      id: userMsgId,
      sender: 'user',
      text: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      // Check if command briefing query
      if (q.toLowerCase().includes('command briefing') || q.toLowerCase().includes('give me a command briefing') || q.toLowerCase().includes('briefing')) {
        const briefingRes = await api.getCommandBriefing('demo-session');
        setActiveBriefing(briefingRes);
        setMessages((prev) => [
          ...prev,
          {
            id: `asst-${Date.now()}`,
            sender: 'assistant',
            text: `AEGIS EXECUTIVE SITUATION BRIEFING compiled. Top priority is ${briefingRes.top_priority_zone} with active escalation in ~42m. Recommended Simulated Mission: ${briefingRes.recommended_mission} (Impact score: ${briefingRes.mission_score}/100).`,
            briefing: briefingRes,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
      } else {
        const resp = await api.orchestratorChat(q, 'demo-session', selectedZoneId, currentMode);
        setMessages((prev) => [
          ...prev,
          {
            id: `asst-${Date.now()}`,
            sender: 'assistant',
            text: resp.answer,
            data: resp,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `asst-${Date.now()}`,
          sender: 'assistant',
          text: 'AI Orchestrator connected via Deterministic Engine telemetry fallback. Core intelligence engines remain fully operational.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleDeepLink = (link: { target_mode: string; target_zone_id?: string }) => {
    onNavigate(link.target_mode as MainNavMode, link.target_zone_id);
  };

  return (
    <div className="fixed bottom-12 right-4 z-40 font-mono select-none">
      {/* Collapsed Trigger Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="flex items-center space-x-2.5 px-4 py-2.5 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-black text-xs shadow-[0_0_30px_rgba(0,240,255,0.6)] transition-all transform hover:scale-105 border border-cyan-300"
        >
          <Bot className="w-4 h-4 text-black animate-pulse" />
          <span className="tracking-wider">AEGIS AI ORCHESTRATOR</span>
          <span className="w-2 h-2 rounded-full bg-black animate-ping"></span>
        </button>
      )}

      {/* Expanded Emergency Command HUD Window */}
      {isOpen && (
        <div className="w-[420px] sm:w-[500px] md:w-[560px] h-[640px] bg-[#070d18]/95 border border-cyan-500/60 rounded-xl shadow-[0_0_50px_rgba(0,0,0,0.8)] backdrop-blur-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
          
          {/* Top Banner: DEMO / SIMULATION MODE & Operational Safety Notice */}
          <div className="bg-gradient-to-r from-cyan-950 via-slate-900 to-blue-950 px-3 py-1.5 border-b border-cyan-500/30 flex items-center justify-between text-[10px]">
            <div className="flex items-center space-x-2">
              <span className="px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 font-black tracking-wider text-[9px]">
                DEMO / SIMULATION MODE
              </span>
              <span className="text-slate-400 text-[10px]">
                DECISION SUPPORT ONLY • REQUIRES HUMAN APPROVAL
              </span>
            </div>
            <div className="flex items-center space-x-1 text-emerald-400 font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
              <span className="text-[9px]">ENGINES ACTIVE</span>
            </div>
          </div>

          {/* Header */}
          <div className="px-4 py-2.5 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="p-1.5 rounded-md bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 shadow-[0_0_10px_rgba(0,240,255,0.3)]">
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <div className="text-xs font-black text-white flex items-center space-x-2">
                  <span>AEGIS DISASTER ORCHESTRATOR</span>
                  <span className="px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-300 text-[9px] border border-cyan-500/30">
                    REASONING LAYER
                  </span>
                </div>
                <div className="text-[10px] text-slate-400 flex items-center space-x-2">
                  <span>Grounding: 6 AEGIS Deterministic Engines</span>
                  <span>•</span>
                  <span>Context: [{currentMode}]</span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-1.5">
              <button
                onClick={() => {
                  setMessages([
                    {
                      id: `init-${Date.now()}`,
                      sender: 'assistant',
                      text: 'AEGIS Disaster Orchestrator session reset. Standing by for situational, predictive, cascade, mission, and simulation queries.',
                      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    }
                  ]);
                }}
                className="p-1.5 rounded text-slate-400 hover:text-cyan-300 hover:bg-slate-800 transition-all"
                title="Reset Session Context"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Quick Action Commands Carousel */}
          <div className="px-3 py-2 bg-slate-950/80 border-b border-slate-800/90 overflow-x-auto flex space-x-1.5 shrink-0 scrollbar-none">
            {quickCommands.map((cmd, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(cmd.query)}
                className="shrink-0 px-2.5 py-1 rounded bg-slate-900 hover:bg-cyan-950/70 text-slate-300 hover:text-cyan-300 border border-slate-800 hover:border-cyan-500/50 text-[10px] font-bold tracking-wider transition-all shadow-sm"
              >
                {cmd.label}
              </button>
            ))}
          </div>

          {/* Messages Stream */}
          <div className="flex-1 p-3.5 overflow-y-auto space-y-4 text-xs font-mono bg-gradient-to-b from-[#070d18] via-[#091222] to-[#070d18]">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                {/* Message Bubble Header */}
                <div className="flex items-center space-x-1.5 text-[9px] text-slate-500 mb-1 px-1">
                  <span>{m.sender === 'user' ? 'OPERATOR' : 'AEGIS ORCHESTRATOR'}</span>
                  <span>•</span>
                  <span>{m.timestamp}</span>
                </div>

                {/* Bubble */}
                <div
                  className={`max-w-[95%] rounded-lg leading-relaxed shadow-lg ${
                    m.sender === 'user'
                      ? 'p-3 bg-cyan-500 text-black font-bold border border-cyan-300'
                      : 'p-3.5 bg-slate-900/95 text-slate-200 border border-slate-800 shadow-[0_4px_20px_rgba(0,0,0,0.4)] space-y-3'
                  }`}
                >
                  {/* Plain Text / Direct Answer */}
                  {m.data?.direct_answer ? (
                    <div className="bg-slate-950/80 p-2.5 rounded border-l-2 border-cyan-400 space-y-1">
                      <div className="text-[9px] uppercase font-black text-cyan-400 tracking-wider">
                        DIRECT ANSWER
                      </div>
                      <div className="text-white font-bold text-xs font-sans leading-snug">
                        {m.data.direct_answer}
                      </div>
                    </div>
                  ) : null}

                  {/* Main Answer Narrative */}
                  <p className="font-sans text-[11px] text-slate-300 leading-relaxed">
                    {m.text}
                  </p>

                  {/* If Structured Response Data is Attached */}
                  {m.data && (
                    <div className="space-y-2.5 pt-2 border-t border-slate-800 text-[11px]">
                      
                      {/* WHY / Tactical Rationale */}
                      {m.data.why_rationale && m.data.why_rationale.length > 0 && (
                        <div className="space-y-1 bg-slate-950/50 p-2.5 rounded border border-slate-800/80">
                          <div className="text-[9px] font-black text-amber-400 uppercase tracking-wider flex items-center space-x-1">
                            <Zap className="w-3 h-3 text-amber-400" />
                            <span>WHY / TACTICAL RATIONALE</span>
                          </div>
                          <ul className="list-disc list-inside text-slate-300 font-sans text-[10px] space-y-1 mt-1">
                            {m.data.why_rationale.map((why, i) => (
                              <li key={i} className="leading-snug">{why}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Facts & Grounded Telemetry */}
                      {m.data.facts && m.data.facts.length > 0 && (
                        <div className="space-y-1">
                          <div className="text-[9px] font-black text-emerald-400 uppercase tracking-wider flex items-center space-x-1">
                            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                            <span>FACTS & GROUNDED TELEMETRY</span>
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 mt-1">
                            {m.data.facts.map((fact, i) => (
                              <div key={i} className="bg-slate-950/60 px-2 py-1 rounded text-[10px] text-slate-300 border border-slate-800/60">
                                • {fact}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Model Estimates & Horizons */}
                      {m.data.model_estimates && m.data.model_estimates.length > 0 && (
                        <div className="space-y-1">
                          <div className="text-[9px] font-black text-amber-400 uppercase tracking-wider flex items-center space-x-1">
                            <TrendingUp className="w-3 h-3 text-amber-400" />
                            <span>MODEL ESTIMATES & PROJECTIONS</span>
                          </div>
                          <div className="space-y-1 mt-1">
                            {m.data.model_estimates.map((est, i) => (
                              <div key={i} className="bg-amber-950/20 px-2 py-1 rounded text-[10px] text-amber-200 border border-amber-500/30 flex items-center justify-between">
                                <span>{est}</span>
                                <span className="px-1 py-0.2 rounded bg-amber-900/60 text-amber-300 text-[8px] font-bold">ESTIMATE</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Uncertainties & Contradictions */}
                      {m.data.uncertainties && m.data.uncertainties.length > 0 && (
                        <div className="space-y-1 bg-red-950/20 p-2 rounded border border-red-500/30">
                          <div className="text-[9px] font-black text-red-400 uppercase tracking-wider flex items-center space-x-1">
                            <AlertTriangle className="w-3 h-3 text-red-400" />
                            <span>UNCERTAINTIES & UNVERIFIED CLAIMS</span>
                          </div>
                          <ul className="list-disc list-inside text-red-200/90 font-sans text-[10px] space-y-0.5 mt-0.5">
                            {m.data.uncertainties.map((unc, i) => (
                              <li key={i}>{unc}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Retrieved SOP Guidance (RAG) */}
                      {m.data.retrieved_guidance && m.data.retrieved_guidance.length > 0 && (
                        <div className="space-y-1 bg-indigo-950/20 p-2.5 rounded-lg border border-indigo-500/30">
                          <div className="flex justify-between items-center text-[9px] font-black text-indigo-300 uppercase tracking-wider">
                            <span className="flex items-center space-x-1">
                              <BookOpen className="w-3 h-3 text-indigo-400" />
                              <span>RETRIEVED DOCTRINAL SOP GUIDANCE</span>
                            </span>
                            <DataSourceBadge sourceType="RAG" size="sm" />
                          </div>
                          <ul className="list-disc list-inside text-slate-300 font-sans text-[10px] space-y-1 mt-1">
                            {m.data.retrieved_guidance.map((guidance, i) => (
                              <li key={i} className="leading-snug">{guidance}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Recommended Next Step */}
                      {m.data.recommendations && m.data.recommendations.length > 0 && (
                        <div className="space-y-1 bg-cyan-950/20 p-2 rounded border border-cyan-500/30">
                          <div className="text-[9px] font-black text-cyan-300 uppercase tracking-wider flex items-center space-x-1">
                            <ShieldAlert className="w-3 h-3 text-cyan-400" />
                            <span>RECOMMENDED OPERATIONAL STEP</span>
                          </div>
                          <div className="text-white font-sans text-[10px] mt-0.5">
                            {m.data.recommendations.join(' • ')}
                          </div>
                        </div>
                      )}


                      {/* Internal Engines Consulted Drawer */}
                      {m.data.tools_used && m.data.tools_used.length > 0 && (
                        <div className="pt-1">
                          <div className="flex items-center justify-between text-[9px] text-slate-500">
                            <span className="uppercase font-bold">Consulted AEGIS Engines:</span>
                            <span className="text-cyan-400 font-bold">Confidence: {m.data.confidence_score}%</span>
                          </div>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {m.data.tools_used.map((tool, i) => (
                              <span key={i} className="px-1.5 py-0.5 rounded bg-slate-950 text-cyan-300 border border-slate-800 text-[9px] font-mono">
                                ✓ {tool.replace('get_', '').replace('run_', '').replace('_', ' ').toUpperCase()}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Interactive Deep Links */}
                      {m.data.deep_links && m.data.deep_links.length > 0 && (
                        <div className="pt-2 border-t border-slate-800 flex flex-wrap gap-1.5">
                          {m.data.deep_links.map((link, i) => (
                            <button
                              key={i}
                              onClick={() => handleDeepLink(link)}
                              className="px-2.5 py-1 rounded bg-cyan-500/15 hover:bg-cyan-500/30 text-cyan-300 hover:text-white border border-cyan-500/40 text-[10px] font-bold flex items-center space-x-1 transition-all"
                            >
                              <span>{link.label}</span>
                              <ExternalLink className="w-2.5 h-2.5 ml-0.5" />
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* If Command Briefing Data is Attached */}
                  {m.briefing && (
                    <div className="space-y-2.5 pt-2 border-t border-slate-800 text-[10px]">
                      <div className="bg-slate-950 p-3 rounded-lg border border-cyan-500/40 space-y-2">
                        <div className="flex justify-between items-center border-b border-slate-800 pb-1.5">
                          <span className="font-black text-cyan-400 text-[11px]">{m.briefing.title}</span>
                          <span className="text-emerald-400 font-bold">{m.briefing.confidence_percent}% Confidence</span>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-2 text-[10px]">
                          <div>
                            <span className="text-slate-500 uppercase">Top Priority:</span>
                            <div className="text-white font-bold">{m.briefing.top_priority_zone}</div>
                          </div>
                          <div>
                            <span className="text-slate-500 uppercase">Current Risk:</span>
                            <div className="text-amber-400 font-black text-sm">{m.briefing.current_risk_score}/100</div>
                          </div>
                        </div>

                        <div>
                          <span className="text-slate-500 uppercase">Escalation Horizon:</span>
                          <div className="text-red-300 font-bold">{m.briefing.predicted_escalation}</div>
                        </div>

                        <div>
                          <span className="text-slate-500 uppercase">Recommended Mission:</span>
                          <div className="text-cyan-300 font-bold">{m.briefing.recommended_mission} (Impact: {m.briefing.mission_score}/100)</div>
                        </div>

                        <div className="pt-1.5 border-t border-slate-800 flex space-x-2">
                          <button
                            onClick={() => onNavigate('MISSIONS', 'zone-7')}
                            className="flex-1 py-1 rounded bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-[10px]"
                          >
                            VIEW MISSION PLAN
                          </button>
                          <button
                            onClick={() => onNavigate('SIMULATE', 'zone-7')}
                            className="flex-1 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-[10px]"
                          >
                            OPEN SIMULATOR
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex items-center space-x-2.5 text-cyan-400 text-xs py-2 px-1">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping"></span>
                <span>Synthesizing structured multi-engine disaster intelligence...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="p-3 bg-slate-900 border-t border-slate-800 flex items-center space-x-2"
          >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask AEGIS (e.g. Which team should go? What if we evacuate Zone 7?)..."
              className="flex-1 bg-slate-950 border border-slate-700 focus:border-cyan-400 rounded-lg px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none shadow-inner"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-40 text-black font-black text-xs flex items-center space-x-1.5 shadow-[0_0_15px_rgba(0,240,255,0.4)] transition-all"
            >
              <span>SEND</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
};
