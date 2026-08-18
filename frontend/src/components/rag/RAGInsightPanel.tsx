import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { RAGQueryResult, RAGDocumentSummary } from '../../types';
import { DataSourceBadge } from '../common/DataSourceBadge';
import {
  BookOpen,
  Search,
  FileText,
  CheckCircle2,
  ExternalLink,
  Shield,
  Zap,
  Clock,
  Sparkles
} from 'lucide-react';

interface RAGInsightPanelProps {
  initialQuery?: string;
  onSelectGuideline?: (guidelineText: string) => void;
}

export const RAGInsightPanel: React.FC<RAGInsightPanelProps> = ({
  initialQuery = "flood evacuation road cutoff",
  onSelectGuideline
}) => {
  const [query, setQuery] = useState<string>(initialQuery);
  const [documents, setDocuments] = useState<RAGDocumentSummary[]>([]);
  const [searchResult, setSearchResult] = useState<RAGQueryResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);

  useEffect(() => {
    loadDocuments();
    handleSearch(initialQuery);
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await api.getRAGDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to load RAG documents catalog:', err);
    }
  };

  const handleSearch = async (searchText: string) => {
    if (!searchText.trim()) return;
    try {
      setLoading(true);
      const res = await api.queryRAG(searchText, 3);
      setSearchResult(res);
    } catch (err) {
      console.error('Failed to query RAG knowledge base:', err);
    } finally {
      setLoading(false);
    }
  };

  const quickTopics = [
    "Hospital trauma redirection",
    "Substation inundation failure",
    "Swiftwater boat capability",
    "Silent crisis zero report",
    "Evacuation route closure"
  ];

  return (
    <div className="hud-card p-4 rounded-2xl border border-indigo-500/40 bg-gradient-to-b from-slate-950 via-[#0a0c18] to-slate-950 shadow-xl font-mono text-xs select-none space-y-4">
      
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-indigo-500/30 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 shadow-[0_0_12px_rgba(99,102,241,0.3)]">
            <BookOpen className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-xs sm:text-sm font-black text-white tracking-wider">
                EMERGENCY SOP & DOCTRINAL RAG KNOWLEDGE
              </h3>
              <DataSourceBadge sourceType="RAG" size="sm" />
            </div>
            <p className="text-[10px] text-slate-400 font-sans mt-0.5">
              Authoritative disaster guidelines, triage standards, and infrastructure contingency doctrine.
            </p>
          </div>
        </div>

        <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-500/40 font-bold">
          {documents.length} SOP MANUALS INDEXED
        </span>
      </div>

      {/* Search Input Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSearch(query);
        }}
        className="flex items-center space-x-2"
      >
        <div className="relative flex-1">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search emergency SOPs (e.g. 'hospital evacuation protocols')..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 pl-9 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-400 font-mono"
          />
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-black text-xs shadow-[0_0_15px_rgba(99,102,241,0.35)] disabled:opacity-40 transition-all flex items-center space-x-1.5"
        >
          <span>{loading ? 'RETRIEVING...' : 'SEARCH SOP'}</span>
        </button>
      </form>

      {/* Quick Topic Chips */}
      <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 scrollbar-thin">
        <span className="text-[9px] text-slate-500 font-bold uppercase shrink-0">TOPICS:</span>
        {quickTopics.map((t, idx) => (
          <button
            key={idx}
            onClick={() => {
              setQuery(t);
              handleSearch(t);
            }}
            className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-indigo-950/60 text-slate-300 hover:text-indigo-200 border border-slate-800 text-[10px] font-bold shrink-0 transition-all"
          >
            {t}
          </button>
        ))}
      </div>

      {/* Retrieved Knowledge Snippets */}
      {searchResult && (
        <div className="space-y-2">
          <div className="flex justify-between items-center text-[10px] text-slate-400 font-bold">
            <span>RETRIEVED DOCTRINAL CITATIONS ({searchResult.retrieved_count})</span>
            <span className="text-indigo-400">Provenance: {searchResult.source_type}</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {searchResult.citations.map((c, i) => (
              <div
                key={c.doc_id + i}
                onClick={() => onSelectGuideline && onSelectGuideline(c.snippet)}
                className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 hover:border-indigo-500/50 flex flex-col justify-between space-y-2 cursor-pointer transition-all hover:bg-slate-900 group"
              >
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[9px] font-black text-indigo-400">{c.doc_id}</span>
                    <span className="text-[8px] px-1.5 py-0.2 rounded bg-indigo-950 text-indigo-300 border border-indigo-500/30">
                      Score: {c.relevance_score}
                    </span>
                  </div>
                  <h4 className="text-[11px] font-bold text-white group-hover:text-indigo-300 leading-tight">
                    {c.title}
                  </h4>
                  <p className="text-[10px] text-slate-300 font-sans mt-1.5 line-clamp-3 leading-relaxed">
                    {c.snippet}
                  </p>
                </div>

                <div className="text-[8px] text-slate-500 pt-1 border-t border-slate-800/80 truncate">
                  Source: {c.source}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};
