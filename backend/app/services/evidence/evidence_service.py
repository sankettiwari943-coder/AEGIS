"""
Evidence Service Orchestrator
High-level service connecting claims, evidence items, decision traces,
and overall system Data Trust Index calculations.
"""
from typing import List, Optional, Dict, Any
from app.models.schemas import (
    EvidenceItem, ClaimAssessment, DecisionEvidenceTrace,
    EvidenceSummaryResponse, EvidenceConflict, EvidenceStatus
)
from app.services.evidence.evidence_engine import evidence_engine
from app.services.evidence.confidence_engine import confidence_engine
from app.services.evidence.verification_engine import verification_engine

class EvidenceService:
    """
    Orchestrates truth, verification, and decision-to-evidence graph tracing.
    """
    def __init__(self):
        self.engine = evidence_engine
        self.confidence_engine = confidence_engine
        self.verification_engine = verification_engine

    def get_all_evidence(
        self,
        zone_id: Optional[str] = None,
        evidence_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[EvidenceItem]:
        items = self.engine.evidence_items
        if zone_id:
            items = [i for i in items if zone_id.lower() in i.location.lower()]
        if evidence_type:
            items = [i for i in items if i.type.value.upper() == evidence_type.upper()]
        if status:
            items = [i for i in items if i.status.value.upper() == status.upper()]
        return items

    def get_evidence_by_id(self, evidence_id: str) -> Optional[EvidenceItem]:
        for item in self.engine.evidence_items:
            if item.id == evidence_id:
                return item
        return None

    def get_all_claims(
        self,
        zone_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ClaimAssessment]:
        return self.engine.get_all_claims(zone_id=zone_id, status=status)

    def get_claim_by_id(self, claim_id: str) -> Optional[ClaimAssessment]:
        return self.engine.get_claim_by_id(claim_id)

    def get_claim_sources(self, claim_id: str) -> Dict[str, Any]:
        claim = self.get_claim_by_id(claim_id)
        if not claim:
            return {}
        return {
            "claim_id": claim.claim_id,
            "title": claim.title,
            "supporting_count": claim.supporting_sources_count,
            "conflicting_count": claim.conflicting_sources_count,
            "supporting_sources": [
                {
                    "id": item.id,
                    "type": item.type.value,
                    "source": item.source,
                    "reliability": item.reliability,
                    "minutes_ago": item.minutes_ago,
                    "claim": item.claim,
                    "value": str(item.value)
                }
                for item in claim.supporting_evidence
            ],
            "conflicting_sources": [
                {
                    "id": item.id,
                    "type": item.type.value,
                    "source": item.source,
                    "reliability": item.reliability,
                    "minutes_ago": item.minutes_ago,
                    "claim": item.claim,
                    "value": str(item.value)
                }
                for item in claim.conflicting_evidence
            ]
        }

    def get_claim_conflicts(self, claim_id: str) -> List[Dict[str, Any]]:
        claim = self.get_claim_by_id(claim_id)
        if not claim or not claim.conflicting_evidence:
            return []
        return [
            {
                "claim_id": claim.claim_id,
                "conflict_description": f"Conflicting signal from {item.source}: '{item.claim}'",
                "conflicting_evidence_id": item.id,
                "conflicting_source": item.source,
                "reliability": item.reliability,
                "minutes_ago": item.minutes_ago,
                "recommended_action": "Cross-correlate with physical field observer before committing destructive action."
            }
            for item in claim.conflicting_evidence
        ]

    def get_decision_evidence_chain(self, decision_id: str) -> Optional[DecisionEvidenceTrace]:
        """
        Traces an operational decision or predictive alert back through:
        DECISION -> RISK -> PREDICTION -> EVIDENCE
        """
        if decision_id in ["decision-zone-7-escalation", "decision-01", "zone-7"]:
            claim = self.get_claim_by_id("claim-01")
            supporting = claim.supporting_evidence if claim else []
            return DecisionEvidenceTrace(
                decision_id="decision-zone-7-escalation",
                decision_type="PREDICTION",
                title="Zone 7 Imminent Isolation in ~42 Minutes",
                zone_id="zone-7",
                action_statement="Preemptively deploy Tactical Unit R4 (Guardian-4) and activate Highland Shelter B before Corridor 14 bridge overtopping reaches 100% cutoff.",
                confidence_percent=87,
                decision_chain=[
                    {
                        "level": "DECISION",
                        "title": "Preemptive Evacuation & Tactical Asset Dispatch",
                        "text": "Authorize dispatch of Tactical Unit R4 and alert Highland Shelter B for Zone 7 displaced population.",
                        "badge": "ACTIONABLE DECISION",
                        "color": "text-cyan-400"
                    },
                    {
                        "level": "RISK",
                        "title": "Cascading Compound Risk Score: 87 / 100",
                        "text": "Corridor 14 cutoff (91) + Hospital Isolation (81) + Substation Delta-2 Trip (72).",
                        "badge": "CASCADING RISK",
                        "color": "text-amber-400"
                    },
                    {
                        "level": "PREDICTION",
                        "title": "State Escalation: Risk 82 ➔ 94 at T+42 Minutes",
                        "text": "River crest velocity (+0.4m/hr) will submerge bridge approach ramps Pier 3 within 42 minutes.",
                        "badge": "MODEL PREDICTION",
                        "color": "text-red-400"
                    },
                    {
                        "level": "EVIDENCE",
                        "title": "5 Corroborated Multi-Source Evidence Signals",
                        "text": "Gauge R-3 (7.9m) + Depth Probe D-7 (95cm) + 17 Geo-tagged images + Sentinel-1 SAR dielectric match.",
                        "badge": "GROUNDED EVIDENCE",
                        "color": "text-emerald-400"
                    }
                ],
                key_signals=[
                    "Hydrological Gauge R-3: River stage 7.9m (+0.4m/hr crest)",
                    "Surface Depth Probe D-7: 95cm standing water overtopping approach",
                    "17 Geo-tagged citizen reports with photographic confirmation",
                    "Sentinel-1 SAR Radar: 88% dielectric surface water anomaly on bridge deck",
                    "Police Dispatch Unit 04 confirms physical approach closure"
                ],
                underlying_claims=["claim-01", "claim-03"],
                underlying_evidence=supporting,
                trust_score=88
            )
        elif decision_id in ["decision-dispatch-r4", "mission-01", "team-r4"]:
            claim = self.get_claim_by_id("claim-03")
            supporting = claim.supporting_evidence if claim else []
            return DecisionEvidenceTrace(
                decision_id="decision-dispatch-r4",
                decision_type="RECOMMENDATION",
                title="Deploy Tactical Unit R4 (Guardian-4) to Zone 7",
                zone_id="zone-7",
                action_statement="Deploy Team R4 (Crew 10, Amphibious Swiftwater + Trauma Paramedic) to extract 12 trapped victims including 3 medical emergencies.",
                confidence_percent=91,
                decision_chain=[
                    {
                        "level": "DECISION",
                        "title": "Approve Tactical Mission R4 Dispatch",
                        "text": "Human operator authorization to dispatch Tactical Unit R4 with 18-minute ETA.",
                        "badge": "MISSION ALLOCATION",
                        "color": "text-cyan-400"
                    },
                    {
                        "level": "RISK",
                        "title": "Hospital Access Drop: 61% ➔ 34% (Critical)",
                        "text": "Riverbank Memorial Hospital access road inundated, requiring specialized swiftwater transport.",
                        "badge": "SECONDARY RISK",
                        "color": "text-amber-400"
                    },
                    {
                        "level": "PREDICTION",
                        "title": "Victim Urgency Score: 94 / 100",
                        "text": "Trapped population in low-lying River Bend experiencing water ingress into ground floors.",
                        "badge": "URGENCY PREDICTION",
                        "color": "text-red-400"
                    },
                    {
                        "level": "EVIDENCE",
                        "title": "Hospital Water Ingress Telemetry & Staff Reports",
                        "text": "Hospital administrator reads 88cm against 100cm bund; 6 medical staff emergency reports.",
                        "badge": "TELEMETRY EVIDENCE",
                        "color": "text-emerald-400"
                    }
                ],
                key_signals=[
                    "12 Trapped residents reported with 3 acute trauma/medical cases",
                    "Hospital ingress corridor impassable to standard 2WD ambulances",
                    "Substation Delta-2 power trip confirmed by SCADA telemetry",
                    "Hospital generator operating with 6.5 hours of emergency diesel remaining"
                ],
                underlying_claims=["claim-01", "claim-03"],
                underlying_evidence=supporting,
                trust_score=89
            )
        elif decision_id in ["decision-zone-4-silent", "silent-risk-04", "zone-4"]:
            claim = self.get_claim_by_id("claim-02")
            supporting = claim.supporting_evidence if claim else []
            return DecisionEvidenceTrace(
                decision_id="decision-zone-4-silent",
                decision_type="SILENT_CRISIS",
                title="Immediate Reconnaissance Dispatch to Zone 4 Slums",
                zone_id="zone-4",
                action_statement="Deploy immediate UAV reconnaissance & Amphibious Swiftwater Unit (Team R1) to Zone 4. Do not wait for incoming SOS calls.",
                confidence_percent=94,
                decision_chain=[
                    {
                        "level": "DECISION",
                        "title": "Dispatch Autonomous Recon & Swiftwater Extraction",
                        "text": "Immediate physical reconnaissance deployment overriding absent 911 calls.",
                        "badge": "SILENT CRISIS ACTION",
                        "color": "text-purple-400"
                    },
                    {
                        "level": "RISK",
                        "title": "Silent Crisis Probability: 91%",
                        "text": "Total communications blindspot masking extreme 145cm flood inundation.",
                        "badge": "UNMONITOREED RISK",
                        "color": "text-red-400"
                    },
                    {
                        "level": "PREDICTION",
                        "title": "9,300 Residents Cut Off in Submerged Basin",
                        "text": "Zero incoming reports is an artifact of tower destruction, not safety.",
                        "badge": "BLINDSPOT ESTIMATE",
                        "color": "text-amber-400"
                    },
                    {
                        "level": "EVIDENCE",
                        "title": "Tower Delta-4 Blackout & SAR Radar Coverage",
                        "text": "100% ping timeout on Tower Delta-4 + Sentinel-1 SAR confirms 145cm continuous standing water.",
                        "badge": "SAR SATELLITE EVIDENCE",
                        "color": "text-emerald-400"
                    }
                ],
                key_signals=[
                    "Cellular base station Tower Delta-4 ping return: 0% (Power severed)",
                    "Sentinel-1 SAR dielectric radar: 94% standing water coverage across slums footprint",
                    "Road 04 Causeway telemetry: Submerged under 140cm water (0% passability)",
                    "Historical census data: 9,300 residents residing below 8.1m MSL depression"
                ],
                underlying_claims=["claim-02"],
                underlying_evidence=supporting,
                trust_score=94
            )
        else:
            # Generic decision trace from claim 1
            claim = self.engine.claims[0]
            return DecisionEvidenceTrace(
                decision_id=decision_id,
                decision_type="PREDICTION",
                title=f"Evidence Trace for {decision_id}",
                zone_id=claim.target_zone_id,
                action_statement="Operational action grounded in multi-source sensor and satellite telemetry.",
                confidence_percent=claim.ai_confidence_percent,
                decision_chain=[
                    {
                        "level": "DECISION",
                        "title": "Operational Action Authorized",
                        "text": "Action grounded in verified multi-source evidence chain.",
                        "badge": "DECISION",
                        "color": "text-cyan-400"
                    },
                    {
                        "level": "RISK",
                        "title": "Systemic Risk State Evaluated",
                        "text": "Risk calculated from empirical sensor inputs.",
                        "badge": "RISK",
                        "color": "text-amber-400"
                    },
                    {
                        "level": "PREDICTION",
                        "title": "Hydraulic State Progression",
                        "text": "Deterministic model forecast cross-verified with radar telemetry.",
                        "badge": "PREDICTION",
                        "color": "text-red-400"
                    },
                    {
                        "level": "EVIDENCE",
                        "title": "Corroborated Telemetry Signals",
                        "text": "Hydrological gauges, SAR satellite apertures, and field reports.",
                        "badge": "EVIDENCE",
                        "color": "text-emerald-400"
                    }
                ],
                key_signals=claim.audit_trail,
                underlying_claims=[claim.claim_id],
                underlying_evidence=claim.supporting_evidence,
                trust_score=claim.data_trust_score
            )

    def get_evidence_summary(self) -> EvidenceSummaryResponse:
        claims = self.engine.claims
        verified = sum(1 for c in claims if c.status == EvidenceStatus.VERIFIED)
        supported = sum(1 for c in claims if c.status == EvidenceStatus.SUPPORTED)
        unverified = sum(1 for c in claims if c.status == EvidenceStatus.UNVERIFIED)
        conflicting = sum(1 for c in claims if c.status == EvidenceStatus.CONFLICTING or c.status == EvidenceStatus.REJECTED)
        stale = sum(1 for c in claims if c.status == EvidenceStatus.STALE)

        trust_index, trust_breakdown = self.confidence_engine.calculate_system_trust_index(
            claims=claims,
            evidence_items=self.engine.evidence_items
        )

        return EvidenceSummaryResponse(
            total_claims_analyzed=42, # Realistic simulated aggregate count
            verified_count=26,
            supported_count=9,
            unverified_count=5,
            conflicting_count=conflicting,
            stale_count=stale,
            data_trust_index=trust_index,
            trust_breakdown=trust_breakdown,
            claims=claims
        )

evidence_service = EvidenceService()
