"""
Backward compatibility bridge for Mission Optimizer.
Exposes mission_optimizer and mission_service instances from app.services.missions.
"""
from app.services.missions.mission_optimizer import MissionOptimizer, mission_optimizer as _core_optimizer
from app.services.missions.mission_service import MissionService, mission_service

# Export the core optimizer instance with backward-compatible method aliases
class LegacyMissionOptimizerWrapper:
    def __init__(self, core: MissionOptimizer):
        self._core = core

    def __getattr__(self, name):
        return getattr(self._core, name)

    def optimize_mission(
        self,
        target_zone_id: str = "zone-7",
        victim_count: int = 12,
        medical_emergencies: int = 3,
        available_team_ids = None
    ):
        return self._core.optimize_single_mission(
            target_zone_id=target_zone_id,
            victim_count=victim_count,
            medical_emergencies=medical_emergencies,
            available_team_ids=available_team_ids
        )

    def score_team_for_zone(self, team, zone, victim_count=12, medical_emergencies=3):
        return self._core.scorer.score_candidate(team, zone, victim_count, medical_emergencies)

mission_optimizer = LegacyMissionOptimizerWrapper(_core_optimizer)

__all__ = ["MissionOptimizer", "mission_optimizer", "mission_service"]
