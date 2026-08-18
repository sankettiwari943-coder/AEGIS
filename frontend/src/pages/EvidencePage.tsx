import React, { useState, useEffect } from 'react';
import { ClaimAssessment, EvidenceSummaryResponse, MainNavMode, EvidenceStatus } from '../types';
import { api } from '../services/api';
import { EvidenceChain } from '../components/evidence/EvidenceChain';
import { 
  FileCheck, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Radio, 
  ShieldAlert, 
  ChevronDown, 
  ChevronUp,
  Cpu,
  Layers,
  ArrowRight,
  Search,
  Sliders,
  TrendingUp,
  Clock,
  ExternalLink,
  Info,
  Compass,
  Sparkles,
  Zap,
  Activity
} from 'lucide-react';

interface EvidencePageProps {
  onNavigate: (mode: MainNavMode, zoneId?: string) => void;
}

export const EvidencePage: React.FC<EvidencePageProps> = ({ onNavigate }) => {
  const [summary, setSummary] = useState<EvidenceSummaryResponse | null>(null);
  const [claims, setClaims] = useState<ClaimAssessment[]>([]);
  const [selectedClaimId, setSelectedClaimId] = useState<string>('claim-01');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [inspectingDecisionId, setInspectingDecisionId] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvidenceData = async () => {
      setLoading(true);
      try {
        const [sumData, claimsData] = await Promise.all([
          api.getEvidenceSummary(),
          api.getClaims()
        ]);
        setSummary(sumData);
        setClaims(claimsData);
      } catch (err) {
        console.error('Failed to load evidence center data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchEvidenceData();
  }, []);

  const activeClaim = claims.find(c => c.claim_id === selectedClaimId) || claims[0];

  const filteredClaims = claims.filter(c => {
    const matchesSearch = c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.claim_statement.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.target_zone_id.toLowerCase().includes(searchQuery.toLowerCase());
    
    if (!matchesSearch) return false;
    if (filterStatus === 'ALL') return true;
    if (filterStatus === 'VERIFIED') return c.status === 'VERIFIED';
    if (filterStatus === 'SUPPORTED') return c.status === 'SUPPORTED';
    if (filterStatus === 'CONFLICTING') return c.status === 'CONFLICTING' || c.status === 'REJECTED';
    if (filterStatus === 'STALE') return c.status === 'STALE';
    if (filterStatus === 'UNVERIFIED') return c.status === 'UNVERIFIED';
    return true;
  });

  return (
    <div className="w-full h-full flex flex-col space-y-3 p-4 overflow-y-auto font-mono text-xs">
      
      {/* 1. TOP BANNER: EVIDENCE INTELLIGENCE & TRUST INDEX */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        
        {/* Left: Summary Metrics Ribbon */}
        <div className="lg:col-span-2 hud-card p-4 rounded-lg flex flex-col justify-between border-l-4 border-l-cyan-400 bg-slate-900/80">
          <div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileCheck className="w-5 h-5 text-cyan-400" />
                <span className="text-white font-extrabold text-sm tracking-wide">
                  EVIDENCE & TRUTH INTELLIGENCE CENTER
                </span>
              </div>
              <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/40 text-[10px] font-bold">
                GROUND TRUTH CORROBORATION
              </span>
            </div>
            <p className="text-slate-400 text-xs mt-1 font-sans">
              Every decision, risk score, and cascade is cross-examined against physical sensor telemetry, SAR radar apertures, citizen reports, and SCADA signals to eliminate unverified rumors and hallucinations.
            </p>
          </div>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-6 gap-2 mt-3 pt-3 border-t border-slate-800 text-center">
            <div className="bg-slate-950/60 p-2 rounded border border-slate-800">
              <div className="text-slate-400 text-[10px]">Claims Analyzed</div>
              <div className="text-white font-black text-sm mt-0.5">{summary?.total_claims_analyzed ?? 42}</div>
            </div>
            <div className="bg-cyan-950/30 p-2 rounded border border-cyan-500/30">
              <div className="text-cyan-400 text-[10px]">Verified</div>
              <div className="text-cyan-300 font-black text-sm mt-0.5">{summary?.verified_count ?? 26}</div>
            </div>
            <div className="bg-emerald-950/30 p-2 rounded border border-emerald-500/30">
              <div className="text-emerald-400 text-[10px]">Supported</div>
              <div className="text-emerald-300 font-black text-sm mt-0.5">{summary?.supported_count ?? 9}</div>
            </div>
            <div className="bg-amber-950/30 p-2 rounded border border-amber-500/30">
              <div className="text-amber-400 text-[10px]">Unverified</div>
              <div className="text-amber-300 font-black text-sm mt-0.5">{summary?.unverified_count ?? 5}</div>
            </div>
            <div className="bg-red-950/30 p-2 rounded border border-red-500/30">
              <div className="text-red-400 text-[10px]">Conflicting</div>
              <div className="text-red-300 font-black text-sm mt-0.5">{summary?.conflicting_count ?? 2}</div>
            </div>
            <div className="bg-purple-950/30 p-2 rounded border border-purple-500/30">
              <div className="text-purple-400 text-[10px]">Stale</div>
              <div className="text-purple-300 font-black text-sm mt-0.5">{summary?.stale_count ?? 1}</div>
            </div>
          </div>
        </div>

        {/* Right: Aggregate Data Trust Meter */}
        <div className="hud-card p-4 rounded-lg flex flex-col justify-between border-l-4 border-l-emerald-400 bg-slate-900/80">
          <div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1.5 text-emerald-400 font-bold">
                <ShieldAlert className="w-4 h-4" />
                <span>DATA TRUST INDEX</span>
              </div>
              <span className="text-emerald-400 font-black text-sm">
                {summary?.data_trust_index ?? 84} / 100
              </span>
            </div>

            {/* Trust Breakdown Progress Bars */}
            <div className="mt-2.5 space-y-1.5 text-[10px]">
              <div>
                <div className="flex justify-between text-slate-400 mb-0.5">
                  <span>Source Reliability</span>
                  <span className="text-slate-200 font-bold">{summary?.trust_breakdown?.source_reliability ?? 88}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded overflow-hidden">
                  <div className="h-full bg-cyan-400 rounded" style={{ width: `${summary?.trust_breakdown?.source_reliability ?? 88}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-400 mb-0.5">
                  <span>Recency Score</span>
                  <span className="text-slate-200 font-bold">{summary?.trust_breakdown?.recency ?? 85}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded overflow-hidden">
                  <div className="h-full bg-emerald-400 rounded" style={{ width: `${summary?.trust_breakdown?.recency ?? 85}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-400 mb-0.5">
                  <span>Cross-Corroboration Consistency</span>
                  <span className="text-slate-200 font-bold">{summary?.trust_breakdown?.consistency ?? 82}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded overflow-hidden">
                  <div className="h-full bg-blue-400 rounded" style={{ width: `${summary?.trust_breakdown?.consistency ?? 82}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-400 mb-0.5">
                  <span>Conflict Penalty Level</span>
                  <span className="text-amber-400 font-bold">{summary?.trust_breakdown?.conflict_level ?? 15}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded overflow-hidden">
                  <div className="h-full bg-amber-400 rounded" style={{ width: `${summary?.trust_breakdown?.conflict_level ?? 15}%` }} />
                </div>
              </div>
            </div>
          </div>

          <div className="mt-2 text-[9px] text-slate-500 italic">
            Reflects verifiable empirical telemetry quality.
          </div>
        </div>
      </div>

      {/* 2. FILTER & SEARCH CONTROLS */}
      <div className="hud-card p-3 rounded-lg flex flex-wrap items-center justify-between gap-2 bg-slate-900/60">
        <div className="flex items-center space-x-1.5 flex-wrap gap-1">
          {['ALL', 'VERIFIED', 'SUPPORTED', 'CONFLICTING', 'STALE', 'UNVERIFIED'].map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-2.5 py-1 rounded text-[11px] font-bold transition-all ${
                filterStatus === status
                  ? 'bg-cyan-500 text-black shadow-[0_0_10px_rgba(6,182,212,0.3)]'
                  : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
              }`}
            >
              {status}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-2 bg-slate-950 px-2.5 py-1 rounded border border-slate-700">
          <Search className="w-3.5 h-3.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search claims, sensors, zones..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-transparent text-white placeholder-slate-500 focus:outline-none text-xs w-48 font-mono"
          />
        </div>
      </div>

      {/* 3. MAIN WORKSPACE: CLAIMS LIST (LEFT) & INVESTIGATION PANEL (RIGHT) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 min-h-[480px]">
        
        {/* Left Column: Claims List */}
        <div className="lg:col-span-5 space-y-2 overflow-y-auto max-h-[620px] pr-1">
          {loading ? (
            <div className="p-8 text-center text-slate-500 animate-pulse">Loading claims...</div>
          ) : filteredClaims.length === 0 ? (
            <div className="p-8 text-center text-slate-500 hud-card rounded-lg">
              No claims match the active filter criteria.
            </div>
          ) : (
            filteredClaims.map((claim) => {
              const isSelected = activeClaim?.claim_id === claim.claim_id;
              const isVerified = claim.status === 'VERIFIED';
              const isSupported = claim.status === 'SUPPORTED';
              const isConflicting = claim.status === 'CONFLICTING' || claim.status === 'REJECTED';
              const isStale = claim.status === 'STALE';

              return (
                <div
                  key={claim.claim_id}
                  onClick={() => setSelectedClaimId(claim.claim_id)}
                  className={`hud-card p-3 rounded-lg cursor-pointer transition-all border ${
                    isSelected
                      ? 'border-cyan-400 bg-cyan-950/30 shadow-[0_0_15px_rgba(6,182,212,0.2)]'
                      : 'border-slate-800 hover:border-slate-700 bg-slate-900/60'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      <span className={`px-1.5 py-0.2 rounded text-[9px] font-black border ${
                        isVerified ? 'bg-cyan-950 text-cyan-300 border-cyan-500/40' :
                        isSupported ? 'bg-emerald-950 text-emerald-300 border-emerald-500/40' :
                        isConflicting ? 'bg-red-950 text-red-300 border-red-500/40' :
                        isStale ? 'bg-purple-950 text-purple-300 border-purple-500/40' :
                        'bg-amber-950 text-amber-300 border-amber-500/40'
                      }`}>
                        {claim.status}
                      </span>
                      <span className="text-[10px] text-slate-400 uppercase font-bold">{claim.target_zone_id}</span>
                    </div>

                    <div className="text-right">
                      <span className="text-[10px] text-slate-400 mr-1">AI CONFIDENCE:</span>
                      <span className={`font-black text-xs ${
                        claim.ai_confidence_percent >= 80 ? 'text-cyan-300' :
                        claim.ai_confidence_percent >= 60 ? 'text-emerald-300' :
                        'text-amber-400'
                      }`}>
                        {claim.ai_confidence_percent}%
                      </span>
                    </div>
                  </div>

                  <div className="text-white font-extrabold text-xs mt-1.5 leading-snug">
                    {claim.title}
                  </div>

                  <p className="text-slate-400 text-[11px] mt-1 font-sans line-clamp-2">
                    {claim.claim_statement}
                  </p>

                  <div className="mt-2.5 pt-2 border-t border-slate-800 flex items-center justify-between text-[10px]">
                    <div className="flex items-center space-x-3 text-slate-400">
                      <span className="text-emerald-400 font-bold">{claim.supporting_sources_count} supporting</span>
                      {claim.conflicting_sources_count > 0 && (
                        <span className="text-red-400 font-bold">{claim.conflicting_sources_count} conflicting</span>
                      )}
                    </div>
                    <span className="text-cyan-400 font-bold flex items-center">
                      INVESTIGATE <ArrowRight className="w-3 h-3 ml-0.5" />
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Column: Detailed Investigation Panel */}
        <div className="lg:col-span-7 hud-card p-4 rounded-lg bg-slate-900/90 border-slate-700 flex flex-col justify-between space-y-4 overflow-y-auto max-h-[620px]">
          {activeClaim ? (
            <div className="space-y-4">
              
              {/* Claim Title & Status Header */}
              <div className="border-b border-slate-800 pb-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-cyan-400 uppercase font-bold tracking-widest">
                    TARGET: {activeClaim.target_entity} ({activeClaim.target_zone_id.toUpperCase()})
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-black border ${
                    activeClaim.status === 'VERIFIED' ? 'bg-cyan-950 text-cyan-300 border-cyan-500/40' :
                    activeClaim.status === 'SUPPORTED' ? 'bg-emerald-950 text-emerald-300 border-emerald-500/40' :
                    activeClaim.status === 'CONFLICTING' || activeClaim.status === 'REJECTED' ? 'bg-red-950 text-red-300 border-red-500/40' :
                    'bg-amber-950 text-amber-300 border-amber-500/40'
                  }`}>
                    STATUS: {activeClaim.status}
                  </span>
                </div>

                <div className="text-base font-extrabold text-white mt-1">
                  {activeClaim.title}
                </div>

                <div className="bg-slate-950 p-2.5 rounded border border-slate-800 mt-2 text-slate-300 text-xs font-sans">
                  <span className="text-cyan-400 font-mono font-bold text-[10px] block mb-0.5">CLAIM STATEMENT:</span>
                  {activeClaim.claim_statement}
                </div>
              </div>

              {/* Confidence & Score Metrics Bar */}
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                  <div className="text-[10px] text-slate-400">AI Confidence</div>
                  <div className="text-cyan-300 font-black text-sm mt-0.5">{activeClaim.ai_confidence_percent}%</div>
                </div>
                <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                  <div className="text-[10px] text-slate-400">Recency Factor</div>
                  <div className="text-emerald-300 font-black text-sm mt-0.5">{activeClaim.recency_score}%</div>
                </div>
                <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                  <div className="text-[10px] text-slate-400">Data Trust Score</div>
                  <div className="text-blue-300 font-black text-sm mt-0.5">{activeClaim.data_trust_score}%</div>
                </div>
              </div>

              {/* Contradicting / Conflicting Signals (If Any) */}
              {activeClaim.conflicting_evidence && activeClaim.conflicting_evidence.length > 0 && (
                <div className="bg-red-950/30 p-3 rounded-lg border-2 border-red-500/50 space-y-2">
                  <div className="flex items-center space-x-1.5 text-red-400 font-bold text-xs">
                    <AlertTriangle className="w-4 h-4 animate-pulse" />
                    <span>CONFLICTING INFORMATION DETECTED ({activeClaim.conflicting_evidence.length})</span>
                  </div>
                  <p className="text-slate-300 text-xs font-sans">
                    The system does not conceal contradictions. Opposing telemetry is isolated and flagged for reconciliation:
                  </p>
                  <div className="space-y-1.5 pt-1">
                    {activeClaim.conflicting_evidence.map((conf) => (
                      <div key={conf.id} className="bg-slate-950/80 p-2 rounded border border-red-500/30 flex items-start justify-between">
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-red-300">{conf.source}</span>
                            <span className="text-[9px] text-slate-400">({conf.minutes_ago}m ago)</span>
                          </div>
                          <div className="text-[11px] text-slate-200 mt-0.5 font-sans">
                            {conf.claim}
                          </div>
                        </div>
                        <div className="text-right shrink-0 ml-2">
                          <span className="text-[9px] text-slate-400">Value:</span>
                          <div className="font-bold text-amber-300 text-[10px]">{String(conf.value)}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Supporting Evidence Checklist */}
              <div className="space-y-2">
                <div className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>SUPPORTING EVIDENCE TELEMETRY ({activeClaim.supporting_evidence.length})</span>
                </div>

                <div className="space-y-1.5">
                  {activeClaim.supporting_evidence.map((item) => (
                    <div key={item.id} className="bg-slate-950 p-2.5 rounded border border-slate-800 flex items-center justify-between">
                      <div className="flex items-start space-x-2.5">
                        <span className="text-emerald-400 font-bold mt-0.5">✓</span>
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-white text-xs">{item.source}</span>
                            <span className="px-1.5 py-0.2 rounded bg-slate-800 text-cyan-300 text-[9px] border border-cyan-500/30">
                              {item.type}
                            </span>
                            <span className="text-[9px] text-slate-400">{item.minutes_ago}m ago</span>
                          </div>
                          <p className="text-slate-300 text-[11px] font-sans mt-0.5">{item.claim}</p>
                        </div>
                      </div>

                      <div className="text-right shrink-0 ml-3">
                        <div className="text-[9px] text-slate-400">Reliability: {(item.reliability * 100).toFixed(0)}%</div>
                        <div className="text-emerald-300 font-bold text-[10px] mt-0.5">{String(item.value)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Chronological Evidence Timeline */}
              {activeClaim.evidence_timeline && activeClaim.evidence_timeline.length > 0 && (
                <div className="space-y-2 bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <div className="text-[11px] font-bold text-cyan-400 uppercase tracking-wider flex items-center space-x-1.5">
                    <Clock className="w-3.5 h-3.5" />
                    <span>CHRONOLOGICAL SIGNAL RECONCILIATION TIMELINE</span>
                  </div>

                  <div className="space-y-1.5 pt-1">
                    {activeClaim.evidence_timeline.map((t, idx) => (
                      <div key={idx} className="flex items-center space-x-2 text-[11px]">
                        <span className="text-slate-500 font-mono text-[9px] w-14 shrink-0">{t.time_display}</span>
                        <span className={`w-1.5 h-1.5 rounded-full ${t.is_contradicting ? 'bg-red-400' : 'bg-cyan-400'}`} />
                        <span className="font-bold text-slate-200">{t.source}:</span>
                        <span className="text-slate-300 font-sans truncate">{t.event}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendation & Recon Warning */}
              <div className="bg-slate-950 p-3 rounded-lg border-l-4 border-l-cyan-400 text-slate-300 text-xs font-sans space-y-1">
                <span className="text-cyan-400 font-mono font-bold text-[10px] block">OPERATIONAL DECISION RECOMMENDATION:</span>
                <p>{activeClaim.decision_recommendation}</p>
                {activeClaim.requires_physical_recon && (
                  <div className="mt-2 text-amber-300 font-bold flex items-center space-x-1">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Physical spotter or UAV recon verification mandatory before full asset commitment.</span>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500">
              Select a claim to inspect its evidence chain.
            </div>
          )}

          {/* Action Footer */}
          <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
            <button
              onClick={() => setInspectingDecisionId(activeClaim?.target_zone_id === 'zone-4' ? 'decision-zone-4-silent' : 'decision-zone-7-escalation')}
              className="px-3 py-1.5 rounded bg-cyan-500 hover:bg-cyan-400 text-black font-extrabold text-xs flex items-center space-x-1.5 shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all"
            >
              <Cpu className="w-3.5 h-3.5" />
              <span>VIEW FULL 4-STAGE DECISION CHAIN</span>
            </button>

            <button
              onClick={() => onNavigate('SIMULATE')}
              className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs flex items-center space-x-1"
            >
              <span>SIMULATE WHAT-IF</span>
              <ArrowRight className="w-3 h-3 ml-1" />
            </button>
          </div>
        </div>
      </div>

      {/* Reusable Decision Evidence Trace Modal */}
      {inspectingDecisionId && (
        <EvidenceChain
          decisionId={inspectingDecisionId}
          onClose={() => setInspectingDecisionId(null)}
          onNavigate={onNavigate}
        />
      )}
    </div>
  );
};
