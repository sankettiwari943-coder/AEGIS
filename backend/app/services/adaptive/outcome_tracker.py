import datetime
from typing import Dict, Any, Optional
from app.services.adaptive.learning_store import learning_store
from app.services.adaptive.prediction_evaluator import prediction_evaluator
from app.services.adaptive.calibration_engine import calibration_engine

class OutcomeTracker:
    """
    Tracks and records real/simulated operational outcomes against predictive models.
    """
    def __init__(self):
        pass

    def record_outcome(
        self,
        metric: str,
        predicted_value: float,
        actual_value: float,
        zone_id: Optional[str] = "zone-7",
        zone_name: Optional[str] = "Zone 7 — River Bend",
        prediction_id: Optional[str] = None,
        source: str = "Operator Observation",
        notes: Optional[str] = None,
        prediction_time: Optional[str] = None,
        observation_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates error, classifies outcome, stores it, and triggers metric recalibration.
        """
        all_outcomes = learning_store.get_all_outcomes()
        next_num = len(all_outcomes) + 1
        outcome_id = f"OUT-{next_num:03d}"

        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        obs_time = observation_time or now_time
        pred_time = prediction_time or now_time

        error = prediction_evaluator.calculate_error(predicted_value, actual_value)
        abs_err = prediction_evaluator.calculate_absolute_error(predicted_value, actual_value)
        rel_err = prediction_evaluator.calculate_relative_error_pct(predicted_value, actual_value)
        status = prediction_evaluator.classify_status(predicted_value, actual_value)

        # Look up current metric confidence
        calibs = learning_store.get_calibrations()
        conf = calibs.get(metric, {}).get("confidence", 0.82)

        outcome_dict = {
            "id": outcome_id,
            "prediction_id": prediction_id or f"PRED-{next_num:03d}",
            "zone_id": zone_id,
            "zone_name": zone_name,
            "metric": metric,
            "predicted_value": predicted_value,
            "actual_value": actual_value,
            "prediction_time": pred_time,
            "observation_time": obs_time,
            "error": error,
            "absolute_error": abs_err,
            "relative_error_pct": rel_err,
            "status": status,
            "source": source,
            "confidence": conf,
            "notes": notes or f"Evaluated via {source}."
        }

        # Store outcome
        learning_store.add_outcome(outcome_dict)

        # Automatically recompute calibration for this metric
        calibration_engine.compute_calibration_for_metric(metric)

        return outcome_dict

outcome_tracker = OutcomeTracker()
