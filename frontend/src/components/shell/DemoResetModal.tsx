import React, { useState } from 'react';
import { useDemo } from '../../context/DemoContext';
import { RotateCcw, X, AlertTriangle, CheckCircle2 } from 'lucide-react';

export const DemoResetModal: React.FC = () => {
  const { showResetModal, setShowResetModal, executeResetDemo } = useDemo();
  const [resetting, setResetting] = useState(false);
  const [success, setSuccess] = useState(false);

  if (!showResetModal) return null;

  const handleReset = async () => {
    try {
      setResetting(true);
      await executeResetDemo();
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        setShowResetModal(false);
      }, 1500);
    } catch (err) {
      console.error('Reset failed:', err);
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-[#0b1220] border border-red-500/60 rounded-2xl p-5 shadow-[0_0_50px_rgba(239,68,68,0.25)] space-y-4 font-mono text-slate-200 animate-in zoom-in-95">
        
        {/* Header */}
        <div className="flex justify-between items-center border-b border-slate-800 pb-2.5">
          <div className="flex items-center space-x-2 text-red-400 font-bold text-sm">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <span>RESET AEGIS DEMO SCENARIO?</span>
          </div>
          <button
            onClick={() => setShowResetModal(false)}
            className="p-1 text-slate-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {success ? (
          <div className="p-4 bg-emerald-950/60 border border-emerald-500/50 rounded-xl flex items-center space-x-3 text-emerald-300 text-xs">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <div>
              <div className="font-bold">DEMO SCENARIO RESET SUCCESSFUL</div>
              <div className="text-[10px] text-emerald-400/80 mt-0.5">Timeline reset to T+0 baseline.</div>
            </div>
          </div>
        ) : (
          <>
            <p className="text-xs font-sans text-slate-300 leading-relaxed">
              This action will reset the deterministic demonstration environment back to its initial baseline state:
            </p>

            <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-1.5 text-[11px] font-sans text-slate-400">
              <div className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                <span>Timeline step reset to <strong className="text-white">T+0 (Current Horizon)</strong></span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                <span>Active missions reset to baseline recommendations</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                <span>Simulation history cleared to default comparison</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                <span>Adaptive feedback re-initialized to 24-item dataset</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                <span>AI Orchestrator conversation sessions cleared</span>
              </div>
            </div>

            <p className="text-[10px] text-slate-500 italic">
              * Note: Base geospatial definitions and deterministic incident parameters will remain intact.
            </p>

            <div className="flex space-x-2 pt-2">
              <button
                onClick={() => setShowResetModal(false)}
                className="flex-1 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 text-xs font-bold transition-all"
              >
                CANCEL
              </button>
              <button
                onClick={handleReset}
                disabled={resetting}
                className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-500 hover:to-amber-500 text-white text-xs font-black shadow-[0_0_20px_rgba(239,68,68,0.4)] disabled:opacity-50 flex items-center justify-center space-x-1.5 transition-all"
              >
                <RotateCcw className={`w-3.5 h-3.5 ${resetting ? 'animate-spin' : ''}`} />
                <span>{resetting ? 'RESETTING...' : 'CONFIRM RESET'}</span>
              </button>
            </div>
          </>
        )}

      </div>
    </div>
  );
};
