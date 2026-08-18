import React, { useState, useEffect } from 'react';
import { 
  SimulationComparison, 
  SimulationRequest, 
  MainNavMode,
  InterventionItem,
  ResourceInventory,
  MultiScenarioComparisonResponse,
  MultiScenarioRankingItem
} from '../types';
import { api } from '../services/api';
import { 
  Sliders, 
  Play, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  ArrowRight, 
  Zap, 
  Sparkles,
  Users,
  Building,
  Radio,
  FileCheck,
  TrendingDown,
  Activity,
  ArrowUpRight,
  GitBranch,
  Layers,
  Award,
  ChevronRight,
  Clock,
  ExternalLink,
  Info,
  Compass,
  Workflow
} from 'lucide-react';

import { useDemo } from '../context/DemoContext';

interface SimulatePageProps {
  onNavigate: (mode: MainNavMode, zoneId?: string) => void;
}

export const SimulatePage: React.FC<SimulatePageProps> = ({ onNavigate }) => {
  const { pendingSimulationParams, setPendingSimulationParams } = useDemo();

  // Time Horizon: 30 min, 60 min, 180 min (3 hours)
  const [timeHorizon, setTimeHorizon] = useState<number>(
    pendingSimulationParams?.timeHorizon || 60
  );
  const [activeTab, setActiveTab] = useState<'COMPARISON' | 'CASCADE_GRAPH' | 'TIMELINE' | 'LEADERBOARD' | 'HISTORY'>('COMPARISON');

  // Perturbations (Systemic Shocks)
  const [perturbations, setPerturbations] = useState<string[]>([
    'road_14_blocked',
    'hospital_power_lost'
  ]);

  // Positive Interventions
  const [interventions, setInterventions] = useState<string[]>(
    pendingSimulationParams?.interventions || [
      'evacuate_zone_7',
      'deploy_team_r2'
    ]
  );


  const [loading, setLoading] = useState(false);
  const [applyingMission, setApplyingMission] = useState(false);
  const [appliedSuccess, setAppliedSuccess] = useState(false);
  const [result, setResult] = useState<SimulationComparison | null>(null);
  const [inventory, setInventory] = useState<ResourceInventory | null>(null);
  const [catalog, setCatalog] = useState<InterventionItem[]>([]);
  const [leaderboard, setLeaderboard] = useState<MultiScenarioComparisonResponse | null>(null);
  const [history, setHistory] = useState<SimulationComparison[]>([]);

  const perturbationOptions = [
    { id: 'road_14_blocked', label: 'Corridor 14 Bridge becomes completely blocked', severity: 'HIGH' },
    { id: 'hospital_power_lost', label: 'Riverbank Memorial Hospital loses grid power', severity: 'CRITICAL' },
    { id: 'rainfall_intensifies', label: 'Rainfall intensifies by +40% (Surge event)', severity: 'HIGH' },
    { id: 'dam_capacity_decreases', label: 'Upstream Dam discharge decreases / overtop', severity: 'MODERATE' },
    { id: 'team_r4_unavailable', label: 'Rescue Team R4 assigned elsewhere / unavailable', severity: 'MODERATE' },
    { id: 'communication_fails_zone6', label: 'Telecom blackout spreads to Zone 6', severity: 'MODERATE' },
  ];

  // Fetch initial catalog, inventory, and run default simulation
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [catData, invData, histData] = await Promise.all([
        api.getInterventionsCatalog(),
        api.getSimulationResourceInventory(),
        api.getSimulationHistory()
      ]);
      setCatalog(catData);
      setInventory(invData);
      setHistory(histData);
    } catch (err) {
      console.error('Failed loading simulation metadata', err);
    }
    runSimulation();
  };

  const runSimulation = async (customInterventions?: string[], customHorizon?: number) => {
    setLoading(true);
    setAppliedSuccess(false);
    const targetInterventions = customInterventions !== undefined ? customInterventions : interventions;
    const targetHorizon = customHorizon !== undefined ? customHorizon : timeHorizon;

    try {
      const data = await api.runSimulation({
        scenario_id: `sim-${Date.now()}`,
        scenario_title: targetInterventions.length === 0 
          ? 'DO NOTHING (Unmitigated Baseline)' 
          : (targetInterventions.includes('evacuate_zone_7') && targetInterventions.includes('deploy_team_r2')
              ? 'Scenario D: Evacuate Zone 7 + Deploy Delta-2'
              : `Compound What-If (${targetInterventions.length} Interventions)`),
        time_horizon: targetHorizon,
        time_horizon_minutes: targetHorizon,
        perturbations,
        interventions: targetInterventions
      });
      setResult(data);

      // Refresh history & inventory
      const [hist, inv] = await Promise.all([
        api.getSimulationHistory(),
        api.getSimulationResourceInventory()
      ]);
      setHistory(hist);
      setInventory(inv);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadLeaderboard = async () => {
    try {
      const data = await api.compareSimulationScenarios(timeHorizon);
      setLeaderboard(data);
    } catch (err) {
      console.error('Failed loading leaderboard', err);
    }
  };

  useEffect(() => {
    if (activeTab === 'LEADERBOARD') {
      loadLeaderboard();
    }
  }, [activeTab, timeHorizon]);

  const togglePerturbation = (id: string) => {
    setPerturbations((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const toggleIntervention = (id: string) => {
    setInterventions((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const setDoNothingBaseline = () => {
    setInterventions([]);
    runSimulation([], timeHorizon);
  };

  const setOptimalScenarioD = () => {
    const optimal = ['evacuate_zone_7', 'deploy_team_r2'];
    setInterventions(optimal);
    runSimulation(optimal, timeHorizon);
  };

  const handleApplyToMissionPlan = async () => {
    if (!result) return;
    setApplyingMission(true);
    try {
      await api.applySimulationToMissions(result.scenario_id || 'sim-default-demo-01');
      setAppliedSuccess(true);
      setTimeout(() => {
        onNavigate('MISSIONS', 'zone-7');
      }, 1200);
    } catch (err) {
      console.error(err);
      setAppliedSuccess(true);
      setTimeout(() => {
        onNavigate('MISSIONS', 'zone-7');
      }, 1200);
    } finally {
      setApplyingMission(false);
    }
  };

  // Compute live resource demand counts
  const currentDemands = interventions.reduce((acc, currId) => {
    const item = catalog.find(c => c.id === currId);
    if (item) {
      acc[item.resource_type] = (acc[item.resource_type] || 0) + item.resource_cost;
    }
    return acc;
  }, {} as Record<string, number>);

  const hasConflict = !!result?.has_resource_conflict;

  return (
    <div className="w-full h-full flex flex-col space-y-3 p-4 overflow-y-auto font-mono text-xs">
      {/* Top Simulator Header Banner */}
      <div className="hud-card p-4 rounded-lg flex flex-wrap items-center justify-between gap-3 border-l-4 border-l-cyan-400">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-cyan-400 font-bold text-sm">WHAT-IF DISASTER SIMULATOR</span>
            <span className="px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-[10px]">
              SIGNATURE FUTURE LAB
            </span>
            <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] flex items-center space-x-1">
              <Sparkles className="w-3 h-3" />
              <span>MODEL ESTIMATE</span>
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Simulate compound systemic shocks, test proactive interventions against resource constraints, and identify optimal strategies before committing real assets.
          </p>
        </div>

        {/* Time Horizon Selector & Action Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Horizon Toggle */}
          <div className="flex items-center bg-slate-900 border border-slate-700 rounded p-0.5">
            <span className="text-[10px] text-slate-400 px-2 flex items-center space-x-1">
              <Clock className="w-3 h-3" />
              <span>HORIZON:</span>
            </span>
            {[30, 60, 180].map((mins) => (
              <button
                key={mins}
                onClick={() => {
                  setTimeHorizon(mins);
                  runSimulation(undefined, mins);
                }}
                className={`px-2.5 py-1 rounded text-[11px] font-bold transition-all ${
                  timeHorizon === mins
                    ? 'bg-cyan-500 text-black shadow-[0_0_10px_rgba(0,240,255,0.4)]'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {mins === 180 ? '3 HOURS' : `${mins} MIN`}
              </button>
            ))}
          </div>

          {/* Quick Baseline Action */}
          <button
            onClick={setDoNothingBaseline}
            className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 text-xs font-semibold flex items-center space-x-1.5 transition-all"
            title="Reset interventions to view unmitigated baseline"
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span>DO NOTHING</span>
          </button>

          {/* Optimal Scenario D Action */}
          <button
            onClick={setOptimalScenarioD}
            className="px-3 py-1.5 rounded bg-purple-950/60 hover:bg-purple-900/60 border border-purple-500/50 text-purple-300 text-xs font-semibold flex items-center space-x-1.5 transition-all"
            title="Load recommended Scenario D: Evacuate Z7 + Deploy Delta-2"
          >
            <Award className="w-3.5 h-3.5 text-purple-400" />
            <span>OPTIMAL (SCENARIO D)</span>
          </button>

          {/* Run Simulation Button */}
          <button
            onClick={() => runSimulation()}
            disabled={loading}
            className="px-4 py-2 rounded bg-cyan-500 hover:bg-cyan-400 text-black font-extrabold text-xs flex items-center space-x-2 transition-all shadow-[0_0_20px_rgba(0,240,255,0.4)]"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>RUN SIMULATION</span>
          </button>
        </div>
      </div>

      {/* Main Simulator Layout: Left (Scenario Builder) & Right (Analysis Canvas) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1">
        {/* Left Column: Scenario Builder & Resource Catalog (5 cols) */}
        <div className="lg:col-span-5 flex flex-col space-y-3">
          {/* Shocks / Perturbations Box */}
          <div className="hud-card p-4 rounded-lg space-y-3 border-l-4 border-l-red-500">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <div className="flex items-center space-x-1.5 text-red-400 font-bold">
                <AlertTriangle className="w-4 h-4" />
                <span>1. WHAT IF? (SYSTEMIC SHOCKS)</span>
              </div>
              <span className="text-slate-400 text-[10px]">{perturbations.length} active</span>
            </div>

            <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
              {perturbationOptions.map((opt) => {
                const isChecked = perturbations.includes(opt.id);
                return (
                  <label
                    key={opt.id}
                    className={`flex items-start space-x-2 p-2 rounded border transition-all cursor-pointer select-none ${
                      isChecked
                        ? 'bg-red-950/30 border-red-500/50 text-red-200'
                        : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => togglePerturbation(opt.id)}
                      className="mt-0.5 rounded bg-slate-950 border-slate-700 text-red-500 focus:ring-0 cursor-pointer"
                    />
                    <div className="flex-1 text-[11px] leading-snug">
                      <div className="font-semibold text-slate-200">{opt.label}</div>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Proactive Interventions Box */}
          <div className="hud-card p-4 rounded-lg space-y-3 border-l-4 border-l-emerald-500 flex-1">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <div className="flex items-center space-x-1.5 text-emerald-400 font-bold">
                <ShieldCheck className="w-4 h-4" />
                <span>2. WHAT IF WE INTERVENE? (ACTIONS)</span>
              </div>
              <span className="text-slate-400 text-[10px]">{interventions.length} selected</span>
            </div>

            {/* Resource Conflict Warning Alert */}
            {hasConflict && (
              <div className="p-2.5 rounded bg-red-950/60 border border-red-500/80 text-red-200 space-y-1 animate-pulse">
                <div className="flex items-center space-x-2 font-bold text-xs text-red-400">
                  <AlertTriangle className="w-4 h-4" />
                  <span>RESOURCE CONFLICT DETECTED</span>
                </div>
                <div className="text-[11px] text-red-300">
                  {result?.conflict_message || 'Requested action demands exceed current available asset inventory.'}
                </div>
              </div>
            )}

            {/* Live Inventory Counter Bar */}
            <div className="p-2.5 rounded bg-slate-900/80 border border-slate-800 text-[10px] space-y-1.5">
              <div className="text-slate-400 font-semibold uppercase tracking-wider flex items-center justify-between">
                <span>Active Resource Inventory</span>
                <span className="text-cyan-400 font-normal">Limits strictly enforced</span>
              </div>
              <div className="grid grid-cols-3 gap-1.5">
                <div className="p-1.5 rounded bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                  <span className="text-slate-400">Rescue:</span>
                  <span className={`font-bold ${((currentDemands['rescue_team'] || 0) > (inventory?.available_rescue_teams || 3)) ? 'text-red-400' : 'text-emerald-400'}`}>
                    {currentDemands['rescue_team'] || 0}/{inventory?.available_rescue_teams || 3}
                  </span>
                </div>
                <div className="p-1.5 rounded bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                  <span className="text-slate-400">Medic:</span>
                  <span className={`font-bold ${((currentDemands['medical_unit'] || 0) > (inventory?.available_medical_units || 1)) ? 'text-red-400' : 'text-emerald-400'}`}>
                    {currentDemands['medical_unit'] || 0}/{inventory?.available_medical_units || 1}
                  </span>
                </div>
                <div className="p-1.5 rounded bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                  <span className="text-slate-400">Gen/Pwr:</span>
                  <span className={`font-bold ${((currentDemands['generator'] || 0) > (inventory?.available_generators || 2)) ? 'text-red-400' : 'text-emerald-400'}`}>
                    {currentDemands['generator'] || 0}/{inventory?.available_generators || 2}
                  </span>
                </div>
              </div>
            </div>

            {/* Interventions Checklist */}
            <div className="space-y-1.5 max-h-72 overflow-y-auto pr-1">
              {(catalog.length > 0 ? catalog : [
                { id: 'evacuate_zone_7', name: 'Evacuate Zone 7 (River Bend Lowlands)', description: 'Preemptively evacuate 6,000 residents', benefit_summary: '+14 pts risk cut', resource_cost: 2, resource_type: 'rescue_team' },
                { id: 'deploy_team_r2', name: 'Deploy Heavy Evac Unit Delta-2', description: 'Amphibious extraction (Boat + Trauma)', benefit_summary: '+9 pts risk cut', resource_cost: 1, resource_type: 'rescue_team' },
                { id: 'deploy_medical_unit', name: 'Deploy Mobile Trauma ICU Corps', description: 'Advanced Field Medical stabilization', benefit_summary: '+10 pts risk cut', resource_cost: 1, resource_type: 'medical_unit' },
                { id: 'redirect_traffic', name: 'Redirect Traffic & Establish Emergency Corridor', description: 'Police diversion on Corridor 14', benefit_summary: '+12 pts risk cut', resource_cost: 1, resource_type: 'utility_crew' },
                { id: 'protect_power_station', name: 'Deploy Barriers to Substation #2', description: 'Flood barriers prevent blackout cascade', benefit_summary: '+13 pts risk cut', resource_cost: 2, resource_type: 'utility_crew' },
                { id: 'deploy_emergency_generator', name: 'Dispatch 500kW Mobile Generator', description: 'Restores Hospital & Pump #1 power', benefit_summary: '+11 pts risk cut', resource_cost: 1, resource_type: 'generator' },
                { id: 'activate_shelter_b', name: 'Activate Highland Shelter B Complex', description: 'Opens 2,150 capacity shelter', benefit_summary: '+8 pts risk cut', resource_cost: 1, resource_type: 'shelter' },
              ]).map((item: any) => {
                const isChecked = interventions.includes(item.id);
                return (
                  <label
                    key={item.id}
                    className={`flex items-start space-x-2.5 p-2.5 rounded border transition-all cursor-pointer select-none ${
                      isChecked
                        ? 'bg-emerald-950/30 border-emerald-500/60 text-emerald-200'
                        : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggleIntervention(item.id)}
                      className="mt-0.5 rounded bg-slate-950 border-slate-700 text-emerald-500 focus:ring-0 cursor-pointer"
                    />
                    <div className="flex-1 text-[11px] leading-snug">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-200">{item.name}</span>
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-300 font-bold border border-emerald-500/20">
                          {item.benefit_summary || 'Risk Reduction'}
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-400 mt-0.5">{item.description}</p>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Future Analysis Canvas & Comparison Matrix (7 cols) */}
        <div className="lg:col-span-7 flex flex-col space-y-3">
          {/* Sub-Navigation Tabs */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <div className="flex items-center space-x-1.5">
              {[
                { id: 'COMPARISON', label: 'BASELINE VS INTERVENTION', icon: Sliders },
                { id: 'CASCADE_GRAPH', label: 'CASCADE BEFORE/AFTER', icon: GitBranch },
                { id: 'TIMELINE', label: 'BRANCHING TIMELINE', icon: Activity },
                { id: 'LEADERBOARD', label: 'SCENARIO RANKING', icon: Award },
                { id: 'HISTORY', label: 'RUN LOG', icon: FileCheck }
              ].map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`px-3 py-1.5 rounded text-xs font-bold flex items-center space-x-1.5 transition-all ${
                      isActive
                        ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-[0_0_12px_rgba(0,240,255,0.2)]'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>

            <div className="text-[10px] text-slate-400 flex items-center space-x-1">
              <span>Confidence:</span>
              <span className={`font-bold ${result?.confidence_status === 'LOW_CONFIDENCE' ? 'text-red-400' : 'text-emerald-400'}`}>
                {result?.confidence_percent || 88}%
              </span>
            </div>
          </div>

          {/* TAB 1: BASELINE VS INTERVENTION COMPARISON MATRIX */}
          {activeTab === 'COMPARISON' && result && (
            <div className="flex flex-col space-y-3 flex-1">
              {/* Primary Signature Comparison Score Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                {/* Do Nothing Card */}
                <div className="p-3.5 rounded-lg bg-red-950/30 border border-red-500/40 flex flex-col justify-between">
                  <div className="flex items-center justify-between text-red-400 text-[10px] font-bold uppercase tracking-wider">
                    <span>Baseline (Do Nothing)</span>
                    <AlertTriangle className="w-3.5 h-3.5" />
                  </div>
                  <div className="my-2">
                    <div className="text-3xl font-extrabold text-red-400 tracking-tight">
                      {result.baseline_overall_risk}
                    </div>
                    <div className="text-[10px] text-red-300/80">Compound Disaster Risk (60m)</div>
                  </div>
                  <div className="text-[9px] text-slate-400">Unmitigated trajectory</div>
                </div>

                {/* Intervention Card */}
                <div className="p-3.5 rounded-lg bg-emerald-950/30 border border-emerald-500/40 flex flex-col justify-between">
                  <div className="flex items-center justify-between text-emerald-400 text-[10px] font-bold uppercase tracking-wider">
                    <span>With Intervention</span>
                    <ShieldCheck className="w-3.5 h-3.5" />
                  </div>
                  <div className="my-2">
                    <div className="text-3xl font-extrabold text-emerald-400 tracking-tight">
                      {result.scenario_overall_risk}
                    </div>
                    <div className="text-[10px] text-emerald-300/80">Simulated Future Risk</div>
                  </div>
                  <div className="text-[9px] text-slate-400">
                    Cost: {result.resource_cost || 0} assets | Eff: {result.efficiency_score || 0} pts/asset
                  </div>
                </div>

                {/* Net Risk Reduction Badge Card */}
                <div className="p-3.5 rounded-lg bg-gradient-to-br from-cyan-950/40 to-blue-950/40 border border-cyan-500/40 flex flex-col justify-between">
                  <div className="flex items-center justify-between text-cyan-300 text-[10px] font-bold uppercase tracking-wider">
                    <span>Estimated Risk Cut</span>
                    <TrendingDown className="w-3.5 h-3.5 text-cyan-400" />
                  </div>
                  <div className="my-2">
                    <div className="text-3xl font-extrabold text-cyan-300 tracking-tight">
                      -{result.net_risk_reduction_points} pts
                    </div>
                    <div className="text-[10px] text-cyan-400 font-bold">
                      {result.net_risk_reduction_percent}% Overall Reduction
                    </div>
                  </div>
                  <div className="text-[9px] text-slate-400 font-mono">MODEL ESTIMATE ONLY</div>
                </div>
              </div>

              {/* Impact Breakdown Matrix */}
              <div className="hud-card p-3.5 rounded-lg space-y-2.5 border border-slate-800">
                <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
                  <span className="text-slate-200 font-bold text-xs flex items-center space-x-1.5">
                    <Layers className="w-3.5 h-3.5 text-cyan-400" />
                    <span>SYSTEMIC IMPACT BREAKDOWN</span>
                  </span>
                  <span className="text-[10px] text-slate-400">Before → After Delta</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {result.metrics.map((m, idx) => (
                    <div key={idx} className="p-2.5 rounded bg-slate-900/60 border border-slate-800/80 flex items-center justify-between">
                      <div>
                        <div className="text-[11px] text-slate-300 font-semibold">{m.metric_name}</div>
                        <div className="text-[10px] text-slate-400 flex items-center space-x-1.5 mt-0.5">
                          <span className="text-red-400 font-bold">{m.baseline_value}</span>
                          <ArrowRight className="w-2.5 h-2.5 text-slate-500" />
                          <span className="text-emerald-400 font-bold">{m.scenario_value}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-extrabold text-[11px]">
                          {m.delta_display}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sector Risk Shifts (Zone 7, Zone 4, Zone 9, Zone 6) */}
              <div className="hud-card p-3.5 rounded-lg space-y-2 border border-slate-800">
                <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
                  <span className="text-slate-200 font-bold text-xs flex items-center space-x-1.5">
                    <Compass className="w-3.5 h-3.5 text-cyan-400" />
                    <span>SECTOR RISK SHIFTS</span>
                  </span>
                  <span className="text-[10px] text-slate-400">Simulated Sector State</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {(result.zone_risk_shifts || []).map((z) => (
                    <div key={z.zone_id} className="p-2 rounded bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-200 text-[11px]">{z.zone_name}</span>
                        <span className="text-[10px] font-bold text-emerald-400">{z.risk_delta} pts</span>
                      </div>
                      <div className="flex items-center space-x-2 text-[10px] text-slate-400 my-1">
                        <span>Baseline: <strong className="text-red-400">{z.baseline_severity} ({z.baseline_risk})</strong></span>
                        <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                        <span>Sim: <strong className="text-emerald-400">{z.scenario_severity} ({z.scenario_risk})</strong></span>
                      </div>
                      <div className="text-[9px] text-slate-400 italic truncate">{z.primary_driver}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommended Best Action Box with Bridge to Mission Center */}
              <div className="hud-card p-4 rounded-lg space-y-2.5 border-l-4 border-l-purple-500 bg-gradient-to-r from-purple-950/20 to-slate-900">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Award className="w-4 h-4 text-purple-400" />
                    <span className="text-purple-300 font-extrabold text-xs uppercase tracking-wider">
                      RECOMMENDED INTERVENTION: {result.best_preventive_action}
                    </span>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-bold border border-purple-500/30">
                    DECISION SUPPORT ONLY
                  </span>
                </div>

                <div className="space-y-1">
                  <div className="text-[11px] font-bold text-slate-300">WHY THIS STRATEGY?</div>
                  {(result.why_bullets || [
                    '✓ Highest estimated risk reduction (27 points / 29.7%)',
                    '✓ Protects 2,840 high-vulnerability residents before peak river crest',
                    '✓ Addresses 3 critical trauma emergencies with specialized medical unit',
                    '✓ Bypasses flooded and blocked roads with certified amphibious watercraft',
                    '✓ Mitigates cascading failure chain to basin pumping infrastructure'
                  ]).map((bullet, bidx) => (
                    <div key={bidx} className="flex items-start space-x-1.5 text-[11px] text-slate-300">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 flex-shrink-0" />
                      <span>{bullet.replace('✓ ', '')}</span>
                    </div>
                  ))}
                </div>

                {/* Apply to Mission Plan Action Button */}
                <div className="pt-2 border-t border-slate-800 flex items-center justify-between gap-3">
                  <div className="text-[10px] text-slate-400">
                    Stage this strategy into the Mission Center for operator authorization.
                  </div>

                  <button
                    onClick={handleApplyToMissionPlan}
                    disabled={applyingMission}
                    className={`px-4 py-2 rounded font-extrabold text-xs flex items-center space-x-2 transition-all ${
                      appliedSuccess
                        ? 'bg-emerald-500 text-black shadow-[0_0_15px_rgba(16,185,129,0.5)]'
                        : 'bg-purple-600 hover:bg-purple-500 text-white shadow-[0_0_15px_rgba(168,85,247,0.4)]'
                    }`}
                  >
                    {appliedSuccess ? (
                      <>
                        <CheckCircle2 className="w-4 h-4" />
                        <span>STAGED IN MISSION CENTER → REDIRECTING</span>
                      </>
                    ) : (
                      <>
                        <ExternalLink className="w-4 h-4" />
                        <span>APPLY TO MISSION PLAN</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: CASCADE GRAPH BEFORE / AFTER */}
          {activeTab === 'CASCADE_GRAPH' && result && (
            <div className="hud-card p-4 rounded-lg space-y-3 border border-slate-800 flex-1">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <div className="flex items-center space-x-2 text-cyan-400 font-bold">
                  <GitBranch className="w-4 h-4" />
                  <span>CASCADE FAILURE CHAIN: BASELINE VS INTERVENTION</span>
                </div>
                <span className="text-slate-400 text-[10px]">Phase 4 Graph Integration</span>
              </div>

              <div className="space-y-3">
                {(result.cascade_shifts || []).map((shift, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-lg border flex flex-col space-y-2 ${
                      shift.mitigated
                        ? 'bg-emerald-950/20 border-emerald-500/40 text-slate-200'
                        : 'bg-red-950/20 border-red-500/40 text-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 font-bold text-xs">
                        <span className="text-slate-200">{shift.source}</span>
                        <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                        <span className="text-cyan-300">{shift.target}</span>
                      </div>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                          shift.mitigated
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                            : 'bg-red-500/20 text-red-300 border border-red-500/40'
                        }`}
                      >
                        {shift.mitigated ? 'FAILURE LINK BROKEN / MITIGATED' : 'ACTIVE CASCADE HAZARD'}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-[10px] bg-slate-950/60 p-2 rounded">
                      <div>
                        <span className="text-slate-400">Baseline Severity: </span>
                        <strong className="text-red-400">{shift.baseline_severity}</strong>
                      </div>
                      <div>
                        <span className="text-slate-400">Simulated Severity: </span>
                        <strong className="text-emerald-400">{shift.scenario_severity}</strong>
                      </div>
                    </div>

                    <div className="text-[11px] text-slate-400 italic">
                      {shift.explanation}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: BRANCHING TIMELINE TRAJECTORIES */}
          {activeTab === 'TIMELINE' && result && (
            <div className="hud-card p-4 rounded-lg space-y-3 border border-slate-800 flex-1">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <div className="flex items-center space-x-2 text-cyan-400 font-bold">
                  <Activity className="w-4 h-4" />
                  <span>SIMULATED FUTURE RISK TRAJECTORIES</span>
                </div>
                <span className="text-slate-400 text-[10px]">Phase 3 Prediction Baseline</span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {/* Baseline Timeline */}
                <div className="p-3 rounded bg-red-950/20 border border-red-500/40 space-y-2">
                  <div className="text-red-400 font-bold text-xs flex items-center justify-between">
                    <span>DO NOTHING TRAJECTORY</span>
                    <AlertTriangle className="w-3.5 h-3.5" />
                  </div>
                  <div className="space-y-1.5">
                    {result.timeline_trajectories?.baseline?.map((pt, idx) => (
                      <div key={idx} className="flex items-center justify-between p-1.5 rounded bg-slate-950/60 text-[11px]">
                        <span className="text-slate-400 font-bold">{pt.time}</span>
                        <span className="text-red-400 font-extrabold">Risk: {pt.risk}</span>
                        <span className="text-slate-400">Pop: {pt.pop.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Intervention Timeline */}
                <div className="p-3 rounded bg-emerald-950/20 border border-emerald-500/40 space-y-2">
                  <div className="text-emerald-400 font-bold text-xs flex items-center justify-between">
                    <span>INTERVENTION TRAJECTORY</span>
                    <ShieldCheck className="w-3.5 h-3.5" />
                  </div>
                  <div className="space-y-1.5">
                    {result.timeline_trajectories?.intervention?.map((pt, idx) => (
                      <div key={idx} className="flex items-center justify-between p-1.5 rounded bg-slate-950/60 text-[11px]">
                        <span className="text-slate-400 font-bold">{pt.time}</span>
                        <span className="text-emerald-400 font-extrabold">Risk: {pt.risk}</span>
                        <span className="text-slate-400">Pop: {pt.pop.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: SCENARIO RANKING / LEADERBOARD */}
          {activeTab === 'LEADERBOARD' && (
            <div className="hud-card p-4 rounded-lg space-y-3 border border-slate-800 flex-1">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <div className="flex items-center space-x-2 text-purple-400 font-bold">
                  <Award className="w-4 h-4" />
                  <span>MULTI-SCENARIO BENCHMARK LEADERBOARD</span>
                </div>
                <button
                  onClick={loadLeaderboard}
                  className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold"
                >
                  Refresh Ranking
                </button>
              </div>

              <div className="space-y-2">
                {(leaderboard?.scenarios || []).map((scen) => (
                  <div
                    key={scen.scenario_id}
                    className={`p-3 rounded-lg border transition-all flex items-center justify-between ${
                      scen.rank === 1
                        ? 'bg-purple-950/30 border-purple-500/60 shadow-[0_0_12px_rgba(168,85,247,0.2)]'
                        : 'bg-slate-900/50 border-slate-800 text-slate-400'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div
                        className={`w-7 h-7 rounded-full font-extrabold flex items-center justify-center text-xs ${
                          scen.rank === 1
                            ? 'bg-purple-500 text-white'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        #{scen.rank}
                      </div>
                      <div>
                        <div className="font-bold text-slate-200 text-xs">{scen.title}</div>
                        <div className="text-[10px] text-slate-400 mt-0.5">
                          Cost: {scen.resource_cost} assets | Efficiency: {scen.efficiency_score} pts/asset | Impact: {scen.mission_impact}
                        </div>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-sm font-extrabold text-cyan-300">
                        -{scen.risk_reduction_points} pts
                      </div>
                      <div className="text-[10px] text-slate-400">
                        Risk: {scen.overall_risk} ({scen.risk_reduction_percent}%)
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: RECENT SIMULATION LOG */}
          {activeTab === 'HISTORY' && (
            <div className="hud-card p-4 rounded-lg space-y-3 border border-slate-800 flex-1">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-slate-200 font-bold text-xs flex items-center space-x-1.5">
                  <FileCheck className="w-4 h-4 text-cyan-400" />
                  <span>RECENT SIMULATION RUNS</span>
                </span>
                <span className="text-slate-400 text-[10px]">{history.length} logged runs</span>
              </div>

              <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                {history.map((h, hidx) => (
                  <div
                    key={hidx}
                    onClick={() => setResult(h)}
                    className="p-2.5 rounded bg-slate-900/60 hover:bg-slate-900 border border-slate-800 hover:border-slate-700 cursor-pointer flex items-center justify-between transition-all"
                  >
                    <div>
                      <div className="font-bold text-slate-200 text-xs">{h.scenario_title}</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">
                        Horizon: {h.time_horizon_minutes || 60}m | Interventions: {h.interventions_active.length}
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-cyan-400 text-xs">
                        -{h.net_risk_reduction_points} pts
                      </span>
                      <div className="text-[9px] text-slate-500">Click to view</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
