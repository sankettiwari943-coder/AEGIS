import React, { useState, useEffect } from 'react';
import { AlertCircle, ArrowRight, Shield, Radio, Flame, Sparkles, Bot } from 'lucide-react';
import { MainNavMode } from '../../types';

interface AlertTickerProps {
  onNavigate: (mode: MainNavMode, zoneId?: string) => void;
}

export const AlertTicker: React.FC<AlertTickerProps> = ({ onNavigate }) => {
  const alerts = [
    {
      id: 1,
      type: 'PREDICTION',
      badge: 'PREDICTIVE ALERT',
      text: 'Zone 7 (River Bend) projected to isolate in 42 minutes. Corridor 14 bridge overtopping imminent.',
      actionLabel: 'RUN SIMULATION',
      targetMode: 'SIMULATE' as MainNavMode,
      color: 'text-amber-400 border-amber-500/40 bg-amber-950/30'
    },
    {
      id: 2,
      type: 'SILENT_RISK',
      badge: 'SILENT CRISIS',
      text: 'Zone 4 (Riverside Slums) 91% Anomaly: 0 SOS reports received due to Tower Delta-4 destruction. 9,300 pop in deep water.',
      actionLabel: 'INSPECT EVIDENCE',
      targetMode: 'EVIDENCE' as MainNavMode,
      color: 'text-red-400 border-red-500/40 bg-red-950/30'
    },
    {
      id: 3,
      type: 'MISSION',
      badge: 'RECOMMENDATION',
      text: 'AI Mission Optimizer recommends dispatching Swiftwater Team Delta-2 with onboard trauma kit.',
      actionLabel: 'VIEW MISSIONS',
      targetMode: 'MISSIONS' as MainNavMode,
      color: 'text-cyan-400 border-cyan-500/40 bg-cyan-950/30'
    }
  ];

  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % alerts.length);
    }, 7000);
    return () => clearInterval(timer);
  }, [alerts.length]);

  const current = alerts[currentIndex];

  const handleAskAegis = (alertItem: typeof alerts[0]) => {
    window.dispatchEvent(new CustomEvent('aegis:ask-orchestrator', {
      detail: { query: `Explain the alert: ${alertItem.text}` }
    }));
  };

  return (
    <div className="w-full bg-[#080d16] border-t border-slate-800/80 px-4 py-2 flex items-center justify-between z-20 text-xs font-mono select-none">
      <div className="flex items-center space-x-3 overflow-hidden">
        <div className="flex items-center space-x-1.5 shrink-0">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
          <span className="font-bold text-slate-300 uppercase tracking-wider text-[11px]">
            TACTICAL AI FEED:
          </span>
        </div>

        <div className="flex items-center space-x-2 truncate">
          <span className={`px-1.5 py-0.5 rounded text-[10px] font-extrabold border ${current.color}`}>
            {current.badge}
          </span>
          <p className="text-slate-200 truncate">{current.text}</p>
        </div>
      </div>

      <div className="flex items-center space-x-2 shrink-0 ml-4">
        {/* ASK AEGIS Button */}
        <button
          onClick={() => handleAskAegis(current)}
          className="flex items-center space-x-1 px-2.5 py-1 rounded bg-cyan-950/80 border border-cyan-500/50 text-cyan-300 hover:bg-cyan-500 hover:text-black text-[10px] font-black tracking-wider transition-all shadow-[0_0_10px_rgba(0,240,255,0.2)]"
          title="Query AI Disaster Orchestrator about this alert"
        >
          <Bot className="w-3 h-3" />
          <span>ASK AEGIS</span>
        </button>

        {/* Action Button */}
        <button
          onClick={() => onNavigate(current.targetMode)}
          className="flex items-center space-x-1 px-2.5 py-1 rounded bg-slate-900 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-800 text-[10px] font-bold tracking-wider transition-all"
        >
          <span>{current.actionLabel}</span>
          <ArrowRight className="w-3 h-3" />
        </button>

        <div className="flex items-center space-x-1 ml-2">
          {alerts.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentIndex(idx)}
              className={`w-1.5 h-1.5 rounded-full transition-all ${
                idx === currentIndex ? 'bg-cyan-400 w-3.5' : 'bg-slate-700'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
