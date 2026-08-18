from typing import List, Dict, Any, Optional
from datetime import datetime
from app.data.flood_dataset import RESCUE_TEAMS_DATA, ZONES_DATA, ROADS_DATA
from app.models.schemas import (
    RescueTeam, Zone, MissionCandidate, MissionRecommendation,
    ClosestTeamComparison, MultiMissionOptimizationPlan, MultiMissionOptimizationRequest
)
from app.services.missions.mission_scoring import MissionScorer, mission_scorer

class MissionOptimizer:
    """
    Multi-Attribute Utility Optimization and Simultaneous Fleet Assignment Engine.
    Allocates specialized rescue assets across affected disaster sectors to maximize overall survival impact.
    """
    def __init__(
        self,
        teams: Optional[List[RescueTeam]] = None,
        zones: Optional[List[Zone]] = None,
        scorer: Optional[MissionScorer] = None
    ):
        self.teams = teams or RESCUE_TEAMS_DATA
        self.zones = zones or ZONES_DATA
        self.zones_map = {z.id: z for z in self.zones}
        self.scorer = scorer or mission_scorer

    def get_zone_by_id(self, zone_id: str) -> Optional[Zone]:
        for z in self.zones:
            if z.id == zone_id or z.code.lower() == zone_id.lower():
                return z
        return None

    def optimize_single_mission(
        self,
        target_zone_id: str = "zone-7",
        victim_count: int = 12,
        medical_emergencies: int = 3,
        available_team_ids: Optional[List[str]] = None
    ) -> MissionRecommendation:
        """
        Optimizes team assignment for a single target incident sector.
        Returns the top recommended asset, alternative candidates, score breakdowns,
        and the explainable 'Why not closest team?' comparison.
        """
        zone = self.get_zone_by_id(target_zone_id) or self.zones_map.get("zone-7", self.zones[0])
        
        # Filter teams if specified
        candidate_teams = self.teams
        if available_team_ids:
            candidate_teams = [t for t in self.teams if t.id in available_team_ids]
            if not candidate_teams:
                candidate_teams = self.teams

        # Check for Silent Crisis Recon Mission
        is_silent = getattr(zone, 'is_silent_risk', False) or zone.connectivity_status.value == "lost"
        silent_score = getattr(zone, 'silent_risk_score', 0)
        
        if is_silent and silent_score >= 60:
            mission_type = "PHYSICAL_RECON"
            urgency_level = "CRITICAL SILENT CRISIS"
        elif medical_emergencies >= 3:
            mission_type = "MEDICAL_EMERGENCY"
            urgency_level = "CRITICAL MEDICAL TRIAGE"
        elif zone.primary_risk_score >= 75:
            mission_type = "RESCUE_EVACUATION"
            urgency_level = "CRITICAL FLOOD EVACUATION"
        else:
            mission_type = "RESCUE_EVACUATION"
            urgency_level = "HIGH PRIORITY"

        # Generate and score candidate assignments
        candidates: List[MissionCandidate] = []
        for team in candidate_teams:
            cand = self.scorer.score_candidate(team, zone, victim_count, medical_emergencies)
            candidates.append(cand)

        # Sort candidates descending by total mission score
        candidates.sort(key=lambda c: c.total_mission_score, reverse=True)
        best_candidate = candidates[0]
        alternates = candidates[1:]

        # Build 'Why not closest team?' comparison
        comparison = self.scorer.generate_closest_team_comparison(
            best_candidate,
            candidates,
            zone,
            medical_emergencies
        )

        # Evidence confidence assessment
        evidence_conf = 91 if not is_silent else 55
        conf_status = "HIGH_CONFIDENCE" if evidence_conf >= 70 else "LOW_CONFIDENCE"

        evidence_signals = [
            f"Sensor telemetry confirms {zone.current_flood_depth_cm} cm flood level",
            f"Road accessibility currently at {zone.road_accessibility_percent}%",
            f"{'Field report confirms ' + str(medical_emergencies) + ' trauma patients' if medical_emergencies > 0 else 'General evacuation call'}"
        ]
        if is_silent:
            evidence_signals.append("Telecom blackout detected — Physical verification mission recommended.")

        return MissionRecommendation(
            mission_id=f"mission-opt-{zone.code.lower()}-{datetime.now().strftime('%M%S')}",
            mission_type=mission_type,
            target_zone_id=zone.id,
            target_zone_name=zone.name,
            victim_count=victim_count,
            medical_emergencies=medical_emergencies,
            flood_depth_cm=zone.current_flood_depth_cm,
            urgency_level=urgency_level,
            urgency_label="MODEL ESTIMATE",
            recommended_team=best_candidate,
            alternate_teams=alternates,
            closest_team_comparison=comparison,
            evidence_confidence_percent=evidence_conf,
            confidence_status=conf_status,
            evidence_signals=evidence_signals,
            human_approval_state="PENDING_APPROVAL",
            simulation_mode_label="SIMULATION / DEMONSTRATION DATA ONLY"
        )

    def optimize_multi_mission_fleet(
        self,
        target_zone_ids: Optional[List[str]] = None,
        available_team_ids: Optional[List[str]] = None,
        prioritize_medical: bool = True
    ) -> MultiMissionOptimizationPlan:
        """
        Solves multi-zone simultaneous dispatch without team conflicts.
        Uses a deterministic utility optimization algorithm to maximize overall fleet survival impact.
        """
        # Default priority zones if none provided
        target_zones: List[Zone] = []
        if target_zone_ids:
            for zid in target_zone_ids:
                z = self.get_zone_by_id(zid)
                if z:
                    target_zones.append(z)
        if not target_zones:
            # Pick the top active/critical zones (e.g. Zone 7, Zone 4, Zone 9, Zone 6)
            sorted_zones = sorted(self.zones, key=lambda z: (z.primary_risk_score + getattr(z, 'cascading_risk_score', 0)), reverse=True)
            target_zones = sorted_zones[:4]

        # Available teams pool
        available_teams = [t for t in self.teams if t.status.lower() in ["ready", "available", "staged"]]
        if available_team_ids:
            available_teams = [t for t in available_teams if t.id in available_team_ids]

        assigned_missions: List[MissionRecommendation] = []
        used_team_ids = set()
        unassigned_zones = []
        conflicts_prevented = 0

        # Sort zones by operational urgency (silent crisis + high risk first)
        def zone_priority_key(z: Zone):
            is_silent = getattr(z, 'is_silent_risk', False)
            return (1 if is_silent else 0, z.primary_risk_score, getattr(z, 'cascading_risk_score', 0))

        target_zones.sort(key=zone_priority_key, reverse=True)

        for zone in target_zones:
            # Estimate victim triage parameters per zone
            v_count = max(6, int(zone.population * 0.0015))
            med_count = 3 if zone.id == "zone-7" else (2 if zone.id in ["zone-4", "zone-6"] else 1)

            # Available unassigned teams
            free_teams = [t for t in available_teams if t.id not in used_team_ids]

            if not free_teams:
                unassigned_zones.append(zone.id)
                continue

            # Score free teams for this zone
            candidates = [self.scorer.score_candidate(t, zone, v_count, med_count) for t in free_teams]
            candidates.sort(key=lambda c: c.total_mission_score, reverse=True)
            best_team_cand = candidates[0]
            alternates = candidates[1:]

            # Mark team as assigned
            used_team_ids.add(best_team_cand.team_id)
            conflicts_prevented += max(0, len(free_teams) - 1)

            # Check comparison
            comp = self.scorer.generate_closest_team_comparison(best_team_cand, candidates, zone, med_count)

            is_silent = getattr(zone, 'is_silent_risk', False) or zone.connectivity_status.value == "lost"
            mission_rec = MissionRecommendation(
                mission_id=f"mission-fleet-{zone.code.lower()}-{len(assigned_missions)+1}",
                mission_type="PHYSICAL_RECON" if is_silent else ("MEDICAL_EMERGENCY" if med_count >= 3 else "RESCUE_EVACUATION"),
                target_zone_id=zone.id,
                target_zone_name=zone.name,
                victim_count=v_count,
                medical_emergencies=med_count,
                flood_depth_cm=zone.current_flood_depth_cm,
                urgency_level="CRITICAL" if zone.primary_risk_score >= 75 else "HIGH PRIORITY",
                urgency_label="MODEL ESTIMATE",
                recommended_team=best_team_cand,
                alternate_teams=alternates,
                closest_team_comparison=comp,
                evidence_confidence_percent=92 if not is_silent else 58,
                confidence_status="HIGH_CONFIDENCE" if not is_silent else "LOW_CONFIDENCE",
                evidence_signals=[
                    f"Assigned under deterministic fleet optimization to sector {zone.code}",
                    f"Team {best_team_cand.callsign} selected over {len(alternates)} available units"
                ],
                human_approval_state="PENDING_APPROVAL",
                simulation_mode_label="SIMULATION / DEMONSTRATION DATA ONLY"
            )
            assigned_missions.append(mission_rec)

        unassigned_teams = [t.id for t in available_teams if t.id not in used_team_ids]
        avg_impact = int(sum(m.recommended_team.expected_impact for m in assigned_missions) / max(1, len(assigned_missions)))

        return MultiMissionOptimizationPlan(
            plan_id=f"plan-fleet-opt-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            total_expected_impact=avg_impact,
            assigned_missions=assigned_missions,
            unassigned_teams=unassigned_teams,
            unassigned_zones=unassigned_zones,
            conflicts_prevented=conflicts_prevented,
            optimization_strategy="Multi-Attribute Utility Fleet Optimization (Deterministic)",
            timestamp=datetime.now().isoformat()
        )

mission_optimizer = MissionOptimizer()
