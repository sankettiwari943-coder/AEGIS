import React, { useState, useEffect } from 'react';
import { 
  MainNavMode, 
  DisasterEvent, 
  Zone, 
  RoadSegment, 
  Infrastructure, 
  RescueTeam, 
  PredictionResponse, 
  ZoneCascadingRisk, 
  SilentRiskAssessment 
} from './types';
import { api } from './services/api';
import { DemoProvider, useDemo } from './context/DemoContext';
import { Header } from './components/shell/Header';
import { DemoControllerBar } from './components/shell/DemoControllerBar';
import { DemoGuideModal } from './components/shell/DemoGuideModal';
import { DemoResetModal } from './components/shell/DemoResetModal';
import { AlertTicker } from './components/shell/AlertTicker';

import { CommandCenterPage } from './pages/CommandCenterPage';
import { LivePage } from './pages/LivePage';
import { PredictPage } from './pages/PredictPage';
import { SimulatePage } from './pages/SimulatePage';
import { MissionsPage } from './pages/MissionsPage';
import { EvidencePage } from './pages/EvidencePage';
import { AdaptivePage } from './pages/AdaptivePage';
import { AIPage } from './pages/AIPage';
import { SystemPage } from './pages/SystemPage';
import { TacticalAssistant } from './components/assistant/TacticalAssistant';

import { RefreshCw, AlertOctagon } from 'lucide-react';

const AppInner: React.FC = () => {
  const [currentMode, setCurrentMode] = useState<MainNavMode>('COMMAND');
  const [event, setEvent] = useState<DisasterEvent | null>(null);
  const [zones, setZones] = useState<Zone[]>([]);
  const [roads, setRoads] = useState<RoadSegment[]>([]);
  const [infrastructure, setInfrastructure] = useState<Infrastructure[]>([]);
  const [teams, setTeams] = useState<RescueTeam[]>([]);
  const [predictions, setPredictions] = useState<PredictionResponse | null>(null);
  const [cascadingRisks, setCascadingRisks] = useState<ZoneCascadingRisk[]>([]);
  const [silentRisks, setSilentRisks] = useState<SilentRiskAssessment[]>([]);
  const [selectedZone, setSelectedZone] = useState<Zone | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [
        eventData,
        zonesData,
        roadsData,
        infraData,
        teamsData,
        predData,
        cascadingData,
        silentData
      ] = await Promise.all([
        api.getCurrentEvent(),
        api.getZones(),
        api.getRoads(),
        api.getInfrastructure(),
        api.getTeams(),
        api.getPredictions(),
        api.getCascadingRisks(),
        api.getSilentRisks()
      ]);

      setEvent(eventData);
      setZones(zonesData);
      setRoads(roadsData);
      setInfrastructure(infraData);
      setTeams(teamsData);
      setPredictions(predData);
      setCascadingRisks(cascadingData);
      setSilentRisks(silentData);

      // Default select Zone 7 (critical river bend zone)
      const initialZone = zonesData.find(z => z.id === 'zone-7') || zonesData[0] || null;
      setSelectedZone(initialZone);
    } catch (err: any) {
      console.error('Failed to load initial AEGIS data:', err);
      setError(err?.message || 'Failed to establish connection to AEGIS intelligence engines.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Global Keyboard Shortcuts 1-8 for rapid Demo Navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }
      switch (e.key) {
        case '1':
          setCurrentMode('COMMAND');
          break;
        case '2':
          setCurrentMode('LIVE');
          break;
        case '3':
          setCurrentMode('PREDICT');
          break;
        case '4':
          setCurrentMode('SIMULATE');
          break;
        case '5':
          setCurrentMode('MISSIONS');
          break;
        case '6':
          setCurrentMode('EVIDENCE');
          break;
        case '7':
          setCurrentMode('ADAPTIVE');
          break;
        case '8':
          setCurrentMode('AI');
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleNavigate = (mode: MainNavMode, zoneId?: string) => {
    setCurrentMode(mode);
    if (zoneId) {
      const z = zones.find(item => item.id === zoneId);
      if (z) setSelectedZone(z);
    }
  };

  if (loading) {
    return (
      <div className="h-screen w-screen bg-[#060a12] flex flex-col items-center justify-center space-y-4 font-mono text-cyan-400">
        <div className="relative">
          <div className="w-16 h-16 rounded-full border-2 border-cyan-500/20 border-t-cyan-400 animate-spin"></div>
          <div className="absolute inset-0 flex items-center justify-center text-xs font-bold">
            Æ
          </div>
        </div>
        <div className="text-center space-y-1">
          <div className="text-sm font-bold tracking-widest uppercase">INITIALIZING AEGIS DISASTER CORE</div>
          <div className="text-xs text-slate-500">Connecting prediction, cascading, evidence & simulation engines...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen w-screen bg-[#060a12] flex flex-col items-center justify-center p-6 font-mono text-slate-300">
        <div className="max-w-md w-full hud-card p-6 rounded-2xl border border-red-500/50 space-y-4 text-center">
          <AlertOctagon className="w-12 h-12 text-red-400 mx-auto animate-pulse" />
          <h2 className="text-base font-black text-white">AEGIS ENGINE OFFLINE</h2>
          <p className="text-xs text-slate-400 font-sans">{error}</p>
          <button
            onClick={loadData}
            className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-black text-xs flex items-center justify-center space-x-2 mx-auto shadow-[0_0_15px_rgba(0,240,255,0.4)]"
          >
            <RefreshCw className="w-4 h-4" />
            <span>RETRY CONNECTION</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen bg-[#060a12] flex flex-col overflow-hidden select-none">
      
      {/* Top Controller Bar (Demo Mode, Timeline Scrubber, Guide & Reset) */}
      <DemoControllerBar currentMode={currentMode} onNavigate={handleNavigate} />

      {/* Main Tactical Header with 8 Navigation Modes */}
      <Header
        currentMode={currentMode}
        onSelectMode={setCurrentMode}
        event={event}
      />

      {/* Main Mode Content */}
      <main className="flex-1 overflow-hidden relative min-h-0">
        {currentMode === 'COMMAND' && (
          <CommandCenterPage
            event={event}
            zones={zones}
            roads={roads}
            infrastructure={infrastructure}
            rescueTeams={teams}
            selectedZone={selectedZone}
            onSelectZone={setSelectedZone}
            onNavigate={handleNavigate}
          />
        )}

        {currentMode === 'LIVE' && (
          <LivePage
            zones={zones}
            roads={roads}
            infrastructure={infrastructure}
            teams={teams}
            silentRisks={silentRisks}
            cascadingRisks={cascadingRisks}
            selectedZone={selectedZone}
            onSelectZone={setSelectedZone}
            onNavigate={handleNavigate}
          />
        )}

        {currentMode === 'PREDICT' && (
          <PredictPage
            zones={zones}
            roads={roads}
            infrastructure={infrastructure}
            teams={teams}
            selectedZone={selectedZone}
            onSelectZone={setSelectedZone}
            onNavigate={handleNavigate}
          />
        )}

        {currentMode === 'SIMULATE' && (
          <SimulatePage onNavigate={handleNavigate} />
        )}

        {currentMode === 'MISSIONS' && (
          <MissionsPage
            teams={teams}
            zones={zones}
            roads={roads}
            infrastructure={infrastructure}
            selectedZone={selectedZone}
            onNavigate={handleNavigate}
          />
        )}

        {currentMode === 'EVIDENCE' && (
          <EvidencePage onNavigate={handleNavigate} />
        )}

        {currentMode === 'ADAPTIVE' && (
          <AdaptivePage onNavigate={handleNavigate} />
        )}

        {currentMode === 'AI' && (
          <AIPage
            onNavigate={handleNavigate}
            initialZoneId={selectedZone?.id || 'zone-7'}
          />
        )}

        {currentMode === 'SYSTEM' && (
          <SystemPage />
        )}
      </main>

      {/* Floating Tactical AI Assistant */}
      <TacticalAssistant
        currentMode={currentMode}
        selectedZoneId={selectedZone?.id}
        onNavigate={handleNavigate}
      />

      {/* Bottom Alert Ticker */}
      <AlertTicker onNavigate={handleNavigate} />

      {/* Interactive Demo Presentation Guide Modal */}
      <DemoGuideModal onNavigate={handleNavigate} />

      {/* Scenario Reset Confirmation Modal */}
      <DemoResetModal />

    </div>
  );
};

export const App: React.FC = () => {
  return (
    <DemoProvider>
      <AppInner />
    </DemoProvider>
  );
};

export default App;
