import React, { useState, useEffect } from 'react';
import { ZoneCascadeGraphResponse, MainNavMode } from '../../types';
import { api } from '../../services/api';
import { CascadeGraphView } from './CascadeGraphView';
import { X, RefreshCw, AlertTriangle, Layers, Zap } from 'lucide-react';

interface CascadeModalProps {
  zoneId: string | null;
  onClose: () => void;
  onNavigate?: (mode: MainNavMode, zoneId?: string) => void;
}

export const CascadeModal: React.FC<CascadeModalProps> = ({
  zoneId,
  onClose,
  onNavigate
}) => {
  const [graphData, setGraphData] = useState<ZoneCascadeGraphResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!zoneId) return;

    const fetchGraph = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getZoneCascadeGraph(zoneId);
        setGraphData(data);
      } catch (err: any) {
        console.error('Failed to load cascade graph:', err);
        setError(err.message || 'Error loading cascade graph telemetry');
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
  }, [zoneId]);

  if (!zoneId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in font-mono">
      <div className="relative w-full max-w-6xl max-h-[90vh] bg-[#070b12] border border-cyan-500/50 rounded-xl shadow-[0_0_50px_rgba(0,240,255,0.2)] flex flex-col overflow-hidden">
        {/* Modal Top Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-900/90">
          <div className="flex items-center space-x-2">
            <span className="p-1.5 rounded bg-amber-950 text-amber-400 border border-amber-500/40">
              <Zap className="w-5 h-5 animate-pulse" />
            </span>
            <div>
              <h2 className="text-sm font-black text-white tracking-wider flex items-center space-x-2">
                <span>CASCADING DISASTER INTELLIGENCE CENTER</span>
                <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/40 text-[9px] font-bold">
                  MULTI-SECTOR DEPENDENCY GRAPH
                </span>
              </h2>
              <div className="text-[10px] text-slate-400">
                Systemic failure chain analysis & explainable risk propagation
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-4 flex-1 overflow-y-auto">
          {loading && (
            <div className="flex flex-col items-center justify-center py-24 space-y-3">
              <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
              <div className="text-xs text-slate-400">
                Propagating Multi-Step Failure Chains across Municipal Grids...
              </div>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-lg bg-red-950/40 border border-red-500/50 text-red-300 text-center space-y-2">
              <AlertTriangle className="w-6 h-6 mx-auto text-red-400" />
              <div className="text-xs font-bold">{error}</div>
            </div>
          )}

          {!loading && !error && graphData && (
            <CascadeGraphView
              graphData={graphData}
              onNavigate={(mode, targetZone) => {
                onClose();
                if (onNavigate) onNavigate(mode, targetZone);
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};
