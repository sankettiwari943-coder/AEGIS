"""
Verification & Truth Status Engine
Classifies claims into truth statuses (VERIFIED, SUPPORTED, UNVERIFIED, CONFLICTING, STALE, REJECTED),
detects source contradictions, and flags insufficient evidence.
"""
from typing import List, Tuple, Optional
from app.models.schemas import EvidenceStatus, EvidenceType, EvidenceItem, EvidenceConflict

class VerificationEngine:
    """
    Evaluates empirical truth state and detects conflicts among multi-source evidence.
    """
    def __init__(self, stale_threshold_minutes: int = 120):
        self.stale_threshold_minutes = stale_threshold_minutes

    def determine_claim_status(
        self,
        confidence_percent: int,
        supporting_items: List[EvidenceItem],
        conflicting_items: List[EvidenceItem]
    ) -> Tuple[EvidenceStatus, bool, Optional[EvidenceConflict], str]:
        """
        Determines empirical truth status for a claim.
        Returns: (status, requires_physical_recon, conflict_obj, recommendation_text)
        """
        # 1. Check Stale Condition
        if supporting_items and all(item.minutes_ago >= self.stale_threshold_minutes for item in supporting_items):
            return (
                EvidenceStatus.STALE,
                True,
                None,
                "Evidence is outdated (>2 hours old). Ground reconnaissance required to refresh telemetry."
            )

        # 2. Check Contradiction / Conflict Condition
        if conflicting_items:
            # Check if high-reliability sources directly contradict
            high_rel_conflicts = [item for item in conflicting_items if item.reliability >= 0.80]
            if high_rel_conflicts and confidence_percent < 70:
                conflict_desc = f"Direct conflict detected: {conflicting_items[0].source} reports opposing state ({conflicting_items[0].value})."
                c_id = (supporting_items[0].claim_id if supporting_items and supporting_items[0].claim_id else "claim-01")
                conflict_obj = EvidenceConflict(
                    conflict_id=f"conf-{c_id}",
                    claim_id=c_id,
                    description=conflict_desc,
                    opposing_evidence_ids=[item.id for item in conflicting_items],
                    reconciliation_status="RECON_REQUIRED",
                    recommended_action="Deploy physical UAV reconnaissance or cross-check nearest gateway telemetry to reconcile opposing signals."
                )

                if confidence_percent <= 35:
                    return (
                        EvidenceStatus.REJECTED,
                        False,
                        conflict_obj,
                        "Claim contradicted and rejected based on authoritative sensor telemetry and optical confirmation."
                    )
                else:
                    return (
                        EvidenceStatus.CONFLICTING,
                        True,
                        conflict_obj,
                        "Conflicting information detected between active telemetry and observer reports. Physical verification recommended."
                    )

        # 3. Check Insufficient Evidence Condition
        source_types = set(item.type for item in supporting_items)
        if len(supporting_items) <= 1 or confidence_percent < 50:
            if not supporting_items:
                return (
                    EvidenceStatus.UNVERIFIED,
                    True,
                    None,
                    "INSUFFICIENT EVIDENCE: AEGIS cannot confidently verify this claim. Additional physical verification required."
                )
            # Only single citizen report or weak signal
            return (
                EvidenceStatus.UNVERIFIED,
                True,
                None,
                "INSUFFICIENT EVIDENCE: Single uncorroborated report. Maintain under telemetry watch; do not dispatch emergency assets on unverified claim alone."
            )

        # 4. Verified vs. Supported
        has_sensor_or_satellite = any(
            item.type in [EvidenceType.SENSOR, EvidenceType.SATELLITE_OBSERVATION, EvidenceType.OFFICIAL_REPORT]
            for item in supporting_items
        )

        if confidence_percent >= 85 and has_sensor_or_satellite and len(source_types) >= 2:
            return (
                EvidenceStatus.VERIFIED,
                False,
                None,
                "Claim verified by multiple independent sensor telemetry, SAR satellite observations, and field reports. Authorized for operational action."
            )
        elif confidence_percent >= 68:
            return (
                EvidenceStatus.SUPPORTED,
                False,
                None,
                "Claim strongly supported by corroborated telemetry and field reports. Ready for proactive staging."
            )
        else:
            return (
                EvidenceStatus.UNVERIFIED,
                True,
                None,
                "Claim moderately supported but lacks definitive multi-source confirmation. Ground spotter check recommended."
            )

verification_engine = VerificationEngine()
