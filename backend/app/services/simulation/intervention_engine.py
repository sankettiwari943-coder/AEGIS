from typing import Dict, List, Any, Optional, Tuple
from app.models.schemas import InterventionItem, ResourceInventory

class InterventionEngine:
    """
    Extensible Catalog of Emergency Interventions and Resource Constraint Validator.
    Defines systemic effects, resource costs, durations, and conflict detection.
    """
    def __init__(self):
        self.catalog: Dict[str, InterventionItem] = self._init_catalog()

    def _init_catalog(self) -> Dict[str, InterventionItem]:
        items = [
            InterventionItem(
                id="evacuate_zone_7",
                name="Evacuate Zone 7 (River Bend Lowlands)",
                description="Preemptively evacuate 6,000 residents from low-lying riverside delta to Highland Complex shelters before peak river crest.",
                category="EVACUATION",
                target_zone_id="zone-7",
                resource_type="rescue_team",
                resource_cost=2,
                benefit_summary="Reduces population exposure by 70% (+14 pts risk cut)",
                estimated_effects={
                    "population_reduction_pct": 70,
                    "zone_risk_cut": 25,
                    "lives_protected": 6100,
                    "overall_risk_benefit": 14
                },
                duration_minutes=60,
                confidence_percent=88
            ),
            InterventionItem(
                id="deploy_team_r2",
                name="Deploy Heavy Evac Unit Delta-2",
                description="Deploy Mass Evacuation & Flood Transport Unit Delta-2 (Boat + Trauma kit + 15 Capacity) to Zone 7.",
                category="RESCUE",
                target_zone_id="zone-7",
                resource_type="rescue_team",
                resource_cost=1,
                benefit_summary="Provides deep-water amphibious extraction (+9 pts risk cut)",
                estimated_effects={
                    "evacuation_support": 15,
                    "medical_support": True,
                    "lives_protected": 1800,
                    "overall_risk_benefit": 9
                },
                duration_minutes=45,
                confidence_percent=92
            ),
            InterventionItem(
                id="deploy_team_r4",
                name="Deploy Tactical Flood Medic Guardian-4",
                description="Deploy Tactical Flood & Paramedic Unit Guardian-4 (Boat + Medical) to Sector 7.",
                category="RESCUE",
                target_zone_id="zone-7",
                resource_type="rescue_team",
                resource_cost=1,
                benefit_summary="Addresses 3 critical trauma emergencies (+9 pts risk cut)",
                estimated_effects={
                    "medical_support": True,
                    "lives_protected": 1800,
                    "overall_risk_benefit": 9
                },
                duration_minutes=45,
                confidence_percent=91
            ),
            InterventionItem(
                id="deploy_medical_unit",
                name="Deploy Mobile Trauma ICU Corps",
                description="Deploy Advanced Field Medical Corps (Medic-3 / AirMed-6) to support flooded trauma wards.",
                category="MEDICAL",
                target_zone_id="zone-7",
                resource_type="medical_unit",
                resource_cost=1,
                benefit_summary="Stabilizes critical patients & prevents medical delay (+10 pts risk cut)",
                estimated_effects={
                    "hospital_access_boost_pct": 20,
                    "medical_risk_cut": 35,
                    "overall_risk_benefit": 10
                },
                duration_minutes=45,
                confidence_percent=89
            ),
            InterventionItem(
                id="deploy_boat_team",
                name="Deploy Inflatable Zodiac Watercraft Squad",
                description="Deploy Zodiac Inflatable Squad (Bravo-5) to navigate flooded arterial roads and extract isolated residents.",
                category="RESCUE",
                target_zone_id="zone-4",
                resource_type="boat_team",
                resource_cost=1,
                benefit_summary="Bypasses submerged roads in silent crisis sectors (+8 pts risk cut)",
                estimated_effects={
                    "waterway_passability_pct": 85,
                    "overall_risk_benefit": 8
                },
                duration_minutes=40,
                confidence_percent=87
            ),
            InterventionItem(
                id="redirect_traffic",
                name="Redirect Traffic & Establish Emergency Corridor",
                description="Implement police diversion on Corridor 14 to preserve emergency hospital access route.",
                category="TRAFFIC",
                target_zone_id="zone-7",
                resource_type="utility_crew",
                resource_cost=1,
                benefit_summary="Restores road accessibility to Riverbank Hospital (+12 pts risk cut)",
                estimated_effects={
                    "road_access_boost_pct": 25,
                    "hospital_access_boost_pct": 22,
                    "overall_risk_benefit": 12
                },
                duration_minutes=30,
                confidence_percent=85
            ),
            InterventionItem(
                id="protect_power_station",
                name="Deploy Barriers to Substation #2",
                description="Deploy rapid inflatable flood barriers and sandbagging to South Power Station Substation #2.",
                category="INFRASTRUCTURE",
                target_zone_id="zone-6",
                resource_type="utility_crew",
                resource_cost=2,
                benefit_summary="Prevents cascading pumping station & hospital blackout (+13 pts risk cut)",
                estimated_effects={
                    "power_cascade_prevented": True,
                    "pump_failure_prevented": True,
                    "overall_risk_benefit": 13
                },
                duration_minutes=60,
                confidence_percent=84
            ),
            InterventionItem(
                id="deploy_emergency_generator",
                name="Dispatch 500kW Mobile Diesel Generator",
                description="Transport 500kW mobile diesel generator to backup Hospital #2 and Basin Drainage Pump #1.",
                category="INFRASTRUCTURE",
                target_zone_id="zone-7",
                resource_type="generator",
                resource_cost=1,
                benefit_summary="Restores basin pumping & trauma hospital grid (+11 pts risk cut)",
                estimated_effects={
                    "pumping_restoration_pct": 100,
                    "hospital_power_restored": True,
                    "overall_risk_benefit": 11
                },
                duration_minutes=45,
                confidence_percent=90
            ),
            InterventionItem(
                id="activate_shelter_b",
                name="Activate Highland Shelter B Complex",
                description="Open Highland High School Complex with 2,150 spare capacity, food rations, and medical post.",
                category="SHELTER",
                target_zone_id="zone-5",
                resource_type="shelter",
                resource_cost=1,
                benefit_summary="Safely houses 2,150 evacuees from flood zones (+8 pts risk cut)",
                estimated_effects={
                    "shelter_capacity_opened": 2150,
                    "overall_risk_benefit": 8
                },
                duration_minutes=30,
                confidence_percent=94
            ),
            InterventionItem(
                id="preposition_resources",
                name="Pre-position Amphibious Assets at Highland",
                description="Stage secondary amphibious rescue transport at Upper Plateau staging area for rapid secondary sorties.",
                category="RESCUE",
                target_zone_id="zone-5",
                resource_type="rescue_team",
                resource_cost=1,
                benefit_summary="Reduces downstream response time by 12 minutes (+7 pts risk cut)",
                estimated_effects={
                    "eta_reduction_minutes": 12,
                    "overall_risk_benefit": 7
                },
                duration_minutes=30,
                confidence_percent=86
            )
        ]
        return {item.id: item for item in items}

    def get_all_interventions(self) -> List[InterventionItem]:
        return list(self.catalog.values())

    def get_intervention_by_id(self, item_id: str) -> Optional[InterventionItem]:
        # Support aliases
        alias_map = {
            "deploy_team_r4": "deploy_team_r4",
            "deploy_rescue_team": "deploy_team_r2",
            "deploy_rescue_team_r4": "deploy_team_r4",
            "deploy_mobile_generator": "deploy_emergency_generator",
            "activate_shelter": "activate_shelter_b",
            "open_shelter": "activate_shelter_b",
            "evacuate_zone": "evacuate_zone_7",
        }
        actual_id = alias_map.get(item_id, item_id)
        return self.catalog.get(actual_id)

    def get_current_inventory(self) -> ResourceInventory:
        return ResourceInventory(
            available_rescue_teams=3,
            available_medical_units=1,
            available_generators=2,
            available_boats=2,
            available_utility_crews=2,
            available_shelters=2,
            active_conflicts=[]
        )

    def validate_resource_constraints(
        self,
        selected_intervention_ids: List[str]
    ) -> Tuple[bool, Optional[str], int]:
        """
        Validates whether the selected interventions can be supported by current resource inventory.
        Returns (is_valid, conflict_warning_message, total_resource_cost).
        """
        inventory = self.get_current_inventory()
        demands = {
            "rescue_team": 0,
            "medical_unit": 0,
            "generator": 0,
            "boat_team": 0,
            "utility_crew": 0,
            "shelter": 0
        }
        total_cost = 0

        for action_id in selected_intervention_ids:
            item = self.get_intervention_by_id(action_id)
            if item:
                res_type = item.resource_type
                if res_type in demands:
                    demands[res_type] += item.resource_cost
                total_cost += item.resource_cost

        conflicts = []
        if demands["rescue_team"] > inventory.available_rescue_teams:
            conflicts.append(f"Requires {demands['rescue_team']} rescue teams (only {inventory.available_rescue_teams} available)")
        if demands["medical_unit"] > inventory.available_medical_units:
            conflicts.append(f"Requires {demands['medical_unit']} medical units (only {inventory.available_medical_units} available)")
        if demands["generator"] > inventory.available_generators:
            conflicts.append(f"Requires {demands['generator']} emergency generators (only {inventory.available_generators} available)")
        if demands["utility_crew"] > inventory.available_utility_crews:
            conflicts.append(f"Requires {demands['utility_crew']} utility crews (only {inventory.available_utility_crews} available)")

        if conflicts:
            msg = "RESOURCE CONFLICT: " + "; ".join(conflicts) + ". Adjust selection to fit available inventory."
            return False, msg, total_cost

        return True, None, total_cost

intervention_engine = InterventionEngine()
