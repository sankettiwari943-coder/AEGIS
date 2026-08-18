"""
Evidence Repository Engine
Maintains grounded multi-source evidence items across all disaster zones,
reconciling sensors, satellite observations, citizen reports, SCADA signals, and official data.
"""
from typing import List, Dict, Any, Optional
from app.models.schemas import EvidenceItem, EvidenceType, EvidenceStatus, ClaimAssessment
from app.services.evidence.confidence_engine import confidence_engine
from app.services.evidence.verification_engine import verification_engine

class EvidenceEngine:
    """
    Core repository of empirical evidence items and structured claims.
    """
    def __init__(self):
        self.evidence_items: List[EvidenceItem] = self._seed_evidence_items()
        self.claims: List[ClaimAssessment] = self._build_claims()

    def _seed_evidence_items(self) -> List[EvidenceItem]:
        return [
            # Claim 01: Corridor 14 Bridge Inundation
            EvidenceItem(
                id="ev-01",
                type=EvidenceType.SENSOR,
                timestamp="2026-08-15T09:58:00Z",
                source="Hydrological Gauge R-3",
                location="Zone 7 — Central River Bridge Pier 3",
                claim_id="claim-01",
                claim="River stage elevation reached 7.9m (+0.4m/hr crest velocity)",
                value="7.9m (Exceeds 7.5m bridge clearance threshold)",
                reliability=0.90,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=False,
                minutes_ago=2
            ),
            EvidenceItem(
                id="ev-02",
                type=EvidenceType.SENSOR,
                timestamp="2026-08-15T09:56:00Z",
                source="Surface Depth Probe D-7",
                location="Zone 7 — Corridor 14 Ingress Ramp",
                claim_id="claim-01",
                claim="Flood depth overtopping approach road",
                value="95 cm standing water",
                reliability=0.90,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=False,
                minutes_ago=4
            ),
            EvidenceItem(
                id="ev-03",
                type=EvidenceType.CITIZEN_REPORT,
                timestamp="2026-08-15T09:53:00Z",
                source="17 Geo-tagged Citizen Reports",
                location="Zone 7 — River Bend Arterial",
                claim_id="claim-01",
                claim="Water surging across bridge deck with stranded vehicles",
                value="17 geo-located photographic submissions",
                reliability=0.70,
                status=EvidenceStatus.SUPPORTED,
                is_contradicting=False,
                minutes_ago=7
            ),
            EvidenceItem(
                id="ev-04",
                type=EvidenceType.SATELLITE_OBSERVATION,
                timestamp="2026-08-15T09:42:00Z",
                source="Sentinel-1 SAR Radar",
                location="Zone 7 — Central River Corridor",
                claim_id="claim-01",
                claim="Dielectric backscatter surface water anomaly on bridge deck",
                value="88% water surface dielectric signature",
                reliability=0.88,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=False,
                minutes_ago=18
            ),
            EvidenceItem(
                id="ev-05",
                type=EvidenceType.OFFICIAL_REPORT,
                timestamp="2026-08-15T09:48:00Z",
                source="Police Dispatch Unit 04",
                location="Zone 7 — Corridor 14 West Entrance",
                claim_id="claim-01",
                claim="Physical road barrier erected due to impassable water flow",
                value="Official closure order transmitted",
                reliability=0.95,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=False,
                minutes_ago=12
            ),
            EvidenceItem(
                id="ev-06",
                type=EvidenceType.SENSOR,
                timestamp="2026-08-15T09:57:00Z",
                source="Traffic Induction Loop 14-B",
                location="Zone 7 — Approach Overpass",
                claim_id="claim-01",
                claim="Traffic sensor still reporting partial vehicular pulse",
                value="14 vehicles/min detected",
                reliability=0.82,
                status=EvidenceStatus.CONFLICTING,
                is_contradicting=True,
                minutes_ago=3
            ),

            # Claim 02: Zone 4 Silent Crisis
            EvidenceItem(
                id="ev-07",
                type=EvidenceType.COMMUNICATION_SIGNAL,
                timestamp="2026-08-15T09:52:00Z",
                source="Cellular Gateway Monitor",
                location="Zone 4 — Tower Delta-4",
                claim_id="claim-02",
                claim="100% ping timeout; base station primary and backup power offline",
                value="0/50 pings returned (Connection LOST)",
                reliability=0.85,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=False,
                minutes_ago=8
            ),
            EvidenceItem(
                id="ev-08",
                type=EvidenceType.SATELLITE_OBSERVATION,
                timestamp="2026-08-15T09:38:00Z",
                source="Sentinel-1 SAR Radar Aperture",
                location="Zone 4 — Riverside Slums Footprint",
                claim_id="claim-02",
                claim="Continuous 145cm deep standing water layer across residential roofs",
                value="94% inundation coverage match",
                reliability=0.88,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=False,
                minutes_ago=22
            ),
            EvidenceItem(
                id="ev-09",
                type=EvidenceType.HISTORICAL_DATA,
                timestamp="2026-08-15T09:15:00Z",
                source="Municipal Census & Elevation GIS",
                location="Zone 4 — West Marshlands",
                claim_id="claim-02",
                claim="9,300 high-density residents in low-elevation depression (8.1m MSL)",
                value="High vulnerability baseline demographic",
                reliability=0.65,
                status=EvidenceStatus.SUPPORTED,
                is_contradicting=False,
                minutes_ago=45
            ),
            EvidenceItem(
                id="ev-10",
                type=EvidenceType.SENSOR,
                timestamp="2026-08-15T09:54:00Z",
                source="Road 04 Causeway Telemetry Probe",
                location="Zone 4 — Marshlands Causeway",
                claim_id="claim-02",
                claim="Causeway submerged under 140cm water; 0% passability",
                value="Passability: 0% (Impassable)",
                reliability=0.90,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=False,
                minutes_ago=6
            ),
            EvidenceItem(
                id="ev-11",
                type=EvidenceType.MODEL_OUTPUT,
                timestamp="2026-08-15T09:55:00Z",
                source="AEGIS Silent Risk Intelligence Engine",
                location="Zone 4 — Entire Sector",
                claim_id="claim-02",
                claim="91% communication anomaly deficit: 0 actual reports vs 56 expected",
                value="Silent crisis score: 91%",
                reliability=0.75,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=False,
                minutes_ago=5
            ),

            # Claim 03: Hospital A Ground Floor & Emergency Power Threat
            EvidenceItem(
                id="ev-12",
                type=EvidenceType.INFRASTRUCTURE_STATUS,
                timestamp="2026-08-15T09:50:00Z",
                source="Hospital Emergency Administrator",
                location="Zone 7 — Riverbank Memorial Hospital",
                claim_id="claim-03",
                claim="Water level reading 88cm against 100cm defensive flood bund",
                value="88 cm depth (12cm freeboard remaining)",
                reliability=0.85,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=False,
                minutes_ago=10
            ),
            EvidenceItem(
                id="ev-13",
                type=EvidenceType.INFRASTRUCTURE_STATUS,
                timestamp="2026-08-15T09:45:00Z",
                source="SCADA Grid Telemetry",
                location="Zone 7 — Substation Delta-2",
                claim_id="claim-03",
                claim="Substation breaker trip cutting grid power to hospital feeder",
                value="Feeder Voltage: 0 kV (Trip Confirmed)",
                reliability=0.85,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=False,
                minutes_ago=15
            ),
            EvidenceItem(
                id="ev-14",
                type=EvidenceType.CITIZEN_REPORT,
                timestamp="2026-08-15T09:46:00Z",
                source="6 Hospital Medical Staff Reports",
                location="Zone 7 — Emergency Bay Approach",
                claim_id="claim-03",
                claim="Ambulance bay flooded; backup diesel fuel supply at 6.5 hours",
                value="6 verified staff reports",
                reliability=0.70,
                status=EvidenceStatus.SUPPORTED,
                is_contradicting=False,
                minutes_ago=14
            ),
            EvidenceItem(
                id="ev-15",
                type=EvidenceType.SENSOR,
                timestamp="2026-08-15T09:51:00Z",
                source="Basement Sump Water Sensor",
                location="Zone 7 — Hospital Utility Wing",
                claim_id="claim-03",
                claim="Water ingress rate exceeding auxiliary sump pump capacity",
                value="Ingress: +3.2 cm/hr",
                reliability=0.90,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=False,
                minutes_ago=9
            ),

            # Claim 04: Substation Delta-1 Explosion Rumor (Contradicted / Debunked)
            EvidenceItem(
                id="ev-16",
                type=EvidenceType.CITIZEN_REPORT,
                timestamp="2026-08-15T09:35:00Z",
                source="4 Unverified Social Media Posts",
                location="Zone 6 — South Industrial Hub",
                claim_id="claim-04",
                claim="Claims that main 220kV transformer exploded in fireball",
                value="Social media rumor text",
                reliability=0.70,
                status=EvidenceStatus.UNVERIFIED,
                is_contradicting=False,
                minutes_ago=25
            ),
            EvidenceItem(
                id="ev-17",
                type=EvidenceType.SENSOR,
                timestamp="2026-08-15T09:58:00Z",
                source="SCADA Substation Transformer Telemetry",
                location="Zone 6 — Substation Delta-1",
                claim_id="claim-04",
                claim="Main transformer bus operating normally under 420A load with normal temperature",
                value="220kV Bus: Active (Temp: 64°C Normal)",
                reliability=0.90,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=True,
                minutes_ago=2
            ),
            EvidenceItem(
                id="ev-18",
                type=EvidenceType.SATELLITE_OBSERVATION,
                timestamp="2026-08-15T09:44:00Z",
                source="Thermal Optical Imagery",
                location="Zone 6 — Industrial Grid Sector",
                claim_id="claim-04",
                claim="No thermal hotspot, fire signature, or smoke plume detected",
                value="Thermal delta: 0.0°C (Normal)",
                reliability=0.88,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=True,
                minutes_ago=16
            ),
            EvidenceItem(
                id="ev-19",
                type=EvidenceType.CITIZEN_REPORT,
                timestamp="2026-08-15T09:52:00Z",
                source="8 Verified Local Field Spotters",
                location="Zone 6 — Industrial Perimeter",
                claim_id="claim-04",
                claim="Direct visual line of sight: only minor surface pooling, no fire",
                value="8 spotter reports confirming no fire",
                reliability=0.70,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=True,
                minutes_ago=8
            ),

            # Claim 05: Shelter B Safe with Reserve Capacity
            EvidenceItem(
                id="ev-20",
                type=EvidenceType.OFFICIAL_REPORT,
                timestamp="2026-08-15T09:30:00Z",
                source="Highland Shelter Director",
                location="Zone 5 — Highland High School",
                claim_id="claim-05",
                claim="Shelter B has 2,150 unoccupied beds and 8 days emergency food rations",
                value="850 / 3,000 capacity (71.7% reserve available)",
                reliability=0.95,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=False,
                minutes_ago=30
            ),
            EvidenceItem(
                id="ev-21",
                type=EvidenceType.SENSOR,
                timestamp="2026-08-15T09:48:00Z",
                source="Plateau Elevation Telemetry Gauge",
                location="Zone 5 — Highland Plateau",
                claim_id="claim-05",
                claim="Elevation 24.5m MSL; zero standing water on access routes",
                value="0.0 cm flood depth",
                reliability=0.90,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=False,
                minutes_ago=12
            ),

            # Claim 06: Dam Breach Rumor (Insufficient Evidence)
            EvidenceItem(
                id="ev-22",
                type=EvidenceType.CITIZEN_REPORT,
                timestamp="2026-08-15T09:56:00Z",
                source="Single Anonymous Message",
                location="Upper River Catchment",
                claim_id="claim-06",
                claim="Rumor claiming North Dam concrete crest collapse",
                value="Single unverified SMS report",
                reliability=0.70,
                status=EvidenceStatus.UNVERIFIED,
                is_contradicting=False,
                minutes_ago=4
            ),
            EvidenceItem(
                id="ev-23",
                type=EvidenceType.SENSOR,
                timestamp="2026-08-15T09:59:00Z",
                source="North Dam Spillway Telemetry",
                location="Upper River Dam",
                claim_id="claim-06",
                claim="Spillway gates operating under controlled discharge rate (450 m3/s)",
                value="Dam structural integrity normal",
                reliability=0.90,
                status=EvidenceStatus.VERIFIED,
                is_contradicting=True,
                minutes_ago=1
            ),

            # Claim 07: Stale Telemetry in Zone 2
            EvidenceItem(
                id="ev-24",
                type=EvidenceType.SENSOR,
                timestamp="2026-08-15T07:35:00Z",
                source="Legacy Water Gauge Z-02",
                location="Zone 2 — North River Terrace",
                claim_id="claim-07",
                claim="Water level reading 55cm from morning observation",
                value="55 cm depth",
                reliability=0.90,
                status=EvidenceStatus.STALE,
                is_contradicting=False,
                minutes_ago=145
            ),
            EvidenceItem(
                id="ev-25",
                type=EvidenceType.CITIZEN_REPORT,
                timestamp="2026-08-15T07:20:00Z",
                source="Morning Citizen Patrol",
                location="Zone 2 — Terrace Park",
                claim_id="claim-07",
                claim="Roadway passable with caution from early morning report",
                value="Passable 4 hours ago",
                reliability=0.70,
                status=EvidenceStatus.STALE,
                is_contradicting=False,
                minutes_ago=160
            )
        ]

    def _build_claims(self) -> List[ClaimAssessment]:
        raw_claims_meta = [
            {
                "claim_id": "claim-01",
                "target_zone_id": "zone-7",
                "target_entity": "Corridor 14 (Central River Bridge)",
                "title": "Corridor 14 Bridge Access Cutoff & Pier Overtopping",
                "claim_statement": "Corridor 14 bridge is becoming impassable within ~35-42 minutes due to river crest overtopping approach ramps and pier abutment.",
                "audit_trail": [
                    "Gauge R-3 recorded river stage 7.9m cresting at +0.4m/hr",
                    "Surface Depth Probe D-7 confirmed 95cm standing water overtopping approach",
                    "17 geo-tagged citizen images verified by computer vision matching",
                    "Sentinel-1 SAR dielectric radar backscatter confirmed water layer on bridge deck",
                    "Police Dispatch Unit 04 issued physical closure order",
                    "Contradiction: Traffic induction loop still pulsing partial residual flow (debunked as trapped vehicles)"
                ]
            },
            {
                "claim_id": "claim-02",
                "target_zone_id": "zone-4",
                "target_entity": "Zone 4 (Riverside Slums & Wetlands)",
                "title": "Severe Silent Crisis & Mass Trapped Population in Zone 4",
                "claim_statement": "Extreme 145cm flood submerged 9,300 resident footprint with total cellular blackout, creating an unmonitored life-safety blindspot.",
                "audit_trail": [
                    "Cellular Gateway Monitor detected 100% timeout on Tower Delta-4",
                    "Sentinel-1 SAR dielectric radar confirmed 145cm deep continuous standing water",
                    "Historical census baseline indicates 9,300 residents in low elevation depression (8.1m MSL)",
                    "Road 04 causeway telemetry confirmed 0% passability",
                    "AEGIS Silent Risk Engine flagged 91% communication anomaly deficit"
                ]
            },
            {
                "claim_id": "claim-03",
                "target_zone_id": "zone-7",
                "target_entity": "Riverbank Memorial Hospital (Zone 7)",
                "title": "Hospital Emergency Generator & Critical Access Breach",
                "claim_statement": "Riverbank Memorial Hospital emergency power and trauma intake corridor are threatened by water breach (88cm against 100cm bund).",
                "audit_trail": [
                    "Hospital Administrator reported 88cm water level against 100cm defensive bund",
                    "SCADA Substation Delta-2 electrical trip confirmed cutting primary grid feed",
                    "6 Hospital medical staff notifications verified via emergency protocol",
                    "Basement sump water sensor recorded ingress rate of +3.2 cm/hr",
                    "Hospital generator operating with 6.5 hours of emergency diesel remaining"
                ]
            },
            {
                "claim_id": "claim-04",
                "target_zone_id": "zone-6",
                "target_entity": "Substation Delta-1 (Main Industrial Grid)",
                "title": "Substation Delta-1 Explosion Rumor Debunked",
                "claim_statement": "Social media reports claiming transformer explosion and catastrophic fire at Substation Delta-1 are false.",
                "audit_trail": [
                    "4 Unverified social media claims detected across public channels",
                    "SCADA Substation telemetry confirmed 220kV bus energized under 420A load with normal operating temperature (64°C)",
                    "Satellite thermal optical imagery detected zero heat plume or fire bloom",
                    "8 Local field spotter reports confirmed only minor water pooling, zero smoke or fire",
                    "Conclusion: Claim rejected as false social media rumor"
                ]
            },
            {
                "claim_id": "claim-05",
                "target_zone_id": "zone-5",
                "target_entity": "Shelter B (Highland High School)",
                "title": "Shelter B Highland Refuge Safe with 2,150 Bed Capacity",
                "claim_statement": "Highland Shelter B is fully operational, dry (0cm water), and has spare capacity to absorb evacuees from Zone 7.",
                "audit_trail": [
                    "Shelter Director manifest confirmed 850/3,000 beds occupied with 2,150 spare capacity",
                    "Highland elevation gauge confirmed 0cm flood depth at 24.5m MSL",
                    "Food ration inventory verified at 8 days supply with on-site medical post",
                    "Optical terrain overlay confirmed clear dry access routes from East Heights"
                ]
            },
            {
                "claim_id": "claim-06",
                "target_zone_id": "zone-2",
                "target_entity": "North Basin Dam Structure",
                "title": "North Dam Crest Collapse Rumor (Insufficient Evidence)",
                "claim_statement": "Single anonymous claim of concrete dam crest breach lacks corroborating evidence and contradicts spillway telemetry.",
                "audit_trail": [
                    "Single anonymous SMS report received without photographic evidence",
                    "North Dam Spillway sensor confirms controlled release of 450 m3/s",
                    "Dam crest structural strain gauges read normal tolerances",
                    "Conclusion: Insufficient evidence; marked unverified under continuous monitoring"
                ]
            },
            {
                "claim_id": "claim-07",
                "target_zone_id": "zone-2",
                "target_entity": "Zone 2 Terrace Roadways",
                "title": "Zone 2 Terrace Passability (Stale Telemetry)",
                "claim_statement": "Zone 2 roadway telemetry is over 2 hours old and requires ground spotter refresh before making tactical transit routing decisions.",
                "audit_trail": [
                    "Legacy water depth probe recorded 55cm 145 minutes ago",
                    "Morning citizen patrol report logged 160 minutes ago",
                    "No fresh telemetry received in last 2 hours",
                    "Conclusion: Marked STALE; dispatching UAV reconnaissance to refresh telemetry"
                ]
            }
        ]

        claims_list = []
        for meta in raw_claims_meta:
            cid = meta["claim_id"]
            supporting = [item for item in self.evidence_items if item.claim_id == cid and not item.is_contradicting]
            conflicting = [item for item in self.evidence_items if item.claim_id == cid and item.is_contradicting]

            conf, rec_score, const_score, trust_score = confidence_engine.evaluate_claim_confidence(supporting, conflicting)
            status, requires_recon, conflict_obj, rec_text = verification_engine.determine_claim_status(conf, supporting, conflicting)

            # Build timeline
            all_items = supporting + conflicting
            all_items.sort(key=lambda x: x.minutes_ago, reverse=True)
            timeline = [
                {
                    "time_display": f"{item.minutes_ago}m ago",
                    "source": item.source,
                    "type": item.type.value,
                    "event": item.claim,
                    "value": str(item.value),
                    "is_contradicting": item.is_contradicting
                }
                for item in all_items
            ]

            claims_list.append(ClaimAssessment(
                claim_id=cid,
                target_zone_id=meta["target_zone_id"],
                target_entity=meta["target_entity"],
                title=meta["title"],
                claim_statement=meta["claim_statement"],
                ai_confidence_percent=conf,
                status=status,
                supporting_sources_count=len(supporting),
                conflicting_sources_count=len(conflicting),
                supporting_evidence=supporting,
                conflicting_evidence=conflicting,
                evidence_timeline=timeline,
                recency_score=rec_score,
                consistency_score=const_score,
                data_trust_score=trust_score,
                audit_trail=meta["audit_trail"],
                decision_recommendation=rec_text,
                requires_physical_recon=requires_recon
            ))

        return claims_list

    def get_all_claims(self, zone_id: Optional[str] = None, status: Optional[str] = None) -> List[ClaimAssessment]:
        results = self.claims
        if zone_id:
            results = [c for c in results if c.target_zone_id == zone_id]
        if status:
            results = [c for c in results if c.status.value.upper() == status.upper()]
        return results

    def get_claim_by_id(self, claim_id: str) -> Optional[ClaimAssessment]:
        for c in self.claims:
            if c.claim_id == claim_id:
                return c
        return None

evidence_engine = EvidenceEngine()
