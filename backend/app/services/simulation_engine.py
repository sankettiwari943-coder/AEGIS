"""
Backward compatibility bridge for Simulation Engine.
Re-exports simulation_engine and simulation_service instances from app.services.simulation.
"""
from app.services.simulation.simulation_engine import SimulationEngine, simulation_engine
from app.services.simulation.simulation_service import SimulationService, simulation_service

__all__ = ["SimulationEngine", "simulation_engine", "SimulationService", "simulation_service"]
