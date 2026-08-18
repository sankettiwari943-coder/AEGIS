import React from 'react';
import { DataSourceClassification } from '../../types';
import { Radio, Database, Shield, Users, Sparkles, BookOpen, Eye, Activity } from 'lucide-react';

interface DataSourceBadgeProps {
  sourceType: DataSourceClassification | string;
  sourceLabel?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const DataSourceBadge: React.FC<DataSourceBadgeProps> = ({
  sourceType,
  sourceLabel,
  size = 'sm',
  className = ''
}) => {
  const norm = (sourceType || 'SIMULATED').toUpperCase();

  const getStyle = () => {
    switch (norm) {
      case 'LIVE':
        return {
          bg: 'bg-emerald-950/80 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
          icon: Activity,
          pulse: true,
          label: sourceLabel || 'LIVE FEED'
        };
      case 'SENSOR':
        return {
          bg: 'bg-cyan-950/80 text-cyan-300 border-cyan-500/50 shadow-[0_0_8px_rgba(6,182,212,0.25)]',
          icon: Radio,
          pulse: false,
          label: sourceLabel || 'IOT SENSOR'
        };
      case 'OFFICIAL':
        return {
          bg: 'bg-blue-950/80 text-blue-300 border-blue-500/50',
          icon: Shield,
          pulse: false,
          label: sourceLabel || 'OFFICIAL DATA'
        };
      case 'CIVILIAN':
        return {
          bg: 'bg-amber-950/80 text-amber-300 border-amber-500/50',
          icon: Users,
          pulse: false,
          label: sourceLabel || 'CIVILIAN SOS'
        };
      case 'AI-INFERRED':
        return {
          bg: 'bg-purple-950/80 text-purple-300 border-purple-500/50 shadow-[0_0_8px_rgba(168,85,247,0.25)]',
          icon: Sparkles,
          pulse: false,
          label: sourceLabel || 'AI-INFERRED'
        };
      case 'RAG':
        return {
          bg: 'bg-indigo-950/80 text-indigo-300 border-indigo-500/50',
          icon: BookOpen,
          pulse: false,
          label: sourceLabel || 'RETRIEVED SOP'
        };
      case 'DEMO CV':
      case 'CV':
        return {
          bg: 'bg-teal-950/80 text-teal-300 border-teal-500/50 shadow-[0_0_8px_rgba(20,184,166,0.25)]',
          icon: Eye,
          pulse: false,
          label: sourceLabel || 'DEMO CV'
        };
      case 'SIMULATED':
      default:
        return {
          bg: 'bg-slate-900/90 text-slate-300 border-slate-700',
          icon: Database,
          pulse: false,
          label: sourceLabel || 'SIMULATED'
        };
    }
  };

  const config = getStyle();
  const Icon = config.icon;

  const sizeClasses = size === 'lg'
    ? 'px-2.5 py-1 text-xs space-x-1.5'
    : size === 'md'
    ? 'px-2 py-0.5 text-[10px] space-x-1'
    : 'px-1.5 py-0.5 text-[9px] space-x-1';

  return (
    <span
      className={`inline-flex items-center rounded-md border font-mono font-bold uppercase tracking-wider ${config.bg} ${sizeClasses} ${className}`}
    >
      {config.pulse && <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping mr-0.5" />}
      <Icon className={size === 'lg' ? 'w-3.5 h-3.5' : 'w-2.5 h-2.5'} />
      <span>{config.label}</span>
    </span>
  );
};
