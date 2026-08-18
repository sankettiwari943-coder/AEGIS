import React from 'react';

interface ConfidenceBadgeProps {
  confidencePercent: number;
  sourceEngine?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md';
  className?: string;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  confidencePercent,
  sourceEngine,
  showLabel = true,
  size = 'sm',
  className = ''
}) => {
  const percent = Math.min(100, Math.max(0, Math.round(confidencePercent)));

  const getStyle = () => {
    if (percent >= 85) {
      return {
        bg: 'bg-emerald-950/70 text-emerald-300 border-emerald-500/40',
        dot: 'bg-emerald-400',
        label: 'HIGH'
      };
    } else if (percent >= 65) {
      return {
        bg: 'bg-amber-950/70 text-amber-300 border-amber-500/40',
        dot: 'bg-amber-400',
        label: 'MODERATE'
      };
    } else {
      return {
        bg: 'bg-red-950/70 text-red-300 border-red-500/40',
        dot: 'bg-red-400',
        label: 'LOW'
      };
    }
  };

  const style = getStyle();

  return (
    <span
      className={`inline-flex items-center space-x-1.5 px-2 py-0.5 rounded border font-mono ${
        size === 'md' ? 'text-xs' : 'text-[10px]'
      } font-bold ${style.bg} ${className}`}
      title={sourceEngine ? `Calibrated Confidence (${sourceEngine})` : 'Confidence'}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
      <span>{percent}%</span>
      {showLabel && <span className="opacity-75 text-[9px]">({style.label})</span>}
    </span>
  );
};
