"""
Evidence Engine Compatibility Adapter
Wraps the modular evidence & truth service while maintaining backward compatibility.
"""
from typing import List, Optional
from app.models.schemas import EvidenceClaim
from app.services.evidence.evidence_service import evidence_service, EvidenceService

class EvidenceEngineAdapter:
    """
    Backward-compatible adapter for legacy EvidenceEngine callers.
    """
    def __init__(self):
        self.service = evidence_service
        self.claims = self._build_legacy_claims()

    def _build_legacy_claims(self) -> List[EvidenceClaim]:
        claims_assessments = self.service.get_all_claims()
        results = []
        for ca in claims_assessments:
            results.append(EvidenceClaim(
                claim_id=ca.claim_id,
                target_zone_id=ca.target_zone_id,
                title=ca.title,
                description=ca.claim_statement,
                citizen_reports_count=sum(1 for e in ca.supporting_evidence if e.type.value == "CITIZEN_REPORT"),
                satellite_synthetic_score=88 if any(e.type.value == "SATELLITE_OBSERVATION" for e in ca.supporting_evidence) else 20,
                telemetry_sensor_confirmed=any(e.type.value == "SENSOR" for e in ca.supporting_evidence),
                contradicting_reports_count=ca.conflicting_sources_count,
                ai_confidence_percent=ca.ai_confidence_percent,
                status=ca.status.value,
                evidence_chain=ca.audit_trail
            ))
        return results

    def get_claims(self, zone_id: Optional[str] = None) -> List[EvidenceClaim]:
        if zone_id:
            return [c for c in self.claims if c.target_zone_id == zone_id]
        return self.claims

evidence_engine = EvidenceEngineAdapter()
