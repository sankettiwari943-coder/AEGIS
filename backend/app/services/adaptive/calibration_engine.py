import uuid
import datetime
from typing import Dict, List, Any, Optional
from app.services.adaptive.learning_store import learning_store
from app.services.adaptive.prediction_evaluator import prediction_evaluator

class CalibrationEngine:
    """
    Detects systematic prediction bias and calculates explainable model recalibration factors.
    Enforces minimum sample thresholds, recency weighting, maximum calibration caps, and generates audit logs.
    """
    def __init__(
        self,
        min_sample_count: int = 5,
        max_calibration_limit: float = 20.0,
        recent_weight: float = 0.8,
        older_weight: float = 0.4,
        min_confidence: float = 0.40,
        max_confidence: float = 0.95
    ):
        self.min_sample_count = min_sample_count
        self.max_calibration_limit = max_calibration_limit
        self.recent_weight = recent_weight
        self.older_weight = older_weight
        self.min_confidence = min_confidence
        self.max_confidence = max_confidence

    def compute_calibration_for_metric(self, metric: str) -> Dict[str, Any]:
        """
        Analyzes historical observations for a metric and computes statistical recalibration factors.
        """
        outcomes = learning_store.get_outcomes_for_metric(metric)
        sample_count = len(outcomes)
        
        # Friendly metric labels
        labels = {
            "road_accessibility": "Road Network Accessibility",
            "hospital_accessibility": "Hospital Trauma Ward Access",
            "predicted_isolation_time": "Sector Isolation Horizon (min)",
            "mission_eta": "Rescue Mission Travel Time (min)",
            "flood_risk": "Surface Flood Inundation Risk",
            "power_risk": "Substation Electrical Failure Risk",
            "cascade_risk": "Secondary Cascading Vulnerability"
        }
        label = labels.get(metric, metric.replace("_", " ").title())

        # Check minimum sample requirement
        if sample_count < self.min_sample_count:
            existing = learning_store.get_calibrations().get(metric, {})
            calib = {
                "metric": metric,
                "label": label,
                "sample_count": sample_count,
                "average_error": existing.get("average_error", 0.0),
                "bias": existing.get("bias", "INSUFFICIENT DATA"),
                "suggested_adjustment": 0.0,
                "applied_adjustment": 0.0,
                "status": "INSUFFICIENT_DATA",
                "confidence": existing.get("confidence", 0.75),
                "confidence_adjustment": 0.0,
                "last_updated": datetime.datetime.now().strftime("%H:%M:%S")
            }
            learning_store.update_calibration(metric, calib)
            return calib

        # Compute weighted error (recent vs older)
        # Outcomes are ordered newest first
        split_idx = max(1, sample_count // 3)
        recent_outcomes = outcomes[:split_idx]
        older_outcomes = outcomes[split_idx:]

        recent_err_sum = sum(o.get("error", 0.0) for o in recent_outcomes)
        older_err_sum = sum(o.get("error", 0.0) for o in older_outcomes)

        recent_avg = (recent_err_sum / len(recent_outcomes)) if recent_outcomes else 0.0
        older_avg = (older_err_sum / len(older_outcomes)) if older_outcomes else 0.0

        # Weighted bias
        weighted_bias = round(
            (recent_avg * self.recent_weight + older_avg * self.older_weight) / (self.recent_weight + self.older_weight),
            2
        )
        avg_err = round(sum(o.get("error", 0.0) for o in outcomes) / sample_count, 2)

        # Classify Bias direction
        if abs(weighted_bias) <= 3.0:
            bias_str = "BALANCED / STABLE"
            status = "STABLE"
            suggested_adj = 0.0
        elif weighted_bias < -3.0:
            bias_str = "UNDERPREDICTING" # actual was lower (e.g. road access collapsed faster)
            status = "RECALIBRATION_RECOMMENDED"
            suggested_adj = weighted_bias
        else:
            bias_str = "OVERPREDICTING" # actual was higher than predicted
            status = "RECALIBRATION_RECOMMENDED"
            suggested_adj = weighted_bias

        # Apply calibration limits (Max cap ±20)
        limit_reached = False
        applied_adj = suggested_adj
        if abs(suggested_adj) > self.max_calibration_limit:
            applied_adj = self.max_calibration_limit if suggested_adj > 0 else -self.max_calibration_limit
            status = "LIMIT_REACHED"
            limit_reached = True

        # Confidence adjustment calculation
        # High accuracy increases confidence, high unmitigated error reduces confidence
        eval_stats = prediction_evaluator.evaluate_outcomes(outcomes)
        acc_pct = eval_stats["accuracy_percent"]
        
        # Base confidence from accuracy: 80% acc -> ~0.82 confidence
        raw_conf = min(self.max_confidence, max(self.min_confidence, (acc_pct / 100.0) * 0.95))
        conf_adj = round(raw_conf - 0.80, 2)

        now_str = datetime.datetime.now().strftime("%H:%M:%S")

        calib_dict = {
            "metric": metric,
            "label": label,
            "sample_count": sample_count,
            "average_error": avg_err,
            "bias": bias_str,
            "suggested_adjustment": suggested_adj,
            "applied_adjustment": round(applied_adj, 1),
            "status": status,
            "confidence": round(raw_conf, 2),
            "confidence_adjustment": conf_adj,
            "last_updated": now_str
        }

        # Log audit learning event if recalibration occurred
        existing = learning_store.get_calibrations().get(metric, {})
        old_val = existing.get("applied_adjustment", 0.0)
        if abs(applied_adj - old_val) > 0.5:
            reason = f"Systematic {bias_str.lower()} bias of {weighted_bias:+.1f} points detected across {sample_count} observations."
            if limit_reached:
                reason += f" (Capped at maximum safe adjustment limit of ±{self.max_calibration_limit} pts)."
            
            learning_store.add_learning_event({
                "id": f"EVT-{str(uuid.uuid4())[:8]}",
                "metric": metric,
                "event_type": "CALIBRATION_UPDATE",
                "old_value": old_val,
                "new_value": applied_adj,
                "reason": reason,
                "evidence_count": sample_count,
                "timestamp": now_str
            })

        learning_store.update_calibration(metric, calib_dict)
        return calib_dict

    def recalibrate_all(self) -> Dict[str, Dict[str, Any]]:
        """Recalibrates all active metrics."""
        metrics = ["road_accessibility", "hospital_accessibility", "predicted_isolation_time", "mission_eta", "flood_risk"]
        results = {}
        for m in metrics:
            results[m] = self.compute_calibration_for_metric(m)
        return results

calibration_engine = CalibrationEngine()
