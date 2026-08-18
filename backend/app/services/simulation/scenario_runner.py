import copy
from typing import List, Dict, Any, Tuple
from app.data.flood_dataset import ZONES_DATA, ROADS_DATA, INFRASTRUCTURE_DATA, RESCUE_TEAMS_DATA
from app.models.schemas import (
    SimulationRequest, Zone, RoadSegment, Infrastructure, RescueTeam,
    RoadStatus, InfraStatus, CascadeLinkShift, ZoneRiskShift
)
from app.services.simulation.intervention_engine import InterventionEngine, intervention_engine
from app.services.missions.mission_optimizer import mission_optimizer

class ScenarioRunner:
    """
    Simulation State Execution Engine.
    Evaluates compound failure perturbations vs positive mitigation interventions
    across 30m, 60m, and 3h predictive horizons.
    """
    def __init__(self, engine: InterventionEngine = None):
        self.intervention_engine = engine or intervention_engine

    def execute_scenario(self, request: SimulationRequest) -> Dict[str, Any]:
        """
        Executes a single scenario simulation. Returns state metrics, sector shifts, and cascade changes.
        """
        horizon = request.time_horizon_minutes or request.time_horizon or 60

        # 1. Deep clone baseline dataset
        sim_zones: List[Zone] = [copy.deepcopy(z) for z in ZONES_DATA]
        sim_roads: List[RoadSegment] = [copy.deepcopy(r) for r in ROADS_DATA]
        sim_infra: List[Infrastructure] = [copy.deepcopy(i) for i in INFRASTRUCTURE_DATA]
        sim_teams: List[RescueTeam] = [copy.deepcopy(t) for t in RESCUE_TEAMS_DATA]

        zones_by_id = {z.id: z for z in sim_zones}
        roads_by_id = {r.id: r for r in sim_roads}
        infra_by_id = {i.id: i for i in sim_infra}
        teams_by_id = {t.id: t for t in sim_teams}

        # 2. Horizon Projection Multiplier (Phase 3 Integration)
        horizon_factor = 1.0 if horizon == 60 else (0.85 if horizon == 30 else 1.25)

        # Baseline reference metrics (Do Nothing unmitigated state at given horizon)
        if horizon >= 180:
            base_risk = 96
            base_pop_at_risk = 14200
            base_hosp_access = 22
            base_road_access = 18
            base_power_risk = 85
            base_cascading = 96
        elif horizon <= 30:
            base_risk = 78
            base_pop_at_risk = 9800
            base_hosp_access = 45
            base_road_access = 38
            base_power_risk = 60
            base_cascading = 80
        else: # 60 minutes default
            base_risk = 91
            base_pop_at_risk = 11800
            base_hosp_access = 34
            base_road_access = 29
            base_power_risk = 72
            base_cascading = 91

        # 3. Apply Systemic Shocks (Perturbations beyond baseline)
        risk_penalty = 0
        pop_penalty = 0
        hosp_penalty = 0
        road_penalty = 0
        power_penalty = 0

        # Only add extra penalties for shocks beyond standard 2 demo shocks
        extra_perturbations = [p for p in request.perturbations if p not in ["road_14_blocked", "hospital_power_lost"]]
        for p in extra_perturbations:
            if p in ["rainfall_intensifies", "rainfall_surge_40pct"]:
                risk_penalty += 4
                pop_penalty += 1200
                road_penalty += 5
            elif p in ["dam_capacity_decreases", "dam_discharge_decrease"]:
                risk_penalty += 3
                pop_penalty += 500
            elif p == "team_r4_unavailable":
                risk_penalty += 2
            elif p == "communication_fails_zone6":
                risk_penalty += 2

        # Unmitigated Baseline for this specific scenario
        unmitigated_risk = min(98, max(20, base_risk + risk_penalty))
        unmitigated_pop = base_pop_at_risk + pop_penalty
        unmitigated_hosp = max(5, base_hosp_access - hosp_penalty)
        unmitigated_road = max(5, base_road_access - road_penalty)
        unmitigated_power = min(99, base_power_risk + power_penalty)
        unmitigated_cascade = min(98, base_cascading + int(risk_penalty * 0.8))

        # 4. Check Resource Constraints & Validate Interventions
        is_valid_res, conflict_msg, total_res_cost = self.intervention_engine.validate_resource_constraints(request.interventions)

        # 5. Apply Positive Interventions (Risk mitigation actions)
        risk_mitigation = 0
        pop_protected = 0
        hosp_restored = 0
        road_restored = 0
        power_restored = 0
        cascade_mitigation = 0
        applied_items = []
        recommended_mission_payload = None

        has_evac = any("evacuate" in a for a in request.interventions)
        has_deploy = any("deploy_team" in a or "deploy_rescue" in a for a in request.interventions)

        # Compound synergy bonus when combining evacuation with active rescue asset deployment
        if has_evac and has_deploy:
            risk_mitigation += 4 # Compound synergy bonus!

        for action_id in request.interventions:
            item = self.intervention_engine.get_intervention_by_id(action_id)
            if not item:
                continue
            applied_items.append(item)

            if action_id in ["evacuate_zone_7", "evacuate_zone"]:
                if "zone-7" in zones_by_id:
                    zones_by_id["zone-7"].population = max(500, int(zones_by_id["zone-7"].population * 0.30))
                    zones_by_id["zone-7"].primary_risk_score = max(20, zones_by_id["zone-7"].primary_risk_score - 25)
                risk_mitigation += 14
                pop_protected += 2100
                cascade_mitigation += 14

            elif action_id in ["deploy_team_r2", "deploy_rescue_team"]:
                if "team-r2" in teams_by_id:
                    teams_by_id["team-r2"].status = "dispatched"
                risk_mitigation += 9
                pop_protected += 800
                cascade_mitigation += 13
                # Phase 6 Mission Optimizer link
                opt_rec = mission_optimizer.optimize_single_mission("zone-7", 12, 3)
                recommended_mission_payload = {
                    "mission_id": opt_rec.mission_id,
                    "target_zone_id": "zone-7",
                    "target_zone_name": "Zone 7 — River Bend Lowlands",
                    "team_id": "team-r2",
                    "team_callsign": "Delta-2 (Heavy Evacuation Unit)",
                    "eta_minutes": 12,
                    "mission_impact": 98
                }

            elif action_id in ["deploy_team_r4", "deploy_rescue_team_r4"]:
                if "team-r4" in teams_by_id:
                    teams_by_id["team-r4"].status = "dispatched"
                risk_mitigation += 9
                pop_protected += 1800
                cascade_mitigation += 8

            elif action_id == "deploy_medical_unit":
                if "hosp-02" in infra_by_id:
                    infra_by_id["hosp-02"].status = InfraStatus.OPERATIONAL
                risk_mitigation += 10
                hosp_restored += 23
                cascade_mitigation += 9

            elif action_id == "redirect_traffic":
                if "road-07" in roads_by_id:
                    roads_by_id["road-07"].status = RoadStatus.OPEN
                    roads_by_id["road-07"].passability_percent = 85
                risk_mitigation += 12
                road_restored += 22
                hosp_restored += 20
                cascade_mitigation += 11

            elif action_id == "protect_power_station":
                if "pwr-02" in infra_by_id:
                    infra_by_id["pwr-02"].status = InfraStatus.OPERATIONAL
                if "pump-01" in infra_by_id:
                    infra_by_id["pump-01"].status = InfraStatus.OPERATIONAL
                risk_mitigation += 13
                power_restored += 21
                cascade_mitigation += 15

            elif action_id in ["deploy_emergency_generator", "deploy_mobile_generator"]:
                if "pump-01" in infra_by_id:
                    infra_by_id["pump-01"].status = InfraStatus.OPERATIONAL
                risk_mitigation += 11
                power_restored += 18
                hosp_restored += 15
                cascade_mitigation += 12

            elif action_id in ["activate_shelter_b", "open_shelter", "activate_shelter"]:
                if "shelt-02" in infra_by_id:
                    infra_by_id["shelt-02"].current_load += 1400
                risk_mitigation += 8
                pop_protected += 2150
                cascade_mitigation += 6

            elif action_id == "preposition_resources":
                risk_mitigation += 7
                cascade_mitigation += 5

            elif action_id == "deploy_boat_team":
                risk_mitigation += 8
                pop_protected += 1200
                cascade_mitigation += 7

        # 6. Calculate Final Simulated Scenario State
        final_scenario_risk = max(25, unmitigated_risk - risk_mitigation)
        final_pop_at_risk = max(800, unmitigated_pop - pop_protected)
        final_hosp_access = min(95, max(5, unmitigated_hosp + hosp_restored))
        final_road_access = min(95, max(5, unmitigated_road + road_restored))
        final_power_risk = max(20, unmitigated_power - power_restored)
        final_cascade_risk = max(24, unmitigated_cascade - cascade_mitigation)

        net_risk_reduction = max(0, unmitigated_risk - final_scenario_risk)
        net_risk_reduction_pct = int((net_risk_reduction / float(max(1, unmitigated_risk))) * 100)

        # Efficiency Score = Risk Reduction / Resource Cost
        eff_score = round(net_risk_reduction / float(max(1, total_res_cost)), 2)

        # 7. Sector Risk Shifts (Before vs After)
        zone_shifts = self._build_zone_shifts(unmitigated_risk, final_scenario_risk, request.interventions)

        # 8. Cascade Link Shifts (Before vs After)
        cascade_shifts = self._build_cascade_shifts(request.interventions)

        # 9. Timeline Trajectories (Current -> +30m -> +60m -> +3h)
        trajectories = self._build_timeline_trajectories(unmitigated_risk, final_scenario_risk)

        return {
            "time_horizon_minutes": horizon,
            "baseline_overall_risk": unmitigated_risk,
            "scenario_overall_risk": final_scenario_risk,
            "net_risk_reduction_points": net_risk_reduction,
            "net_risk_reduction_percent": net_risk_reduction_pct,
            "resource_cost": total_res_cost,
            "efficiency_score": eff_score,
            "metrics_raw": {
                "population_at_risk": (unmitigated_pop, final_pop_at_risk),
                "hospital_access": (unmitigated_hosp, final_hosp_access),
                "road_access": (unmitigated_road, final_road_access),
                "power_risk": (unmitigated_power, final_power_risk),
                "cascade_risk": (unmitigated_cascade, final_cascade_risk)
            },
            "zone_risk_shifts": zone_shifts,
            "cascade_shifts": cascade_shifts,
            "timeline_trajectories": trajectories,
            "has_resource_conflict": not is_valid_res,
            "conflict_message": conflict_msg,
            "recommended_mission_payload": recommended_mission_payload
        }

    def _build_zone_shifts(
        self,
        base_risk: int,
        scen_risk: int,
        interventions: List[str]
    ) -> List[ZoneRiskShift]:
        evac_active = any("evacuate" in a for a in interventions)
        deploy_active = any("deploy" in a for a in interventions)
        
        return [
            ZoneRiskShift(
                zone_id="zone-7",
                zone_code="Z-07",
                zone_name="Zone 7 — River Bend Lowlands",
                baseline_risk=94,
                baseline_severity="CRITICAL",
                scenario_risk=64 if (evac_active and deploy_active) else (75 if evac_active else 88),
                scenario_severity="HIGH" if (evac_active or deploy_active) else "CRITICAL",
                risk_delta=-30 if (evac_active and deploy_active) else (-19 if evac_active else -6),
                primary_driver="Preemptive evacuation & dedicated amphibious rescue deployment" if (evac_active or deploy_active) else "Severe river basin inundation"
            ),
            ZoneRiskShift(
                zone_id="zone-4",
                zone_code="Z-04",
                zone_name="Zone 4 — Riverside Slums & Wetlands",
                baseline_risk=91,
                baseline_severity="CRITICAL",
                scenario_risk=72,
                scenario_severity="HIGH",
                risk_delta=-19,
                primary_driver="Telecom blackout mitigated via physical watercraft recon"
            ),
            ZoneRiskShift(
                zone_id="zone-9",
                zone_code="Z-09",
                zone_name="Zone 9 — River Confluence South Outskirts",
                baseline_risk=88,
                baseline_severity="HIGH",
                scenario_risk=79,
                scenario_severity="HIGH",
                risk_delta=-9,
                primary_driver="Upstream pump barrier protection stabilizes confluence backflow"
            ),
            ZoneRiskShift(
                zone_id="zone-6",
                zone_code="Z-06",
                zone_name="Zone 6 — South Power & Industrial Hub",
                baseline_risk=85,
                baseline_severity="HIGH",
                scenario_risk=58,
                scenario_severity="MODERATE",
                risk_delta=-27,
                primary_driver="Substation #2 flood barrier protection active"
            )
        ]

    def _build_cascade_shifts(self, interventions: List[str]) -> List[CascadeLinkShift]:
        has_traffic = "redirect_traffic" in interventions
        has_power = "protect_power_station" in interventions or "deploy_emergency_generator" in interventions
        has_med = "deploy_medical_unit" in interventions or any("team_r" in a for a in interventions)

        return [
            CascadeLinkShift(
                source="Flood Inundation",
                target="Corridor 14 Road Cutoff",
                baseline_severity="CRITICAL (100% Severed)",
                scenario_severity="MODERATE (Corridor Diverted)" if has_traffic else "CRITICAL",
                mitigated=has_traffic,
                explanation="Traffic diversion breaks road isolation link to Riverbank Hospital" if has_traffic else "Unmitigated flood overtopping continues to block ambulance transit"
            ),
            CascadeLinkShift(
                source="Substation #2 Flood Inundation",
                target="Basin Drainage Pump #1 Failure",
                baseline_severity="CRITICAL (Blackout Imminent)",
                scenario_severity="STABLE (Protected)" if has_power else "CRITICAL",
                mitigated=has_power,
                explanation="Mobile generator / rapid barrier protection preserves pumping station power" if has_power else "Power loss causes pump failure and backwater surge"
            ),
            CascadeLinkShift(
                source="Road Blockage",
                target="Hospital Trauma Patient Mortality",
                baseline_severity="HIGH (Emergency Response Delayed)",
                scenario_severity="LOW (Triage Stabilized)" if has_med else "HIGH",
                mitigated=has_med,
                explanation="Dedicated field trauma unit deployed on-site before hospital transfer" if has_med else "Severe paramedic delay in flooded sectors"
            )
        ]

    def _build_timeline_trajectories(
        self,
        base_risk: int,
        scen_risk: int
    ) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "baseline": [
                {"time": "NOW", "risk": 78, "pop": 8240, "hosp_access": 61},
                {"time": "+30m", "risk": 86, "pop": 9800, "hosp_access": 45},
                {"time": "+60m", "risk": base_risk, "pop": 11800, "hosp_access": 34},
                {"time": "+3h", "risk": min(99, base_risk + 5), "pop": 14200, "hosp_access": 22}
            ],
            "intervention": [
                {"time": "NOW", "risk": 78, "pop": 8240, "hosp_access": 61},
                {"time": "+30m", "risk": max(30, int(scen_risk * 1.08)), "pop": 9200, "hosp_access": 52},
                {"time": "+60m", "risk": scen_risk, "pop": 8900, "hosp_access": 57},
                {"time": "+3h", "risk": min(95, max(28, scen_risk + 3)), "pop": 7600, "hosp_access": 64}
            ]
        }

scenario_runner = ScenarioRunner()
