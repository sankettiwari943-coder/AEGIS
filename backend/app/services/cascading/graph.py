"""
Disaster Dependency Graph Topology
Defines the directed causal dependency graph among disaster components,
municipal infrastructure, emergency services, and population vulnerability.
"""
from typing import Dict, List, Any, Optional
import networkx as nx

class DisasterDependencyGraph:
    """
    Directed Graph representing inter-system failure dependencies.
    Nodes represent hazard states, physical infrastructure, medical assets,
    population exposure, and communication channels.
    Edges represent directed causal impacts with impact weight, confidence,
    and mechanistic explanation.
    """
    def __init__(self):
        self.graph = self._build_canonical_graph()

    def _build_canonical_graph(self) -> nx.DiGraph:
        G = nx.DiGraph()

        # Canonical Node Definitions with base metadata
        nodes_metadata = {
            "rainfall_surge": {
                "label": "Heavy Rainfall Surge",
                "category": "hazard",
                "triggered_by": "Atmospheric convective band precipitation",
                "impact_description": "Increases surface runoff velocity and basin inflow rate",
                "evidence_signals": ["Doppler radar precipitation echo", "Field rain gauges > 60mm/h"]
            },
            "river_crest": {
                "label": "River Level Crest",
                "category": "hazard",
                "triggered_by": "Upstream catchment discharge and sustained rainfall surge",
                "impact_description": "Exceeds natural riverbank embankment threshold",
                "evidence_signals": ["Hydraulic river gauge telemetry", "Upstream flow velocity sensors"]
            },
            "flood": {
                "label": "Surface Flood Inundation",
                "category": "hazard",
                "triggered_by": "River overtopping and urban drainage backwater saturation",
                "impact_description": "Submerges low-elevation terrain, access roads, and grid infrastructure",
                "evidence_signals": ["SAR satellite synthetic aperture imagery", "Telemetry depth probes", "Citizen reports"]
            },
            "power_failure": {
                "label": "Power Substation Failure",
                "category": "infrastructure",
                "triggered_by": "Flood depth exceeding electrical bund barrier (90cm)",
                "impact_description": "Disables municipal power grid, drainage pump telemetry, and local telecom nodes",
                "evidence_signals": ["SCADA grid trip alarms", "Substation water sensor telemetry", "Voltage drop notifications"]
            },
            "pump_failure": {
                "label": "Drainage Pump Failure",
                "category": "infrastructure",
                "triggered_by": "Power station outage and mechanical pump chamber submergence",
                "impact_description": "Halts stormwater evacuation; creates compounding backwater surge into residential sectors",
                "evidence_signals": ["Pump flow meter drop to 0 m3/s", "SCADA circuit breaker trip"]
            },
            "road_blockage": {
                "label": "Road & Corridor Blockage",
                "category": "infrastructure",
                "triggered_by": "Flood depth exceeding vehicular and emergency passability thresholds (>40cm)",
                "impact_description": "Cuts off terrestrial evacuation routes and ambulance transit corridors",
                "evidence_signals": ["GIS road status sensors", "Traffic corridor camera feeds", "Vehicle telemetry reroutes"]
            },
            "telecom_blackout": {
                "label": "Communication Tower Blackout",
                "category": "communication",
                "triggered_by": "Flood immersion of telecom tower base and fiber backhaul severance",
                "impact_description": "Loss of cellular reception, mobile SOS capabilities, and IoT sensor telemetry",
                "evidence_signals": ["Carrier ping timeout", "Base station battery exhaustion", "Zero incoming citizen SOS packets"]
            },
            "reporting_blackout": {
                "label": "Citizen Reporting Blackout",
                "category": "communication",
                "triggered_by": "Cellular and telecom infrastructure collapse",
                "impact_description": "Creates emergency blindspot where zero reports mask severe disaster impact",
                "evidence_signals": ["SOS report count anomaly vs expected population volume", "Repeater station offline"]
            },
            "hospital_isolation": {
                "label": "Hospital Accessibility Loss",
                "category": "medical",
                "triggered_by": "Access road inundation and emergency entrance flooding",
                "impact_description": "Ambulances and emergency medical transport unable to reach trauma center",
                "evidence_signals": ["Route passability drop < 50%", "Hospital emergency bay flood sensor"]
            },
            "medical_delay": {
                "label": "Medical Response Delay",
                "category": "medical",
                "triggered_by": "Hospital isolation and transit road blockage",
                "impact_description": "Emergency trauma response ETA increases beyond critical survival window",
                "evidence_signals": ["Ambulance GPS reroute delays", "Field paramedic triage backlog"]
            },
            "medical_supply_shortage": {
                "label": "Medical Supply Shortage",
                "category": "medical",
                "triggered_by": "Logistics road cutoffs and local warehouse flooding",
                "impact_description": "Depletes trauma blood units, oxygen cylinders, and emergency medicines",
                "evidence_signals": ["Hospital pharmacy stock alerts", "Logistics supply truck obstruction"]
            },
            "water_contamination": {
                "label": "Water Supply Contamination",
                "category": "environmental",
                "triggered_by": "Stormwater runoff infiltration into potable water pipelines and drainage overflow",
                "impact_description": "Contaminates drinking water reservoirs, risking waterborne epidemic outbreak",
                "evidence_signals": ["Turbidity sensors > 50 NTU", "Water treatment plant intake shutdown"]
            },
            "sanitation_failure": {
                "label": "Sanitation & Sewage Overflow",
                "category": "environmental",
                "triggered_by": "Combined sewer surcharge and pump station outage",
                "impact_description": "Sewage backup into residential streets and basements",
                "evidence_signals": ["Manhole pressure monitors", "Environmental health sensor alerts"]
            },
            "shelter_overload": {
                "label": "Shelter Capacity Overload",
                "category": "population",
                "triggered_by": "Mass displaced population converging on limited accessible shelters",
                "impact_description": "Exceeds shelter beds, rations, and basic sanitation capabilities",
                "evidence_signals": ["Shelter intake manifest > 90% capacity", "Queue length at highland shelters"]
            },
            "evacuation_gridlock": {
                "label": "Evacuation Gridlock",
                "category": "population",
                "triggered_by": "Simultaneous vehicular evacuation converging on narrowing passable roads",
                "impact_description": "Traps civilian population in vehicles within rising flood zones",
                "evidence_signals": ["Traffic congestion index > 95%", "Aerial drone reconnaissance imagery"]
            },
            "population_isolation": {
                "label": "Population Physical Isolation",
                "category": "population",
                "triggered_by": "Arterial road cutoffs and surrounding deep floodwaters (>100cm)",
                "impact_description": "Residents stranded on rooftops and upper floors without terrestrial escape",
                "evidence_signals": ["High-resolution satellite flood extent", "Emergency thermal UAV scans"]
            },
            "silent_crisis_blindspot": {
                "label": "Silent Crisis Blindspot",
                "category": "silent_crisis",
                "triggered_by": "Reporting blackout combined with high hazard and population exposure",
                "impact_description": "Operations center falsely assumes zone safety due to absence of SOS telemetry",
                "evidence_signals": ["Silent Risk Engine anomaly index > 80", "Historical population density overlay"]
            },
            "victim_risk": {
                "label": "Victim Severity Escalation",
                "category": "population",
                "triggered_by": "Compounding delays in medical access, physical isolation, and water exposure",
                "impact_description": "Critical escalation from minor exposure to severe hypothermia, trauma, and casualties",
                "evidence_signals": ["Multi-factor casualty risk calculation", "Field paramedic escalation notices"]
            }
        }

        for node_id, data in nodes_metadata.items():
            G.add_node(node_id, **data)

        # Canonical Directed Edges with impact, confidence, and explanatory reasoning
        edges_data = [
            # Meteorological / Hydraulic Causality
            {
                "source": "rainfall_surge",
                "target": "river_crest",
                "relationship": "causes",
                "impact": 0.95,
                "confidence": 0.94,
                "reason": "Sustained high precipitation rate in the upstream catchment rapidly increases river crest elevation.",
                "is_feedback_loop": False
            },
            {
                "source": "river_crest",
                "target": "flood",
                "relationship": "causes",
                "impact": 0.92,
                "confidence": 0.92,
                "reason": "River water level exceeding containment banks causes extensive surface inundation in low-lying zones.",
                "is_feedback_loop": False
            },
            {
                "source": "rainfall_surge",
                "target": "flood",
                "relationship": "causes",
                "impact": 0.88,
                "confidence": 0.90,
                "reason": "Intense rainfall directly generates pluvial urban surface runoff exceeding local storm drain capacity.",
                "is_feedback_loop": False
            },

            # Flood -> Infrastructure Failures
            {
                "source": "flood",
                "target": "road_blockage",
                "relationship": "causes",
                "impact": 0.86,
                "confidence": 0.89,
                "reason": "Rising floodwaters submerge bridge approaches and low-elevation road segments, halting vehicle movement.",
                "is_feedback_loop": False
            },
            {
                "source": "flood",
                "target": "power_failure",
                "relationship": "causes",
                "impact": 0.80,
                "confidence": 0.86,
                "reason": "Flood depth breaching electrical substation barrier bunds triggers emergency automated shutoffs.",
                "is_feedback_loop": False
            },
            {
                "source": "flood",
                "target": "telecom_blackout",
                "relationship": "causes",
                "impact": 0.74,
                "confidence": 0.84,
                "reason": "Floodwater inundation of tower base stations and fiber exchange vaults severs transmission lines.",
                "is_feedback_loop": False
            },
            {
                "source": "flood",
                "target": "water_contamination",
                "relationship": "causes",
                "impact": 0.70,
                "confidence": 0.82,
                "reason": "Floodwaters breach potable distribution networks and water intake pumping heads.",
                "is_feedback_loop": False
            },

            # Power -> Downstream Systems
            {
                "source": "power_failure",
                "target": "pump_failure",
                "relationship": "disables",
                "impact": 0.94,
                "confidence": 0.95,
                "reason": "Loss of municipal electrical grid cuts power to heavy stormwater drainage pumps lacking backup generators.",
                "is_feedback_loop": False
            },
            {
                "source": "power_failure",
                "target": "telecom_blackout",
                "relationship": "disables",
                "impact": 0.78,
                "confidence": 0.88,
                "reason": "Substation outage drains cellular tower backup battery reserves within 2 hours.",
                "is_feedback_loop": False
            },

            # Feedback Loop: Pump Failure -> Surface Flooding Amplification
            {
                "source": "pump_failure",
                "target": "flood",
                "relationship": "amplifies",
                "impact": 0.82,
                "confidence": 0.85,
                "reason": "Disabled basin drainage pumps cause backwater accumulation, increasing local flood depth and duration.",
                "is_feedback_loop": True # FEEDBACK LOOP
            },
            {
                "source": "pump_failure",
                "target": "sanitation_failure",
                "relationship": "causes",
                "impact": 0.84,
                "confidence": 0.86,
                "reason": "Drainage pump cessation causes combined sewer mains to backflow into streets.",
                "is_feedback_loop": False
            },

            # Road Blockage -> Emergency & Medical Delays
            {
                "source": "road_blockage",
                "target": "hospital_isolation",
                "relationship": "cuts_off",
                "impact": 0.88,
                "confidence": 0.90,
                "reason": "Inundation of critical access corridors (e.g. Corridor 14) physically isolates regional trauma facilities.",
                "is_feedback_loop": False
            },
            {
                "source": "road_blockage",
                "target": "medical_delay",
                "relationship": "delays",
                "impact": 0.85,
                "confidence": 0.88,
                "reason": "Submerged transit corridors force emergency ambulances into circuitous detour routes.",
                "is_feedback_loop": False
            },
            {
                "source": "road_blockage",
                "target": "evacuation_gridlock",
                "relationship": "causes",
                "impact": 0.80,
                "confidence": 0.83,
                "reason": "Bottlenecks at impassable bridge approaches create severe multi-kilometer vehicular gridlocks.",
                "is_feedback_loop": False
            },
            {
                "source": "road_blockage",
                "target": "population_isolation",
                "relationship": "causes",
                "impact": 0.90,
                "confidence": 0.91,
                "reason": "Loss of all surrounding road ingress cuts off residential neighborhoods from terrestrial rescue units.",
                "is_feedback_loop": False
            },
            {
                "source": "road_blockage",
                "target": "medical_supply_shortage",
                "relationship": "delays",
                "impact": 0.72,
                "confidence": 0.80,
                "reason": "Obstruction of logistics arteries prevents resupply of blood, oxygen, and emergency drugs.",
                "is_feedback_loop": False
            },

            # Medical Chain
            {
                "source": "hospital_isolation",
                "target": "medical_delay",
                "relationship": "amplifies",
                "impact": 0.91,
                "confidence": 0.92,
                "reason": "When the primary trauma center is unreachable, emergency medical transit times increase drastically.",
                "is_feedback_loop": False
            },
            {
                "source": "medical_delay",
                "target": "victim_risk",
                "relationship": "amplifies",
                "impact": 0.89,
                "confidence": 0.91,
                "reason": "Delays in advanced life support and triage response directly increase critical victim severity.",
                "is_feedback_loop": False
            },
            {
                "source": "medical_supply_shortage",
                "target": "victim_risk",
                "relationship": "amplifies",
                "impact": 0.76,
                "confidence": 0.82,
                "reason": "Depleted critical pharmaceuticals compromise field stabilization of severe trauma patients.",
                "is_feedback_loop": False
            },

            # Communication & Silent Crisis Chain
            {
                "source": "telecom_blackout",
                "target": "reporting_blackout",
                "relationship": "causes",
                "impact": 0.96,
                "confidence": 0.95,
                "reason": "Cellular tower outage prevents trapped citizens from transmitting digital SOS requests or 911 calls.",
                "is_feedback_loop": False
            },
            {
                "source": "reporting_blackout",
                "target": "silent_crisis_blindspot",
                "relationship": "causes",
                "impact": 0.94,
                "confidence": 0.93,
                "reason": "Absence of incoming SOS signals produces a false operational assumption of low demand.",
                "is_feedback_loop": False
            },
            {
                "source": "silent_crisis_blindspot",
                "target": "victim_risk",
                "relationship": "amplifies",
                "impact": 0.87,
                "confidence": 0.89,
                "reason": "Undetected trapped populations receive delayed asset dispatch, escalating casualty rates.",
                "is_feedback_loop": False
            },

            # Population & Environmental -> Victim Risk
            {
                "source": "population_isolation",
                "target": "victim_risk",
                "relationship": "amplifies",
                "impact": 0.85,
                "confidence": 0.88,
                "reason": "Stranded citizens unable to self-evacuate face rising waters and depleting provisions.",
                "is_feedback_loop": False
            },
            {
                "source": "evacuation_gridlock",
                "target": "victim_risk",
                "relationship": "amplifies",
                "impact": 0.75,
                "confidence": 0.81,
                "reason": "Vehicles trapped in low underpasses risk rapid submersion by flash floodwaters.",
                "is_feedback_loop": False
            },
            {
                "source": "water_contamination",
                "target": "victim_risk",
                "relationship": "causes",
                "impact": 0.68,
                "confidence": 0.79,
                "reason": "Exposure to pathogen-laden floodwaters causes secondary gastrointestinal and chemical illness.",
                "is_feedback_loop": False
            },
            {
                "source": "population_isolation",
                "target": "shelter_overload",
                "relationship": "causes",
                "impact": 0.70,
                "confidence": 0.78,
                "reason": "Highland refuge structures in non-isolated sectors face concentrated displaced populations.",
                "is_feedback_loop": False
            }
        ]

        for edge in edges_data:
            G.add_edge(
                edge["source"],
                edge["target"],
                relationship=edge["relationship"],
                impact=edge["impact"],
                confidence=edge["confidence"],
                reason=edge["reason"],
                is_feedback_loop=edge.get("is_feedback_loop", False)
            )

        return G

    def get_node_data(self, node_id: str) -> Dict[str, Any]:
        return self.graph.nodes.get(node_id, {})

    def get_edge_data(self, source: str, target: str) -> Dict[str, Any]:
        return self.graph.get_edge_data(source, target, {})

    def get_successors(self, node_id: str) -> List[str]:
        if node_id in self.graph:
            return list(self.graph.successors(node_id))
        return []

    def get_predecessors(self, node_id: str) -> List[str]:
        if node_id in self.graph:
            return list(self.graph.predecessors(node_id))
        return []

canonical_graph = DisasterDependencyGraph()
