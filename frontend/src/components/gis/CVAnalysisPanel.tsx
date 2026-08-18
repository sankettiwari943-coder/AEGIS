import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { CVAnalysisResult, CVScanSummary, DetectedObject } from '../../types';
import { DataSourceBadge } from '../common/DataSourceBadge';
import { ConfidenceBadge } from '../common/ConfidenceBadge';
import {
  Eye,
  Camera,
  Layers,
  AlertTriangle,
  CheckCircle2,
  Maximize2,
  X,
  Compass,
  Zap,
  Radio,
  FileCheck
} from 'lucide-react';

interface CVAnalysisPanelProps {
  selectedZoneId?: string;
  onClose?: () => void;
}

export const CVAnalysisPanel: React.FC<CVAnalysisPanelProps> = ({
  selectedZoneId = 'zone-7',
  onClose
}) => {
  const [scans, setScans] = useState<CVScanSummary[]>([]);
  const [selectedScanId, setSelectedScanId] = useState<string>('SCAN-Z07-DRONE-01');
  const [analysisResult, setAnalysisResult] = useState<CVAnalysisResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    loadScans();
  }, []);

  useEffect(() => {
    if (selectedZoneId === 'zone-4') {
      setSelectedScanId('SCAN-Z04-SAR-01');
    } else if (selectedZoneId === 'zone-2') {
      setSelectedScanId('SCAN-Z02-AERIAL-01');
    } else {
      setSelectedScanId('SCAN-Z07-DRONE-01');
    }
  }, [selectedZoneId]);

  useEffect(() => {
    if (selectedScanId) {
      runAnalysis(selectedScanId);
    }
  }, [selectedScanId]);

  const loadScans = async () => {
    try {
      const list = await api.getCVScans();
      setScans(list);
    } catch (err) {
      console.error('Failed to load CV scans catalog:', err);
    }
  };

  const runAnalysis = async (scanId: string) => {
    try {
      setLoading(true);
      const res = await api.getCVScan(scanId);
      setAnalysisResult(res);
    } catch (err) {
      console.error('Failed to run CV analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="hud-card p-4 rounded-2xl border border-teal-500/40 bg-gradient-to-b from-slate-950 via-[#071318] to-slate-950 shadow-2xl font-mono text-xs select-none space-y-4">
      
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-teal-500/30 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-teal-500/20 text-teal-300 border border-teal-500/40 shadow-[0_0_12px_rgba(20,184,166,0.3)]">
            <Camera className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-xs sm:text-sm font-black text-white tracking-wider">
                AERIAL & SATELLITE CV RECONNAISSANCE
              </h3>
              <DataSourceBadge sourceType="DEMO CV" size="sm" />
            </div>
            <p className="text-[10px] text-slate-400 font-sans mt-0.5">
              Automated image segmentation for flood extent, submerged roads, and damaged structures.
            </p>
          </div>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="p-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-700 transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Scan Selector Pills */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1 scrollbar-thin">
        {scans.map((s) => {
          const isSelected = selectedScanId === s.scan_id;
          return (
            <button
              key={s.scan_id}
              onClick={() => setSelectedScanId(s.scan_id)}
              className={`px-3 py-1.5 rounded-xl border text-[10px] font-bold shrink-0 transition-all flex items-center space-x-2 ${
                isSelected
                  ? 'bg-teal-500 text-black border-teal-400 shadow-[0_0_12px_rgba(20,184,166,0.4)]'
                  : 'bg-slate-950/80 text-slate-300 border-slate-800 hover:border-teal-500/40'
              }`}
            >
              <span>{s.title.split('—')[0]}</span>
              <span className={`px-1.5 py-0.2 rounded text-[8px] font-black ${isSelected ? 'bg-black text-teal-300' : 'bg-slate-900 text-slate-400'}`}>
                {s.sensor_modality.replace('_', ' ')}
              </span>
            </button>
          );
        })}
      </div>

      {/* Main Analysis Display */}
      {analysisResult && (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
          
          {/* Left: Synthetic Aerial Image Canvas Simulation (7 cols) */}
          <div className="md:col-span-7 bg-slate-950 rounded-xl border border-slate-800 p-3 flex flex-col space-y-3 relative overflow-hidden">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-400 font-bold flex items-center space-x-1.5">
                <Layers className="w-3.5 h-3.5 text-teal-400" />
                <span>ORTHOMOSAIC RADAR OVERLAY</span>
              </span>
              <span className="text-teal-300 font-mono font-bold">
                {analysisResult.source_image_name}
              </span>
            </div>

            {/* Synthetic Multi-Band Tactical Canvas Box */}
            <div className="h-52 w-full rounded-lg bg-gradient-to-br from-slate-900 via-teal-950/30 to-blue-950/40 border border-teal-500/30 relative flex items-center justify-center overflow-hidden">
              {/* Radar Grid Lines */}
              <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f2b33_1px,transparent_1px),linear-gradient(to_bottom,#0f2b33_1px,transparent_1px)] bg-[size:24px_24px] opacity-40"></div>
              
              {/* Simulated Inundation Mask Polygon */}
              <div className="absolute inset-4 rounded-xl bg-teal-500/15 border-2 border-dashed border-teal-400/60 flex items-center justify-center">
                <span className="text-[10px] text-teal-300/80 font-bold bg-slate-950/90 px-2 py-0.5 rounded border border-teal-500/40">
                  FLOOD INUNDATION EXTENT ({analysisResult.flood_extent_percent}%)
                </span>
              </div>

              {/* Simulated Bounding Boxes */}
              {analysisResult.detections.map((d, i) => (
                <div
                  key={d.id}
                  style={{
                    top: `${d.bbox[0] * 75 + 10}%`,
                    left: `${d.bbox[1] * 75 + 10}%`,
                    width: `${(d.bbox[2] - d.bbox[0]) * 90 + 20}%`,
                    height: `${(d.bbox[3] - d.bbox[1]) * 60 + 20}%`
                  }}
                  className="absolute border-2 border-red-400/80 bg-red-500/10 rounded pointer-events-none flex items-start justify-start p-0.5"
                >
                  <span className="text-[8px] bg-red-950 text-red-200 px-1 rounded font-black leading-none">
                    {d.label.replace('_', ' ')} ({Math.round(d.confidence * 100)}%)
                  </span>
                </div>
              ))}

              <div className="absolute bottom-2 left-2 text-[9px] text-slate-400 bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800">
                Resolution: {analysisResult.metadata?.ground_sampling_distance_cm ? `${analysisResult.metadata.ground_sampling_distance_cm} cm/px` : 'SAR C-Band'}
              </div>
            </div>

            {/* Diagnostic Takeaway */}
            <div className="p-2.5 bg-teal-950/20 rounded-lg border border-teal-500/30 text-[11px] text-slate-300 font-sans leading-relaxed">
              <strong className="text-teal-300 font-mono uppercase">CV Diagnostic:</strong> {analysisResult.operational_takeaway}
            </div>
          </div>

          {/* Right: Metrics & Detected Objects Breakdown (5 cols) */}
          <div className="md:col-span-5 flex flex-col justify-between space-y-3">
            
            {/* Quick Summary Metrics Grid */}
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
                <span className="text-[9px] text-slate-500 uppercase block">FLOOD EXTENT</span>
                <span className="text-base font-black text-teal-300">{analysisResult.flood_extent_percent}%</span>
              </div>

              <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
                <span className="text-[9px] text-slate-500 uppercase block">DAMAGED STRUCTURES</span>
                <span className="text-base font-black text-red-400">{analysisResult.damaged_structures_count}</span>
              </div>

              <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
                <span className="text-[9px] text-slate-500 uppercase block">BLOCKED ROADS</span>
                <span className="text-base font-black text-amber-400">{analysisResult.blocked_roads_count}</span>
              </div>

              <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
                <span className="text-[9px] text-slate-500 uppercase block">STRANDED CLUSTERS</span>
                <span className="text-base font-black text-cyan-300">{analysisResult.trapped_clusters_count}</span>
              </div>
            </div>

            {/* Detected Objects List */}
            <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 space-y-2 flex-1">
              <div className="flex justify-between items-center text-[10px] text-slate-400 font-bold border-b border-slate-800 pb-1">
                <span>DETECTED TARGETS ({analysisResult.detections.length})</span>
                <span>CONFIDENCE</span>
              </div>
              <div className="space-y-1.5 max-h-36 overflow-y-auto scrollbar-thin">
                {analysisResult.detections.map((d) => (
                  <div key={d.id} className="flex justify-between items-center p-1.5 rounded bg-slate-900/60 border border-slate-800/80 text-[10px]">
                    <div className="flex items-center space-x-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-red-400"></span>
                      <span className="text-slate-200 capitalize">{d.label.replace('_', ' ')}</span>
                    </div>
                    <span className="text-teal-300 font-bold">{Math.round(d.confidence * 100)}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Bottom Confidence Bar */}
            <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900 border border-slate-800 text-[10px]">
              <span className="text-slate-400">Model Classification Confidence:</span>
              <ConfidenceBadge confidencePercent={analysisResult.overall_confidence * 100} size="sm" />
            </div>

          </div>

        </div>
      )}

    </div>
  );
};
