"""
Confidence Engine
Calculates explainable multi-source AI/Evidence Confidence scores with source reliability weighting,
exponential recency decay, cross-corroboration amplification, and conflict penalties.
"""
from typing import List, Dict, Any, Tuple
import math
from app.models.schemas import EvidenceType, EvidenceItem

# Configurable prototype reliability weights by source type
DEFAULT_SOURCE_RELIABILITY: Dict[EvidenceType, float] = {
    EvidenceType.OFFICIAL_REPORT: 0.95,
    EvidenceType.SENSOR: 0.90,
    EvidenceType.SATELLITE_OBSERVATION: 0.88,
    EvidenceType.INFRASTRUCTURE_STATUS: 0.85,
    EvidenceType.COMMUNICATION_SIGNAL: 0.85,
    EvidenceType.MODEL_OUTPUT: 0.75,
    EvidenceType.CITIZEN_REPORT: 0.70,
    EvidenceType.HISTORICAL_DATA: 0.65
}

class ConfidenceEngine:
    """
    Computes explainable confidence metrics for claims and recommendations.
    All scores represent AI / Evidence Confidence estimates strictly bounded between 0 and 100.
    """
    def __init__(
        self,
        reliability_weights: Dict[EvidenceType, float] = None,
        recency_half_life_minutes: float = 45.0,
        stale_threshold_minutes: int = 120
    ):
        self.reliability_weights = reliability_weights or DEFAULT_SOURCE_RELIABILITY
        self.recency_half_life_minutes = recency_half_life_minutes
        self.stale_threshold_minutes = stale_threshold_minutes

    def get_source_reliability(self, evidence_type: EvidenceType) -> float:
        return self.reliability_weights.get(evidence_type, 0.75)

    def calculate_recency_factor(self, minutes_ago: int) -> float:
        """
        Exponential recency decay function: exp(-ln(2) * t / half_life).
        Recent evidence maintains factor ~ 1.0, decaying gradually over time.
        """
        if minutes_ago <= 0:
            return 1.0
        decay_constant = math.log(2) / self.recency_half_life_minutes
        return float(math.exp(-decay_constant * minutes_ago))

    def evaluate_claim_confidence(
        self,
        supporting_items: List[EvidenceItem],
        conflicting_items: List[EvidenceItem]
    ) -> Tuple[int, int, int, int]:
        """
        Calculates explainable confidence for a claim.
        Returns: (confidence_pct, recency_score, consistency_score, data_trust_score)
        """
        if not supporting_items and not conflicting_items:
            return 0, 0, 0, 0

        # 1. Base Supporting Score
        # Accumulate weighted reliability of supporting sources with diminishing returns
        supporting_score = 0.0
        total_recency = 0.0

        for item in supporting_items:
            rel = item.reliability or self.get_source_reliability(item.type)
            rec = self.calculate_recency_factor(item.minutes_ago)
            total_recency += rec
            # Diminishing marginal utility of additional signals
            supporting_score += rel * rec * (0.85 ** (len(supporting_items) - 1) if len(supporting_items) > 5 else 1.0)

        avg_recency = total_recency / len(supporting_items) if supporting_items else 0.5
        recency_score = int(max(10, min(100, round(avg_recency * 100))))

        # Corroboration boost if multiple distinct source types corroborate
        source_types = set(item.type for item in supporting_items)
        corroboration_multiplier = 1.0 + min(0.35, (len(source_types) - 1) * 0.10)
        
        raw_confidence = (min(100.0, supporting_score * 32.0)) * corroboration_multiplier

        # 2. Contradiction / Conflict Penalty
        conflict_penalty = 0.0
        for conflict_item in conflicting_items:
            c_rel = conflict_item.reliability or self.get_source_reliability(conflict_item.type)
            c_rec = self.calculate_recency_factor(conflict_item.minutes_ago)
            conflict_penalty += (c_rel * c_rec * 35.0)

        # Consistency score (100 minus conflict intensity)
        consistency_score = int(max(10, min(100, round(100.0 - (conflict_penalty * 1.5)))))

        # Net AI Confidence Score
        net_confidence = raw_confidence - conflict_penalty
        final_confidence = int(max(0, min(100, round(net_confidence))))

        # If supporting signals are insufficient (e.g. only 1 weak uncorroborated report)
        if len(supporting_items) == 1 and supporting_items[0].type == EvidenceType.CITIZEN_REPORT and len(source_types) == 1:
            final_confidence = min(final_confidence, 48)

        # Data Trust Score for this claim
        data_trust = int(round(final_confidence * 0.5 + recency_score * 0.25 + consistency_score * 0.25))

        return final_confidence, recency_score, consistency_score, data_trust

    def calculate_system_trust_index(
        self,
        claims: List[Any],
        evidence_items: List[EvidenceItem]
    ) -> Tuple[int, Dict[str, int]]:
        """
        Calculates the aggregate Data Trust Index (0-100) across all evidence streams.
        """
        if not evidence_items:
            return 82, {
                "source_reliability": 88,
                "recency": 85,
                "consistency": 82,
                "coverage": 80,
                "conflict_level": 15
            }

        # 1. Source Reliability Index
        avg_reliability = sum(item.reliability for item in evidence_items) / len(evidence_items)
        source_rel_score = int(round(avg_reliability * 100))

        # 2. Recency Index
        avg_rec = sum(self.calculate_recency_factor(item.minutes_ago) for item in evidence_items) / len(evidence_items)
        recency_score = int(round(avg_rec * 100))

        # 3. Conflict Index
        conflict_count = sum(1 for item in evidence_items if item.is_contradicting)
        conflict_ratio = conflict_count / len(evidence_items) if evidence_items else 0.0
        conflict_score = int(round(conflict_ratio * 100))
        consistency_score = max(10, 100 - int(round(conflict_ratio * 250)))

        # 4. Sensor Coverage Index
        coverage_score = 86

        # Overall composite Data Trust Index
        trust_index = int(round(
            source_rel_score * 0.35 +
            recency_score * 0.25 +
            consistency_score * 0.25 +
            coverage_score * 0.15
        ))

        breakdown = {
            "source_reliability": source_rel_score,
            "recency": recency_score,
            "consistency": consistency_score,
            "coverage": coverage_score,
            "conflict_level": conflict_score
        }

        return trust_index, breakdown

confidence_engine = ConfidenceEngine()
