from typing import Dict, Any, List
import math

class EscalationModel:
    """
    Escalation Threshold & Confidence Modeling Engine.
    Detects when a sector or infrastructure element will cross critical operational safety limits.
    """
    def __init__(self, critical_threshold: int = 90):
        self.critical_threshold = critical_threshold

    def calculate_escalation_time(
        self,
        current_risk: int,
        predicted_risk_30m: int,
        predicted_risk_60m: int,
        default_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Determines if and when the critical threshold will be breached using linear/polynomial projection.
        """
        if current_risk >= self.critical_threshold:
            return {
                "escalation_detected": True,
                "minutes_to_escalation": 0,
                "status": "CRITICAL_NOW"
            }

        if predicted_risk_60m < self.critical_threshold:
            return {
                "escalation_detected": False,
                "minutes_to_escalation": default_minutes,
                "status": "MONITORING"
            }

        # Calculate exact minute where trajectory crosses critical threshold
        # Interval 0 -> 30 min
        if predicted_risk_30m >= self.critical_threshold:
            slope = (predicted_risk_30m - current_risk) / 30.0
            needed = self.critical_threshold - current_risk
            minutes = max(5, int(needed / slope)) if slope > 0 else 15
        else:
            # Interval 30 -> 60 min
            slope = (predicted_risk_60m - predicted_risk_30m) / 30.0
            needed = self.critical_threshold - predicted_risk_30m
            minutes = max(31, int(30 + (needed / slope))) if slope > 0 else 45

        return {
            "escalation_detected": True,
            "minutes_to_escalation": minutes,
            "status": "IMMINENT_ESCALATION"
        }

    def compute_confidence_score(
        self,
        sensor_signals_count: int = 4,
        historical_consistency: float = 0.90, # 0.0 - 1.0
        conflicting_signals: int = 0
    ) -> int:
        """
        Calculates explainable model confidence percentage.
        """
        base_confidence = 75.0
        signal_bonus = min(15.0, sensor_signals_count * 3.5)
        consistency_bonus = historical_consistency * 10.0
        conflict_penalty = conflicting_signals * 8.0

        confidence = base_confidence + signal_bonus + consistency_bonus - conflict_penalty
        return min(96, max(50, int(confidence)))

escalation_model = EscalationModel()
