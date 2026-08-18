import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '../services/api';
import {
  HealthResponse,
  DemoStateResponse,
  DemoTimelineStep,
  SimulationPreloadParams,
  MainNavMode
} from '../types';

interface DemoContextType {
  scenarioTime: string;
  setScenarioTime: (time: string) => void;
  scenarioIntensity: 'Normal' | 'Escalating' | 'Critical';
  setScenarioIntensity: (intensity: 'Normal' | 'Escalating' | 'Critical') => void;
  activeDemoStep: number;
  setActiveDemoStep: (step: number) => void;
  demoGuideOpen: boolean;
  setDemoGuideOpen: (open: boolean) => void;
  showResetModal: boolean;
  setShowResetModal: (show: boolean) => void;
  health: HealthResponse | null;
  demoState: DemoStateResponse | null;
  pendingSimulationParams: SimulationPreloadParams | null;
  setPendingSimulationParams: (params: SimulationPreloadParams | null) => void;
  executeResetDemo: () => Promise<void>;
  refreshHealth: () => Promise<void>;
  currentTimelineStepData: DemoTimelineStep | undefined;
}

const DemoContext = createContext<DemoContextType | undefined>(undefined);

export const DemoProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [scenarioTime, setScenarioTime] = useState<string>('T+0');
  const [scenarioIntensity, setScenarioIntensity] = useState<'Normal' | 'Escalating' | 'Critical'>('Escalating');
  const [activeDemoStep, setActiveDemoStep] = useState<number>(1);
  const [demoGuideOpen, setDemoGuideOpen] = useState<boolean>(false);
  const [showResetModal, setShowResetModal] = useState<boolean>(false);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [demoState, setDemoState] = useState<DemoStateResponse | null>(null);
  const [pendingSimulationParams, setPendingSimulationParams] = useState<SimulationPreloadParams | null>(null);

  const refreshHealth = async () => {
    try {
      const h = await api.getHealthStatus();
      setHealth(h);
    } catch (err) {
      console.error('Failed to load health status:', err);
    }
  };

  const fetchDemoState = async () => {
    try {
      const st = await api.getDemoState();
      setDemoState(st);
    } catch (err) {
      console.error('Failed to load demo state:', err);
    }
  };

  useEffect(() => {
    refreshHealth();
    fetchDemoState();
  }, []);

  const executeResetDemo = async () => {
    try {
      await api.resetDemo();
      setScenarioTime('T+0');
      setScenarioIntensity('Escalating');
      setActiveDemoStep(1);
      setPendingSimulationParams(null);
      setShowResetModal(false);
      await Promise.all([refreshHealth(), fetchDemoState()]);
    } catch (err) {
      console.error('Failed to reset demo:', err);
    }
  };

  const currentTimelineStepData = demoState?.timeline_steps.find((s) => s.time === scenarioTime);

  useEffect(() => {
    if (currentTimelineStepData) {
      if (currentTimelineStepData.zone7_risk >= 90 || currentTimelineStepData.zone7_isolation_minutes === 0) {
        setScenarioIntensity('Critical');
      } else if (currentTimelineStepData.zone7_risk >= 50) {
        setScenarioIntensity('Escalating');
      } else {
        setScenarioIntensity('Normal');
      }
    } else if (demoState?.intensity) {
      const norm = demoState.intensity.toLowerCase();
      if (norm.includes('crit')) setScenarioIntensity('Critical');
      else if (norm.includes('esca')) setScenarioIntensity('Escalating');
      else setScenarioIntensity('Normal');
    }
  }, [scenarioTime, currentTimelineStepData, demoState]);

  return (
    <DemoContext.Provider
      value={{
        scenarioTime,
        setScenarioTime,
        scenarioIntensity,
        setScenarioIntensity,
        activeDemoStep,
        setActiveDemoStep,
        demoGuideOpen,
        setDemoGuideOpen,
        showResetModal,
        setShowResetModal,
        health,
        demoState,
        pendingSimulationParams,
        setPendingSimulationParams,
        executeResetDemo,
        refreshHealth,
        currentTimelineStepData
      }}
    >
      {children}
    </DemoContext.Provider>
  );
};

export const useDemo = (): DemoContextType => {
  const context = useContext(DemoContext);
  if (!context) {
    throw new Error('useDemo must be used within a DemoProvider');
  }
  return context;
};
