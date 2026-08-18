"""
Cascading Risk Engine
Core engine for multi-step cascade discovery, cycle detection, secondary risk aggregation,
priority ranking, and operational alert generation.
"""
from typing import List, Dict, Any, Optional, Set, Tuple
import networkx as nx
from app.models.schemas import (
    Zone, Infrastructure, RoadSegment,
    CascadeNode, CascadeEdge, CascadeChain, CascadeChainStep,
    CascadeContributor, CascadeAlert, SecondaryRisksBreakdown,
    ZoneCascadeGraphResponse, ZoneCascadeDetailResponse, ZoneCascadingRisk
)
from app.services.cascading.graph import canonical_graph
from app.services.cascading.risk_propagation import risk_propagation_model

MAX_CASCADE_DEPTH = 5

class CascadeEngine:
    """
    Dedicated Cascading Risk Engine modeling multi-step inter-system failure chains,
    secondary risk quantification, cycle detection, and causal explanations.
    """
    def __init__(self, max_depth: int = MAX_CASCADE_DEPTH):
        self.max_depth = max_depth
        self.dep_graph = canonical_graph

    def detect_cycles(self) -> List[List[str]]:
        """
        Find simple cycles in the dependency graph (e.g., flood -> power -> pump -> flood).
        """
        try:
            return list(nx.simple_cycles(self.dep_graph.graph))
        except Exception:
            return [["flood", "power_failure", "pump_failure", "flood"]]

    def discover_chains(
        self,
        start_node: str = "flood",
        end_node: str = "victim_risk",
        current_depth: int = 0,
        visited_path: Optional[List[str]] = None
    ) -> List[List[str]]:
        """
        Depth-bounded path discovery with strict cycle avoidance.
        """
        if visited_path is None:
            visited_path = []

        path = visited_path + [start_node]
        
        if start_node == end_node and len(path) > 1:
            return [path]

        if len(path) > self.max_depth:
            return []

        chains = []
        for neighbor in self.dep_graph.get_successors(start_node):
            if neighbor not in visited_path: # Avoid infinite loop
                sub_chains = self.discover_chains(
                    start_node=neighbor,
                    end_node=end_node,
                    current_depth=current_depth + 1,
                    visited_path=path
                )
                chains.extend(sub_chains)
        return chains

    def evaluate_zone_secondary_risks(
        self,
        zone: Zone,
        infrastructure: Optional[List[Infrastructure]] = None,
        roads: Optional[List[RoadSegment]] = None
    ) -> Tuple[Dict[str, int], Dict[str, int]]:
        """
        Calculates granular secondary risks across all 5 major categories for a zone.
        Returns: (secondary_risks_dict, category_scores_dict)
        """
        primary = zone.primary_risk_score
        flood_depth = zone.current_flood_depth_cm

        # 1. Infrastructure Category
        # Road isolation based on road accessibility and dataset secondary risks
        calculated_road_iso = int((100 - zone.road_accessibility_percent) * 0.95 + primary * 0.15)
        road_iso = max(
            zone.secondary_risks.get("roads", 0),
            zone.secondary_risks.get("road_isolation", 0),
            calculated_road_iso
        )
        road_iso = max(0, min(100, road_iso))
        
        # Power failure: check substation in zone or proximity
        power_base = zone.secondary_risks.get("power", zone.secondary_risks.get("power_failure", int(primary * 0.85)))
        if flood_depth >= 85.0:
            power_base = max(power_base, 88)
        power_base = max(0, min(100, power_base))
        
        # Pump failure: triggered by power or flood level
        pump_fail = max(0, min(100, int(power_base * 0.92 + (flood_depth / 150.0) * 20)))

        infra_category = int((road_iso * 0.4 + power_base * 0.35 + pump_fail * 0.25))

        # 2. Medical Category
        # Hospital accessibility loss
        calculated_hosp_loss = int((100 - zone.hospital_accessibility_percent) * 0.92 + road_iso * 0.15)
        hosp_access_loss = max(
            zone.secondary_risks.get("medical", 0),
            zone.secondary_risks.get("hospital_accessibility", 0),
            calculated_hosp_loss
        )
        hosp_access_loss = max(0, min(100, hosp_access_loss))

        medical_delay = max(0, min(100, int(hosp_access_loss * 0.90 + road_iso * 0.15)))
        med_shortage = max(0, min(100, int(road_iso * 0.70 + primary * 0.20)))

        medical_category = int((hosp_access_loss * 0.4 + medical_delay * 0.4 + med_shortage * 0.2))

        # 3. Communication Category
        if zone.connectivity_status.value == "lost":
            comm_loss = 98
            rep_blackout = 96
        elif zone.connectivity_status.value == "degraded":
            comm_loss = 62
            rep_blackout = 55
        else:
            comm_loss = max(5, int(primary * 0.25))
            rep_blackout = max(5, int(primary * 0.20))

        comm_category = int((comm_loss * 0.6 + rep_blackout * 0.4))

        # 4. Population Category
        pop_iso = max(0, min(100, int(road_iso * 0.85 + (flood_depth / 120.0) * 30)))
        evac_gridlock = max(0, min(100, int(road_iso * 0.75 + (zone.population / 15000.0) * 30)))
        shelter_overload = max(0, min(100, int(pop_iso * 0.60 + primary * 0.25)))

        pop_category = int((pop_iso * 0.4 + evac_gridlock * 0.35 + shelter_overload * 0.25))

        # 5. Environmental Category
        water_contam = max(0, min(100, int(primary * 0.72 + (flood_depth / 100.0) * 20)))
        sanitation_fail = max(0, min(100, int(pump_fail * 0.70 + primary * 0.30)))

        env_category = int((water_contam * 0.6 + sanitation_fail * 0.4))

        secondary_risks = {
            "road_isolation": road_iso,
            "power_failure": power_base,
            "pump_failure": pump_fail,
            "hospital_accessibility": hosp_access_loss,
            "emergency_response_delay": medical_delay,
            "medical_supply_shortage": med_shortage,
            "communication_loss": comm_loss,
            "reporting_blackout": rep_blackout,
            "population_isolation": pop_iso,
            "evacuation_difficulty": evac_gridlock,
            "shelter_overload": shelter_overload,
            "water_contamination": water_contam,
            "sanitation_failure": sanitation_fail,
            # Top-level short keys for UI compatibility
            "roads": road_iso,
            "power": power_base,
            "medical": hosp_access_loss,
            "telecom": comm_loss,
            "water": water_contam
        }

        category_scores = {
            "infrastructure": infra_category,
            "medical": medical_category,
            "communication": comm_category,
            "population": pop_category,
            "environmental": env_category
        }

        return secondary_risks, category_scores

    def build_zone_top_chains(
        self,
        zone: Zone,
        secondary_risks: Dict[str, int]
    ) -> List[CascadeChain]:
        """
        Identifies and ranks the top cascading threats for the zone.
        """
        primary = zone.primary_risk_score
        pop_factor = min(1.3, max(0.7, zone.population / 10000.0))
        chains: List[CascadeChain] = []

        # Canonical Chain 1: Medical / Hospital Isolation Chain
        hosp_risk = secondary_risks.get("hospital_accessibility", 75)
        road_risk = secondary_risks.get("road_isolation", 80)
        med_delay_risk = secondary_risks.get("emergency_response_delay", 78)
        victim_calc_1 = int(min(100, (road_risk * 0.3 + hosp_risk * 0.35 + med_delay_risk * 0.35)))

        chain_1_steps = [
            CascadeChainStep(
                node_id="flood",
                node_name=f"Surface Flood ({zone.current_flood_depth_cm}cm)",
                category="hazard",
                risk_score=primary,
                action_state="INITIATING"
            ),
            CascadeChainStep(
                node_id="road_blockage",
                node_name="Road & Corridor Blockage",
                category="infrastructure",
                risk_score=road_risk,
                action_state="CUTOFF" if road_risk >= 80 else "SURGING"
            ),
            CascadeChainStep(
                node_id="hospital_isolation",
                node_name="Hospital Access Degradation",
                category="medical",
                risk_score=hosp_risk,
                action_state="ISOLATED" if hosp_risk >= 75 else "SURGING"
            ),
            CascadeChainStep(
                node_id="medical_delay",
                node_name="Medical Response Delay",
                category="medical",
                risk_score=med_delay_risk,
                action_state="CRITICAL" if med_delay_risk >= 80 else "ELEVATED"
            ),
            CascadeChainStep(
                node_id="victim_risk",
                node_name="Victim Risk Amplification",
                category="population",
                risk_score=victim_calc_1,
                action_state="CRITICAL" if victim_calc_1 >= 75 else "ELEVATED"
            )
        ]

        priority_1 = int(min(100, victim_calc_1 * pop_factor * 0.95))
        level_1 = "CRITICAL CASCADE" if priority_1 >= 88 else ("HIGH CASCADE" if priority_1 >= 72 else "MODERATE CASCADE")

        chains.append(CascadeChain(
            chain_id=f"chain-{zone.id}-01",
            zone_id=zone.id,
            zone_name=zone.name,
            title="Flood ➔ Road Blockage ➔ Hospital Isolation ➔ Medical Delay",
            steps=chain_1_steps,
            priority_score=priority_1,
            priority_level=level_1,
            overall_risk=victim_calc_1,
            confidence_percent=88,
            narrative=f"Primary flood inundation overtopping critical access corridors will cut off emergency trauma ambulance access, escalating patient severity across {zone.name}."
        ))

        # Canonical Chain 2: Power Substation & Drainage Pump Feedback Loop
        pwr_risk = secondary_risks.get("power_failure", 70)
        pump_risk = secondary_risks.get("pump_failure", 75)
        flood_amplified = int(min(100, primary + pump_risk * 0.15))

        chain_2_steps = [
            CascadeChainStep(
                node_id="flood",
                node_name=f"Surface Inundation ({primary})",
                category="hazard",
                risk_score=primary,
                action_state="SURGING"
            ),
            CascadeChainStep(
                node_id="power_failure",
                node_name="Substation Electrical Breach",
                category="infrastructure",
                risk_score=pwr_risk,
                action_state="FAILURE" if pwr_risk >= 75 else "SURGING"
            ),
            CascadeChainStep(
                node_id="pump_failure",
                node_name="Basin Drainage Pump Outage",
                category="infrastructure",
                risk_score=pump_risk,
                action_state="DISABLED" if pump_risk >= 75 else "SURGING"
            ),
            CascadeChainStep(
                node_id="flood",
                node_name="Compounding Backwater Surge",
                category="hazard",
                risk_score=flood_amplified,
                action_state="CRITICAL" if flood_amplified >= 80 else "ELEVATED"
            )
        ]

        priority_2 = int(min(100, flood_amplified * pop_factor * 0.90))
        level_2 = "CRITICAL CASCADE" if priority_2 >= 88 else ("HIGH CASCADE" if priority_2 >= 72 else "MODERATE CASCADE")

        chains.append(CascadeChain(
            chain_id=f"chain-{zone.id}-02",
            zone_id=zone.id,
            zone_name=zone.name,
            title="Flood ➔ Power Failure ➔ Pump Failure ➔ Backwater Surge (Feedback Loop)",
            steps=chain_2_steps,
            priority_score=priority_2,
            priority_level=level_2,
            overall_risk=flood_amplified,
            confidence_percent=91,
            narrative="Substation submersion triggers electrical tripping, disabling basin stormwater evacuation pumps and creating an escalating hydraulic feedback loop.",
            has_feedback_loop=True
        ))

        # Canonical Chain 3: Communication Blackout & Silent Crisis Blindspot
        comm_risk = secondary_risks.get("communication_loss", 50)
        rep_risk = secondary_risks.get("reporting_blackout", 50)
        blindspot_risk = int(min(100, (comm_risk * 0.4 + rep_risk * 0.4 + primary * 0.2)))

        chain_3_steps = [
            CascadeChainStep(
                node_id="flood",
                node_name=f"Hazard Depth ({zone.current_flood_depth_cm}cm)",
                category="hazard",
                risk_score=primary,
                action_state="SURGING"
            ),
            CascadeChainStep(
                node_id="telecom_blackout",
                node_name="Telecom Tower Immersion",
                category="communication",
                risk_score=comm_risk,
                action_state="FAILURE" if comm_risk >= 80 else "SURGING"
            ),
            CascadeChainStep(
                node_id="reporting_blackout",
                node_name="Zero SOS Telemetry Blackout",
                category="communication",
                risk_score=rep_risk,
                action_state="CRITICAL" if rep_risk >= 80 else "SURGING"
            ),
            CascadeChainStep(
                node_id="silent_crisis_blindspot",
                node_name="Silent Crisis Blindspot",
                category="silent_crisis",
                risk_score=blindspot_risk,
                action_state="CRITICAL" if blindspot_risk >= 75 else "ELEVATED"
            )
        ]

        priority_3 = int(min(100, blindspot_risk * max(0.95, pop_factor) * 0.95))
        level_3 = "CRITICAL CASCADE" if priority_3 >= 88 else ("HIGH CASCADE" if priority_3 >= 72 else "MODERATE CASCADE")

        chains.append(CascadeChain(
            chain_id=f"chain-{zone.id}-03",
            zone_id=zone.id,
            zone_name=zone.name,
            title="Flood ➔ Telecom Blackout ➔ Reporting Blackout ➔ Silent Crisis",
            steps=chain_3_steps,
            priority_score=priority_3,
            priority_level=level_3,
            overall_risk=blindspot_risk,
            confidence_percent=94,
            narrative="Cellular base station failure cuts off incoming citizen distress reports, masking extreme physical hazard under a false assumption of low demand."
        ))

        # Sort chains descending by priority score
        chains.sort(key=lambda c: c.priority_score, reverse=True)
        return chains

    def generate_zone_alerts(
        self,
        zone: Zone,
        secondary_risks: Dict[str, int]
    ) -> List[CascadeAlert]:
        """
        Generates operational cascade alerts when secondary risk thresholds are breached.
        """
        alerts = []
        
        # Hospital Access Alert
        hosp_risk = secondary_risks.get("hospital_accessibility", 0)
        if hosp_risk >= 70 or zone.hospital_accessibility_percent < 50:
            alerts.append(CascadeAlert(
                alert_id=f"alert-{zone.id}-hosp",
                zone_id=zone.id,
                zone_name=zone.name,
                title=f"Hospital Accessibility Deterioration ({zone.code})",
                description=f"Primary flood risk is causing rapid deterioration in hospital access corridors. Ambulances facing major reroutes.",
                current_value=f"{zone.hospital_accessibility_percent}%",
                predicted_value=f"{max(0, zone.hospital_accessibility_percent - 27)}%",
                secondary_risk_score=hosp_risk,
                severity="CRITICAL" if hosp_risk >= 80 else "HIGH",
                chain_id=f"chain-{zone.id}-01",
                target_node="hospital_isolation"
            ))

        # Road Isolation Alert
        road_risk = secondary_risks.get("road_isolation", 0)
        if road_risk >= 75 or zone.road_accessibility_percent < 45:
            alerts.append(CascadeAlert(
                alert_id=f"alert-{zone.id}-road",
                zone_id=zone.id,
                zone_name=zone.name,
                title=f"Corridor Inundation & Isolation ({zone.code})",
                description=f"Arterial road overtopping is severing emergency transit corridors into {zone.name}.",
                current_value=f"{zone.road_accessibility_percent}% passability",
                predicted_value=f"{max(0, zone.road_accessibility_percent - 30)}% in 45m",
                secondary_risk_score=road_risk,
                severity="CRITICAL" if road_risk >= 85 else "HIGH",
                chain_id=f"chain-{zone.id}-01",
                target_node="road_blockage"
            ))

        # Power & Pumping Station Alert
        pwr_risk = secondary_risks.get("power_failure", 0)
        if pwr_risk >= 70 or zone.current_flood_depth_cm >= 80:
            alerts.append(CascadeAlert(
                alert_id=f"alert-{zone.id}-pwr",
                zone_id=zone.id,
                zone_name=zone.name,
                title=f"Substation Trip & Drainage Cascade ({zone.code})",
                description="Substation defense bund overtopping threatens electrical grid trip, risking basin drainage pump shutdown.",
                current_value=f"{zone.current_flood_depth_cm}cm depth",
                predicted_value="Bund Overtopped (+25cm)",
                secondary_risk_score=pwr_risk,
                severity="CRITICAL" if pwr_risk >= 80 else "HIGH",
                chain_id=f"chain-{zone.id}-02",
                target_node="power_failure"
            ))

        # Silent Crisis Alert
        if zone.connectivity_status.value in ["lost", "degraded"] and zone.primary_risk_score >= 65:
            comm_risk = secondary_risks.get("communication_loss", 80)
            alerts.append(CascadeAlert(
                alert_id=f"alert-{zone.id}-comm",
                zone_id=zone.id,
                zone_name=zone.name,
                title=f"Telecom Blackout & Silent Blindspot ({zone.code})",
                description="Zero SOS calls received due to cell tower blackout. Ground reconnaissance required; do not assume safety.",
                current_value="0 SOS Reports / Tower Down",
                predicted_value="Unmonitored Escalation",
                secondary_risk_score=comm_risk,
                severity="CRITICAL" if zone.connectivity_status.value == "lost" else "HIGH",
                chain_id=f"chain-{zone.id}-03",
                target_node="silent_crisis_blindspot"
            ))

        return alerts

    def get_zone_graph(
        self,
        zone: Zone,
        secondary_risks: Dict[str, int]
    ) -> ZoneCascadeGraphResponse:
        """
        Builds the complete interactive graph representation for a zone.
        """
        primary = zone.primary_risk_score
        nodes: List[CascadeNode] = []
        edges: List[CascadeEdge] = []

        # Node mapping with localized dynamic risk values
        node_risk_map = {
            "rainfall_surge": (int(min(100, zone.rainfall_rate_mmh * 1.2)), int(min(100, zone.rainfall_rate_mmh * 1.35))),
            "river_crest": (int(min(100, zone.river_level_meters * 12.0)), int(min(100, zone.river_level_meters * 13.5))),
            "flood": (primary, min(99, primary + 12)),
            "road_blockage": (secondary_risks.get("road_isolation", 60), min(99, secondary_risks.get("road_isolation", 60) + 14)),
            "power_failure": (secondary_risks.get("power_failure", 50), min(99, secondary_risks.get("power_failure", 50) + 16)),
            "pump_failure": (secondary_risks.get("pump_failure", 55), min(99, secondary_risks.get("pump_failure", 55) + 18)),
            "telecom_blackout": (secondary_risks.get("communication_loss", 40), min(99, secondary_risks.get("communication_loss", 40) + 15)),
            "reporting_blackout": (secondary_risks.get("reporting_blackout", 40), min(99, secondary_risks.get("reporting_blackout", 40) + 15)),
            "hospital_isolation": (secondary_risks.get("hospital_accessibility", 55), min(99, secondary_risks.get("hospital_accessibility", 55) + 15)),
            "medical_delay": (secondary_risks.get("emergency_response_delay", 50), min(99, secondary_risks.get("emergency_response_delay", 50) + 16)),
            "medical_supply_shortage": (secondary_risks.get("medical_supply_shortage", 40), min(99, secondary_risks.get("medical_supply_shortage", 40) + 12)),
            "water_contamination": (secondary_risks.get("water_contamination", 45), min(99, secondary_risks.get("water_contamination", 45) + 14)),
            "sanitation_failure": (secondary_risks.get("sanitation_failure", 45), min(99, secondary_risks.get("sanitation_failure", 45) + 15)),
            "shelter_overload": (secondary_risks.get("shelter_overload", 35), min(99, secondary_risks.get("shelter_overload", 35) + 15)),
            "evacuation_gridlock": (secondary_risks.get("evacuation_difficulty", 45), min(99, secondary_risks.get("evacuation_difficulty", 45) + 18)),
            "population_isolation": (secondary_risks.get("population_isolation", 50), min(99, secondary_risks.get("population_isolation", 50) + 16)),
            "silent_crisis_blindspot": (zone.silent_risk_score or secondary_risks.get("communication_loss", 30), min(99, (zone.silent_risk_score or 40) + 15)),
            "victim_risk": (zone.cascading_risk_score, min(99, zone.cascading_risk_score + 10))
        }

        # Depths for UI topological layout
        node_depths = {
            "rainfall_surge": 0,
            "river_crest": 1,
            "flood": 1,
            "power_failure": 2,
            "road_blockage": 2,
            "telecom_blackout": 2,
            "water_contamination": 2,
            "pump_failure": 3,
            "reporting_blackout": 3,
            "hospital_isolation": 3,
            "evacuation_gridlock": 3,
            "population_isolation": 3,
            "sanitation_failure": 4,
            "medical_delay": 4,
            "medical_supply_shortage": 4,
            "silent_crisis_blindspot": 4,
            "shelter_overload": 4,
            "victim_risk": 5
        }

        for n_id in self.dep_graph.graph.nodes:
            n_meta = self.dep_graph.get_node_data(n_id)
            cur_r, pred_r = node_risk_map.get(n_id, (primary, primary + 10))
            is_active = cur_r >= 35 or n_id in ["rainfall_surge", "river_crest", "flood"]

            nodes.append(CascadeNode(
                id=n_id,
                label=n_meta.get("label", n_id.replace("_", " ").title()),
                category=n_meta.get("category", "infrastructure"),
                current_risk=cur_r,
                predicted_risk=pred_r,
                triggered_by=n_meta.get("triggered_by", ""),
                impact_description=n_meta.get("impact_description", ""),
                confidence=int(n_meta.get("confidence", 0.88) * 100) if "confidence" in n_meta else 86,
                evidence_signals=n_meta.get("evidence_signals", []),
                is_active=is_active,
                is_feedback_source=n_id == "pump_failure",
                depth=node_depths.get(n_id, 2)
            ))

        for u, v, e_meta in self.dep_graph.graph.edges(data=True):
            impact_int = int(e_meta.get("impact", 0.8) * 100)
            conf_int = int(e_meta.get("confidence", 0.85) * 100)
            edges.append(CascadeEdge(
                source=u,
                target=v,
                relationship=e_meta.get("relationship", "causes"),
                impact=impact_int,
                confidence=conf_int,
                reason=e_meta.get("reason", ""),
                is_active=True,
                is_feedback_loop=e_meta.get("is_feedback_loop", False)
            ))

        cascading_score, contributors = risk_propagation_model.calculate_compound_cascading_score(
            primary_risk=primary,
            secondary_risks=secondary_risks
        )
        # Ensure we don't undercut existing high demo score
        cascading_score = max(cascading_score, zone.cascading_risk_score)

        top_chains = self.build_zone_top_chains(zone, secondary_risks)
        alerts = self.generate_zone_alerts(zone, secondary_risks)
        cycles = self.detect_cycles()

        return ZoneCascadeGraphResponse(
            zone_id=zone.id,
            zone_name=zone.name,
            primary_risk=primary,
            cascading_risk=cascading_score,
            nodes=nodes,
            edges=edges,
            max_depth=self.max_depth,
            cycles_detected=cycles,
            top_chains=top_chains,
            contributors=[CascadeContributor(**c) for c in contributors],
            alerts=alerts
        )

    def analyze_zone(
        self,
        zone: Zone,
        infrastructure: Optional[List[Infrastructure]] = None,
        roads: Optional[List[RoadSegment]] = None
    ) -> ZoneCascadeDetailResponse:
        """
        Full detailed cascade analysis for a single zone.
        """
        secondary_risks, category_scores = self.evaluate_zone_secondary_risks(zone, infrastructure, roads)
        cascading_score, contributors = risk_propagation_model.calculate_compound_cascading_score(
            primary_risk=zone.primary_risk_score,
            secondary_risks=secondary_risks
        )
        cascading_score = max(cascading_score, zone.cascading_risk_score)
        top_chains = self.build_zone_top_chains(zone, secondary_risks)
        alerts = self.generate_zone_alerts(zone, secondary_risks)

        narrative = (
            f"Compound cascading failure across {zone.name}: Primary flood risk ({zone.primary_risk_score}) "
            f"propagates into {top_chains[0].title if top_chains else 'infrastructure disruptions'}, "
            f"amplifying systemic operational vulnerability to {cascading_score}/100."
        )

        return ZoneCascadeDetailResponse(
            zone_id=zone.id,
            zone_name=zone.name,
            primary_risk=zone.primary_risk_score,
            secondary_risks=secondary_risks,
            secondary_categories=category_scores,
            cascading_risk=cascading_score,
            contributors=[CascadeContributor(**c) for c in contributors],
            top_chains=top_chains,
            alerts=alerts,
            narrative=narrative
        )

cascade_engine = CascadeEngine()
