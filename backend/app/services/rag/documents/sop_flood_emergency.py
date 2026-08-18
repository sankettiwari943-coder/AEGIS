EMERGENCY_SOP_DOCUMENTS = [
    {
        "id": "SOP-FL-001",
        "title": "Standard Operating Procedure: Urban Riverine Flood Escalation & Sector Containment",
        "category": "FLOOD_MANAGEMENT",
        "source": "National Disaster Management Authority (NDMA) Tactical Manual 2026",
        "last_revised": "2026-03-15",
        "content": """
STANDARD OPERATING PROCEDURE: URBAN RIVERINE FLOOD ESCALATION (SOP-FL-001)

1. INCIDENT CLASSIFICATION AND THRESHOLDS:
- Stage 1 (Alert): River crest exceeding baseline +1.5m. Sump pump stations online.
- Stage 2 (Warning): Flood water level exceeding 50cm in residential corridors. Primary road access restricted.
- Stage 3 (Critical Escalation): Inundation exceeding 100cm, river crest +3.0m, or arterial access cut off within 60 minutes. Immediate proactive evacuation mandatory.

2. COMMAND DECISION PROTOCOL:
- Proactive evacuation orders must be issued BEFORE arterial routes are submerged below 30cm passability.
- When an arterial route drops below 30% passability, all standard wheeled vehicles must be redirected or recalled; only amphibious units and high-clearance swiftwater boats may proceed.
- Sectors with critical infrastructure (hospitals, substations, drainage pumps) take precedence for mobile barrier deployment.

3. CASUALTY PREVENTION & PRIORITY TRIAGE:
- Priority 1: High-dependency medical patients, elderly residents in ground-floor structures, oxygen-dependent civilians.
- Priority 2: Stranded civilian clusters in isolated low-lying topography.
- Priority 3: Commercial and non-critical residential properties.
"""
    },
    {
        "id": "SOP-EV-002",
        "title": "Evacuation Routing and Roadway Accessibility Contingency Protocol",
        "category": "EVACUATION_LOGISTICS",
        "source": "State Emergency Operations Center (SEOC) Logistics Field Guide",
        "last_revised": "2026-01-20",
        "content": """
EVACUATION ROUTING AND ROADWAY ACCESSIBILITY CONTINGENCY PROTOCOL (SOP-EV-002)

1. CORRIDOR MONITORING AND CLOSURE CRITERIA:
- Roads with water depth > 45cm or current velocity > 1.5 m/s are categorized as UNPASSABLE for civilian evacuation.
- If Corridor 14 or arterial bridge approaches are predicted to submerge within 45 minutes, immediate counterflow evacuation routing must be activated to Southern High Ground (Zone 3).

2. ALTERNATIVE TRANSPORT HUBS:
- Staging Area Alpha: North Sector Transit Terminal (Elevation 18.2m).
- Staging Area Beta: High School Stadium Complex (Elevation 22.5m).
- When bridge corridors are lost, helicopter winch extraction and amphibious transport become primary transit modalities.

3. TRAFFIC DECONGESTION AND CONTROL:
- Deploy traffic enforcement drones to detect stalled vehicles obstructing arterial corridors.
- Maintain a dedicated 1-lane emergency corridor strictly for dispatched rescue assets (Ambulances, Heavy Rescue Units).
"""
    },
    {
        "id": "SOP-MED-003",
        "title": "Hospital Isolation and Critical Care Continuity Protocol",
        "category": "MEDICAL_CRITICAL_CARE",
        "source": "Ministry of Health Emergency Medical Preparedness Guidelines",
        "last_revised": "2025-11-10",
        "content": """
HOSPITAL ISOLATION AND CRITICAL CARE CONTINUITY PROTOCOL (SOP-MED-003)

1. FACILITY PROTECTION THRESHOLDS:
- Memorial Hospital (Zone 7) requires uninterrupted power and road access for regional ICU patient inflow.
- If road accessibility falls below 35%, initiate regional trauma diversion protocol immediately.

2. TRAUMA & ICU DIVERSION PROTOCOL:
- All incoming regional ambulances are automatically rerouted to District General Hospital (Zone 2) or Metro Trauma Center (Zone 5).
- On-site hospital generators must be elevated above 150cm flood line; fuel resupply via boat must be staged if road transport fails.

3. PATIENT EVACUATION PRIORITIES:
- Neonatal intensive care and ventilator-dependent patients must be moved to 3rd floor or higher prior to basement power room flooding.
"""
    },
    {
        "id": "SOP-INFRA-004",
        "title": "Substation Inundation & Cascading Power Grid Failure Mitigation",
        "category": "INFRASTRUCTURE_PROTECTION",
        "source": "Electrical Grid Safety and Emergency Operations Guideline",
        "last_revised": "2026-02-01",
        "content": """
SUBSTATION INUNDATION & CASCADING POWER GRID FAILURE MITIGATION (SOP-INFRA-004)

1. SUBSTATION FLOOD MARGIN THRESHOLDS:
- Substation #2 (Zone 7) operates at 11kV/33kV distribution. Safe bund water margin is 30cm.
- When water level reaches within 15cm of bund height, deploy mobile high-volume dewatering pumps immediately.

2. CASCADING IMPACT PREVENTION:
- An unmitigated electrical trip at Substation #2 causes simultaneous power loss to Basin Drainage Pump Station #1 and Cellular Transmission Towers Delta-4 and Echo-2.
- Pre-stage dedicated diesel generators at Pump Station #1 with automatic transfer switches before grid de-energization.
- Prioritize high-capacity barrier staging around transformer yards to avoid metropolitan blackout.
"""
    },
    {
        "id": "SOP-RES-005",
        "title": "Swiftwater Rescue Prioritization and Capability Matching Matrix",
        "category": "RESCUE_OPERATIONS",
        "source": "Federal Urban Search & Rescue (USAR) Doctrine 2026",
        "last_revised": "2026-04-05",
        "content": """
SWIFTWATER RESCUE PRIORITIZATION AND CAPABILITY MATCHING MATRIX (SOP-RES-005)

1. TEAM CAPABILITY ALLOCATION:
- In environments with current velocity > 2.0 m/s and debris fields, deploy swiftwater boat teams (e.g. Delta-2, Alpha-1) rather than standard foot rescue squads.
- Heavy Evacuation Units with medical crew are required for incidents reporting > 10 victims or oxygen-dependent casualties.
- Closest team is NOT always the optimal choice: travel speed, obstacle negotiation, and medical payload capacity must be balanced against raw ETA.

2. DISPATCH APPROVAL PROTOCOL:
- AI-recommended mission plans require explicit human commander approval.
- Automated dispatches are prohibited; commander must review expected impact, travel obstacles, and alternative allocations.
"""
    },
    {
        "id": "SOP-SIL-006",
        "title": "Silent Risk & Telecommunication Blackout Reconnaissance Protocol",
        "category": "SILENT_CRISIS_MANAGEMENT",
        "source": "Integrated Crisis Information Operations Standard",
        "last_revised": "2026-05-12",
        "content": """
SILENT RISK & TELECOMMUNICATION BLACKOUT RECONNAISSANCE PROTOCOL (SOP-SIL-006)

1. DEFINITION OF SILENT CRISIS:
- A sector characterized by high environmental hazard (inundation > 100cm) and substantial exposed population (> 1,000 residents), yet reporting ZERO civilian SOS calls due to cellular tower destruction.
- Principle: 'Zero civilian reports in a high-hazard sector indicates communication loss, NOT safety.'

2. MANDATORY RECONNAISSANCE DISPATCH:
- When a Silent Crisis Index exceeds 75/100 (e.g. Zone 4 Riverside Slums), autonomous or manned reconnaissance assets must be dispatched within 15 minutes.
- Deploy long-range satellite-linked drones or rapid scout teams (Echo-1, Recon Alpha) to assess ground truth and establish emergency mesh WiFi/satellite relays.
"""
    }
]
