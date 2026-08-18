"""
Backward compatibility bridge for AI Disaster Orchestrator.
Re-exports DisasterOrchestrator and disaster_orchestrator from app.services.orchestrator.
"""
from app.services.orchestrator.orchestrator import DisasterOrchestrator, disaster_orchestrator

__all__ = ["DisasterOrchestrator", "disaster_orchestrator"]
