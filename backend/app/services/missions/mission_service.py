from typing import List, Dict, Any, Optional
from datetime import datetime
from app.data.flood_dataset import RESCUE_TEAMS_DATA, ZONES_DATA
from app.models.schemas import (
    RescueTeam, Zone, MissionRecommendation, MissionCandidate,
    MultiMissionOptimizationPlan, MissionModifyRequest
)
from app.services.missions.mission_optimizer import MissionOptimizer, mission_optimizer

class MissionService:
    """
    Mission Management and Simulated Dispatch Orchestrator.
    Manages the lifecycle of recommended, modified, and approved simulated missions.
    """
    def __init__(self, optimizer: Optional[MissionOptimizer] = None):
        self.optimizer = optimizer or mission_optimizer
        self.simulated_missions: Dict[str, MissionRecommendation] = {}
        self._initialize_default_missions()

    def _initialize_default_missions(self):
        """Pre-populates baseline recommendations for primary active zones."""
        default_z7 = self.optimizer.optimize_single_mission("zone-7", victim_count=12, medical_emergencies=3)
        self.simulated_missions[default_z7.mission_id] = default_z7

    def get_all_missions(self) -> List[MissionRecommendation]:
        """Returns all currently tracked mission recommendations."""
        # Ensure zone 7 is always present
        if not self.simulated_missions:
            self._initialize_default_missions()
        return list(self.simulated_missions.values())

    def get_mission_by_id(self, mission_id: str) -> Optional[MissionRecommendation]:
        if mission_id in self.simulated_missions:
            return self.simulated_missions[mission_id]
        
        # Fallback: check if zone-based ID pattern
        for m in self.simulated_missions.values():
            if m.mission_id == mission_id or m.target_zone_id == mission_id:
                return m
        
        # Generate on-demand if zone id
        zone = self.optimizer.get_zone_by_id(mission_id)
        if zone:
            rec = self.optimizer.optimize_single_mission(zone.id)
            self.simulated_missions[rec.mission_id] = rec
            return rec
        return None

    def get_fleet_recommendations(
        self,
        zones: Optional[List[str]] = None,
        available_teams: Optional[List[str]] = None
    ) -> MultiMissionOptimizationPlan:
        """Returns multi-sector fleet allocation recommendations."""
        plan = self.optimizer.optimize_multi_mission_fleet(zones, available_teams)
        for m in plan.assigned_missions:
            self.simulated_missions[m.mission_id] = m
        return plan

    def optimize_mission(
        self,
        target_zone_id: str = "zone-7",
        victim_count: int = 12,
        medical_emergencies: int = 3,
        available_team_ids: Optional[List[str]] = None
    ) -> MissionRecommendation:
        """Optimizes a single zone mission and registers it."""
        rec = self.optimizer.optimize_single_mission(
            target_zone_id=target_zone_id,
            victim_count=victim_count,
            medical_emergencies=medical_emergencies,
            available_team_ids=available_team_ids
        )
        self.simulated_missions[rec.mission_id] = rec
        return rec

    def approve_mission(
        self,
        mission_id: str,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Approves a mission under simulation mode.
        Updates team in-memory status and records audit trace.
        """
        mission = self.get_mission_by_id(mission_id)
        selected_team_id = team_id or (mission.recommended_team.team_id if mission else "team-r4")
        
        if mission:
            mission.human_approval_state = "APPROVED"
            mission.approved_at = datetime.now().isoformat()
            # If a specific team was approved, make sure it's reflected in recommendation
            if team_id and team_id != mission.recommended_team.team_id:
                # Find team in alternates or generate
                for alt in mission.alternate_teams:
                    if alt.team_id == team_id:
                        # Swap recommended with alt
                        old_rec = mission.recommended_team
                        mission.recommended_team = alt
                        mission.alternate_teams = [old_rec] + [a for a in mission.alternate_teams if a.team_id != team_id]
                        break

        # Update in-memory team status
        team_callsign = selected_team_id
        for t in RESCUE_TEAMS_DATA:
            if t.id == selected_team_id:
                t.status = "dispatched"
                t.current_mission = mission_id
                team_callsign = t.callsign

        return {
            "status": "APPROVED",
            "dispatch_status": "DISPATCHED — SIMULATION",
            "mission_id": mission_id,
            "team_id": selected_team_id,
            "team_callsign": team_callsign,
            "approved_at": datetime.now().isoformat(),
            "simulation_mode_label": "SIMULATION / DEMONSTRATION DATA ONLY",
            "message": f"Mission {mission_id} authorized by human operator. Asset {team_callsign} status set to DISPATCHED (Simulation)."
        }

    def modify_mission(
        self,
        mission_id: str,
        modify_req: MissionModifyRequest
    ) -> MissionRecommendation:
        """
        Allows the operator to override team, target zone, or triage parameters,
        and dynamically recalculates the candidate scores, route, and comparisons.
        """
        existing = self.get_mission_by_id(mission_id)
        
        target_zone_id = modify_req.target_zone_id or (existing.target_zone_id if existing else "zone-7")
        victim_count = modify_req.victim_count if modify_req.victim_count is not None else (existing.victim_count if existing else 12)
        medical_emergencies = modify_req.medical_emergencies if modify_req.medical_emergencies is not None else (existing.medical_emergencies if existing else 3)
        
        # Recalculate base optimization
        recalc = self.optimizer.optimize_single_mission(
            target_zone_id=target_zone_id,
            victim_count=victim_count,
            medical_emergencies=medical_emergencies
        )

        # If user explicitly selected a non-recommended team, promote it to recommended slot for comparison
        if modify_req.team_id and modify_req.team_id != recalc.recommended_team.team_id:
            chosen_cand = None
            for alt in recalc.alternate_teams:
                if alt.team_id == modify_req.team_id:
                    chosen_cand = alt
                    break
            
            if chosen_cand:
                old_best = recalc.recommended_team
                recalc.recommended_team = chosen_cand
                recalc.alternate_teams = [old_best] + [a for a in recalc.alternate_teams if a.team_id != modify_req.team_id]
                # Update closest team comparison
                zone = self.optimizer.get_zone_by_id(target_zone_id)
                if zone:
                    recalc.closest_team_comparison = self.optimizer.scorer.generate_closest_team_comparison(
                        chosen_cand,
                        [chosen_cand, old_best] + recalc.alternate_teams,
                        zone,
                        medical_emergencies
                    )

        recalc.mission_id = mission_id
        self.simulated_missions[mission_id] = recalc
        return recalc

    def dismiss_mission(self, mission_id: str) -> Dict[str, Any]:
        """Dismisses or defers a mission recommendation."""
        mission = self.get_mission_by_id(mission_id)
        if mission:
            mission.human_approval_state = "DISMISSED"
        return {
            "status": "DISMISSED",
            "mission_id": mission_id,
            "message": f"Mission {mission_id} recommendation dismissed by operator."
        }

    def reset(self):
        """Resets all missions back to the baseline state."""
        self.simulated_missions.clear()
        self._initialize_default_missions()

mission_service = MissionService()

